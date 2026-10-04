# 🖱️ AI Virtual Mouse Controller

> *Transform your web camera into an AI-powered touchless gesture interface using OpenCV, MediaPipe Tasks API, and PyAutoGUI.*

---

## 🌟 Overview

**AI Virtual Mouse Controller** is a high-performance computer vision tool built in Python. It translates real-time hand gestures into native operating system input commands—letting you control mouse navigation, clicking, and page scrolling hands-free. 

Powered by **MediaPipe 1.0+ Tasks Vision API**, this script accurately tracks 21 hand landmarks even in variable lighting conditions with minimal latency.

---

## ✨ Features

- 👆 **Precision Pointing:** Move the screen cursor using intuitive index finger positioning.
- 🤏 **Left Click:** Pinch your **Index Finger + Thumb**.
- 🔘 **Right Click:** Pinch your **Middle Finger + Thumb**.
- ⚡ **Double Click:** Pinch your **Ring Finger + Thumb**.
- 📜 **Dynamic Scrolling:** Join your **Index + Middle Fingers** together and move your hand up or down to scroll web pages and documents smoothly.
- 🎯 **Jitter Reduction:** Built-in exponential smoothing algorithms smooth out natural hand tremors.
- ⏱️ **Debounce Safety:** Cooldown logic prevents multiple accidental click triggers.

---

## 🎮 Gesture Mapping Guide

| Gesture | Visual Action | OS Command Triggered |
| :--- | :--- | :--- |
| **Point Index Finger** | Cursor follows fingertip | Cursor Movement |
| **Pinch Index + Thumb** | Green target circle | Left Mouse Click |
| **Pinch Middle + Thumb** | Red target circle | Right Mouse Click |
| **Pinch Ring + Thumb** | Purple target circle | Double Left Click |
| **Index + Middle Together** | "Mode: Scroll" overlay | Mouse Wheel Scroll Up/Down |

---

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.9 – 3.12+
- Built-in or external USB Webcam
- Active Virtual Environment (`venv` recommended)

### 1. Repository Setup

```bash
# Create project folder
mkdir VirtualMouse_OpenCV
cd VirtualMouse_OpenCV

# Initialize Python Virtual Environment
python -m venv venv

# Activate Virtual Environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install opencv-python mediapipe pyautogui numpy
```

### 3. Download Model Weights

Download the official MediaPipe Hand Landmarker model file into your root project directory:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "hand_landmarker.task"
```

**macOS / Linux (Bash):**
```bash
curl -O https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

---

## 📁 Directory Structure

```text
VirtualMouse_OpenCV/
│
├── hand_landmarker.task   # MediaPipe AI vision model file
├── virtual_mouse.py        # Core application script
├── venv/                  # Python isolated environment
└── README.md              # Project documentation
```

---

## 🏃 Running the Application

Ensure your virtual environment is active and run:

```bash
python virtual_mouse.py
```

*Press **`q`** while focused on the active camera feed window to terminate the application.*

---

## ⚙️ Configuration & Fine-Tuning

Inside `virtual_mouse.py`, you can tune the motion and responsiveness parameters:

```python
# Smoothing factor (Lower = faster response | Higher = smoother cursor trajectory)
smooth_factor = 4 

# Active bounding box margin (pixels from camera edges for screen boundary mapping)
frame_margin = 100 

# Cooldown delay in seconds between consecutive clicks
cooldown_delay = 0.4 
```

---

## 🛡️ Troubleshooting

- **Webcam Access Blocked:** Make sure VS Code or your terminal application has camera permissions enabled in your OS settings.
- **FailSafe Trigger:** PyAutoGUI has a safeguard if the cursor hits the extreme corners of the screen. This is disabled in the script via `pyautogui.FAILSAFE = False`.
- **Model File Error:** Confirm that `hand_landmarker.task` is located in the exact same directory as `virtual_mouse.py`.

---

## 📄 License

Distributed under the MIT License. Feel free to modify and expand!