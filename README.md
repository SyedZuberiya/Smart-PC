# Smart PC: Gesture & Voice Control 🚀🖐️🎙️

**Smart PC** is an AI-powered desktop assistant that uses hand gestures and voice commands to perform common tasks on your Windows PC. It provides an accessible and intuitive way to control your system—no mouse or keyboard required!

## 🔧 Features

- 👋 **Gesture-based Access Control** using hand recognition with MediaPipe
- 🎤 **Voice Commands** to open apps, control the desktop, and more
- 🔒 **Security Lockout** after multiple failed attempts
- 📸 Take Snapshots directly from the webcam
- 📁 Access essential Windows functions (Explorer, Notepad, Lock Screen, Restart, Shutdown, etc.)
- 🗣️ **Live Voice Captioning** for note-taking or accessibility


## 🛠 Tech Stack

- Python 3.x
- OpenCV
- MediaPipe
- pyttsx3 (Text-to-Speech)
- SpeechRecognition
- tkinter (GUI)
- PIL
- playsound
- pyautogui

## 🖥️ System Requirements

- Windows OS (tested on Windows 10/11)
- Webcam
- Microphone
- Python 3.8+
- Internet connection (for voice recognition)

## 🔌 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-pc-gesture-voice.git
   cd smart-pc-gesture-voice
**Project Structure**
smart-pc-gesture-voice/
├── assets/
│   └── alarm.mp3                 # Alarm sound file
│
├── snapshots/                    # Saved webcam snapshots
│   └── snapshot_*.png
│
├── src/
│   └── smart_pc.py               # Main application script
│   └── gesture_utils.py          # (Optional) Gesture recognition logic
│   └── voice_utils.py            # (Optional) Voice command & captioning
│   └── gui_components.py         # (Optional) Tkinter GUI components
│
├── README.md                     # Project overview and usage
├── requirements.txt              # Python dependencies
└── LICENSE                       # MIT or other license

**Author:**

Syeda Zuberiya
GitHub: github.com/SyedZuberiya
LinkedIn: linkedin.com/in/syed-riya
