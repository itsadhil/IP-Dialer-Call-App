# IP-Dialer-Call-App
This project is a Python-based IP dialer for making real-time audio calls over a local network using socket communication. It provides an interface to dial an IP address, manage recent calls, and handle audio transmission. The app allows users to record calls and view their recent call history. The project is built with Tkinter for the GUI and PyAudio for audio handling.

# Features
- Dial IP: Dial a specific IP address and port for making audio calls.
- Incoming Calls: Automatically listen for incoming calls and handle them.
- Call Controls: Mute, record, and hang up calls.
- Recent Calls: View a list of recent outgoing and incoming calls.
- Call Recording: Record ongoing calls and save them as .wav files.
- Full Duplex Audio: Send and receive audio in real-time over a TCP socket.
- Checksum Verification: Ensures data integrity during audio transmission by verifying checksums.

# Technologies Used
- Python: Main programming language.
- Tkinter: For GUI elements (dial pad, call controls, etc.).
- Socket: For TCP communication between caller and receiver.
- PyAudio: For handling real-time audio input/output.
- Wave: For saving recorded audio as .wav files.
- Threading: For handling concurrent audio sending and receiving.

# Getting Started

**Prerequisites**

- Python 3.x
- Tkinter (usually included with Python)
- PyAudio: Install via

```bash
pip install pyaudio
```

# Installation

1.  **Clone this repository or download the source code.**

    ```bash
    git clone https://github.com/itsadhil/ip-dialer-call-app.git
    cd ip-dialer-call-app

3.  **Install dependencies:**

    ```bash
    pip install pyaudio

# Running the Application

**To run the app, execute the following command:**
```bash
python call_app.py
```

# Audio Devices

The application automatically lists available audio devices in the console, including default input and output devices. The user can check the console for details on input/output channels.

# Usage

**Dialing an IP**
- Open the app.
- Click on the Dial IP button.
- Enter the IP address and port of the receiving end (default port is 5000).
- Once connected, audio will start transmitting in real-time.

**Incoming Calls**

The app listens for incoming calls on port 5000 by default. When a call is received, you’ll be prompted to accept it.

**Call Recording**
- During a call, press the Record button to start recording.
- Press Stop Recording to end the recording. The recording will be saved as call_recording.wav.

**Recent Calls**
- View recent calls by clicking the Recent Calls button.
- View recent calls by clicking the Recent Calls button.

**Hang Up**
Click the Hang Up button to terminate the call.

**Call Flow**
- Dial or Accept: Initiate or accept a call.
- Audio Stream: Audio is sent and received over a TCP connection.
- Checksum Validation: Audio packets are validated using a SHA-256 checksum.
- Real-time Audio: Audio is transmitted and played in real-time.
- Hang Up: End the call and close the connection.

# Configuration
- Default Port: The default port is 5000. You can change this in the code if needed.
 ```bash
 self.port = 5000  # Default port
 ```
**Audio Format:**
- Format: pyaudio.paInt16
- Channels: 1 (Mono)
- Sample Rate: 16 kHz
- Chunk Size: 1024
You can adjust these parameters to change the audio quality and performance.

# Known Issues
- High Latency: Lowering the sample rate and increasing chunk size helps reduce latency, but the application may experience slight delays due to network conditions.
- Checksum Mismatch: If data integrity is compromised, the audio may not play back correctly, and the app will discard the compromised packets.

# Future Enhancements
- Implement Mute functionality.
- Add Secure Communication (e.g., encryption).
- Allow the user to configure audio devices from the app's GUI.

# Contribution

Contribution is appreciated.
Contact Me on Discord Through @hayayaquazi


