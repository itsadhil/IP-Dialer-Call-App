import socket
import threading
import pyaudio
import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, Button, Label
import struct
import hashlib
import wave

class CallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Dialer Call App")
        self.recent_calls = []

        # Socket info
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.port = 5000  # Default port
        self.call_active = False
        self.connection = None
        self.client_socket = None
        self.server_socket = None

        # PyAudio setup
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Lower sample rate to reduce latency
        self.chunk_size = 1024  # Increase chunk size for better performance

        # Call Recording
        self.recording = False
        self.recorded_frames = []

        # Tabs for Dial and Recent Calls
        self.tabs = tk.Frame(self.root)
        self.tabs.pack(side="top", fill="x")

        self.dial_button = tk.Button(self.tabs, text="Dial IP", command=self.dial_ip)
        self.dial_button.pack(side="left")

        self.recent_button = tk.Button(self.tabs, text="Recent Calls", command=self.show_recent_calls)
        self.recent_button.pack(side="left")

        # Main frame for dynamic content
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.listbox = Listbox(self.main_frame)
        self.listbox.pack(fill="both", expand=True)

        # Call interface buttons
        self.call_status_label = Label(self.root, text="Call Status: Not in Call")
        self.call_status_label.pack(pady=5)

        self.hangup_button = Button(self.root, text="Hang Up", command=self.hang_up, state="disabled")
        self.hangup_button.pack(side="left", padx=5)

        self.mute_button = Button(self.root, text="Mute", command=self.toggle_mute, state="disabled")
        self.mute_button.pack(side="left", padx=5)

        self.record_button = Button(self.root, text="Record", command=self.toggle_record, state="disabled")
        self.record_button.pack(side="left", padx=5)

        # Start thread to listen for incoming calls
        threading.Thread(target=self.listen_for_calls, daemon=True).start()

        # Debug available audio devices
        self.list_audio_devices()

    def list_audio_devices(self):
        """ Print available audio devices for debugging """
        print("Listing available audio devices...\n")
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            print(f"Device {i}: {dev_info['name']}, Input Channels: {dev_info['maxInputChannels']}, Output Channels: {dev_info['maxOutputChannels']}")

        default_input = self.p.get_default_input_device_info()
        default_output = self.p.get_default_output_device_info()
        print(f"\nDefault Input Device: {default_input['name']}")
        print(f"Default Output Device: {default_output['name']}")

    def show_recent_calls(self):
        self.listbox.delete(0, tk.END)
        for call in self.recent_calls:
            self.listbox.insert(tk.END, call)

    def dial_ip(self):
        # Prompt user for IP address and port
        ip_address = simpledialog.askstring("Dial IP", "Enter IP Address:")
        port = simpledialog.askinteger("Dial Port", "Enter Port (default 5000):", initialvalue=5000)

        if ip_address and port:
            self.recent_calls.append(f"Called {ip_address}:{port}")
            self.make_call(ip_address, port)

    def make_call(self, ip_address, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
            self.client_socket.connect((ip_address, port))
            self.call_active = True

            # Enable call interface buttons
            self.hangup_button.config(state="normal")
            self.mute_button.config(state="normal")
            self.record_button.config(state="normal")
            self.call_status_label.config(text=f"In Call with {ip_address}:{port}")

            messagebox.showinfo("Calling", f"Calling {ip_address}:{port}...")

            # Start audio transmission in full duplex (send and receive audio)
            threading.Thread(target=self.handle_audio, args=(self.client_socket,), daemon=True).start()

        except Exception as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")
            messagebox.showerror("Connection Error", f"Error connecting to {ip_address}:{port}: {str(e)}")

    def listen_for_calls(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        self.server_socket.bind(('0.0.0.0', self.port))  # Bind to all interfaces
        self.server_socket.listen(1)  # Listen for incoming connections
        print(f"Listening for calls on {self.host_ip}:{self.port}")

        while True:
            try:
                conn, addr = self.server_socket.accept()
                if not self.call_active:
                    messagebox.showinfo("Incoming Call", f"Receiving call from {addr[0]}:{self.port}")
                    self.connection = conn
                    self.call_active = True
                    self.recent_calls.append(f"Received call from {addr[0]}")

                    # Update call status and enable buttons
                    self.hangup_button.config(state="normal")
                    self.mute_button.config(state="normal")
                    self.record_button.config(state="normal")
                    self.call_status_label.config(text=f"In Call with {addr[0]}")

                    threading.Thread(target=self.handle_audio, args=(conn,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_audio(self, sock):
        try:
            # Open audio stream for both input and output (full-duplex)
            stream = self.p.open(format=self.audio_format,
                                 channels=self.channels,
                                 rate=self.rate,
                                 input=True,
                                 output=True,
                                 frames_per_buffer=self.chunk_size)

            def send_audio():
                while self.call_active:
                    try:
                        # Capture audio from the microphone
                        data = stream.read(self.chunk_size, exception_on_overflow=False)
                        
                        # Generate checksum
                        checksum = hashlib.sha256(data).digest()

                        # Pack size, checksum, and data
                        packed_data = struct.pack('!I32s', len(data), checksum) + data

                        # Send the packed audio data
                        sock.sendall(packed_data)
                    except Exception as e:
                        print(f"Error sending audio: {e}")
                        break

            def receive_audio():
                while self.call_active:
                    try:
                        # Receive the size and checksum
                        header = sock.recv(36)
                        if len(header) < 36:
                            break

                        data_size, received_checksum = struct.unpack('!I32s', header)

                        # Receive the audio data
                        received_data = self.receive_exact(sock, data_size)

                        # Verify checksum
                        actual_checksum = hashlib.sha256(received_data).digest()
                        if actual_checksum != received_checksum:
                            print("Checksum mismatch! Data integrity compromised.")
                            continue

                        # Play the received audio data
                        stream.write(received_data)

                        # Record audio if recording is active
                        if self.recording:
                            self.recorded_frames.append(received_data)

                    except Exception as e:
                        print(f"Error receiving audio: {e}")
                        break

            # Start threads for sending and receiving audio
            send_thread = threading.Thread(target=send_audio, daemon=True)
            receive_thread = threading.Thread(target=receive_audio, daemon=True)
            send_thread.start()
            receive_thread.start()

            send_thread.join()
            receive_thread.join()

        except Exception as e:
            print(f"Error handling audio: {e}")

    def receive_exact(self, sock, size):
        """ Helper to receive exactly 'size' bytes from the socket """
        buf = b""
        while len(buf) < size:
            data = sock.recv(size - len(buf))
            if not data:
                return buf
            buf += data
        return buf

    def toggle_record(self):
        if not self.recording:
            self.recording = True
            self.recorded_frames = []
            self.record_button.config(text="Stop Recording")
            print("Recording started.")
        else:
            self.recording = False
            self.record_button.config(text="Record")
            print("Recording stopped. Saving to file...")

            # Save recorded frames to a .wav file
            filename = "call_recording.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.recorded_frames))
            wf.close()
            print(f"Recording saved as {filename}.")

    def hang_up(self):
        if self.connection:
            self.connection.close()
        if self.client_socket:
            self.client_socket.close()

        self.call_active = False
        self.call_status_label.config(text="Call Status: Not in Call")
        self.hangup_button.config(state="disabled")
        self.mute_button.config(state="disabled")
        self.record_button.config(state="disabled")
        print("Call ended.")

    def toggle_mute(self):
        # Handle muting if necessary
        pass

    def on_close(self):
        self.server_socket.close()
        self.p.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CallApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()