# ZeroTouch OS: The Ambient Spatial Companion

<p align="center">
  <b>An executive, zero-touch spatial vision engine bringing fluid, hands-free OS control to Windows.</b><br>
  <i>Built for the UAT "Computer Vision: See / Analyze / Build" Hackathon.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Computer%20Vision-MediaPipe%20Tasks-orange?style=flat-square" alt="MediaPipe">
  <img src="https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=flat-square" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Privacy-100%25%20Local%20RAM-success?style=flat-square" alt="Local Privacy">
  <img src="https://img.shields.io/badge/Platform-Windows%2011%20%2F%2010-0078D6?style=flat-square" alt="Windows 11">
</p>

---

## 🧭 Philosophy: "The Invisible Peripheral"

ZeroTouch rejects distracting, neon "cyber/hacker" gimmicks in favor of an **executive, precision-engineered instrument**. It runs quietly in the background as a zero-footprint companion, surfacing visually and acoustically *only* when deliberate spatial intent is mathematically verified.

* **100% Local Inferencing:** Zero video frames are written to disk or transmitted across a network. All computer vision models execute in volatile memory (RAM).
* **Zero Accidental Triggers:** Multimodal verification (typing detection, body-ownership binding, anti-jitter bone geometry, gaze tracking) ensures the system never misinterprets casual everyday hand movements or resting positions.
* **Context-Aware Spatial OS Integration:** ZeroTouch actively inspects foreground Windows applications to dynamically remap gestures to whatever you are doing—slides, video meetings, or multimedia.

---

## 🎯 Context-Aware Spatial Control Modes

ZeroTouch automatically morphs its gesture behaviors depending on your active foreground application:

| Context | Target Applications | Gestures & Actions | Visual Feedback |
| :--- | :--- | :--- | :--- |
| **📊 Presentation Mode** | PowerPoint, Google Slides, Keynote, Acrobat PDF | • **Swipe Right:** `▶ SLIDE NEXT`<br>• **Swipe Left:** `◀ SLIDE PREV`<br>• **Palm Hold (0.5s):** `⬛ BLANK / RESUME SLIDES` (`B`) | Wide Floating Capsule with full phrase confirmation |
| **🎥 Meeting Mode** | Zoom, Microsoft Teams, Google Meet, Webex | • **Palm Hold (0.5s):** `📹 CAM TOGGLE` (`Alt + V`)<br>• **Swipe Right / Left:** `👥 NEXT / PREV VIEW`<br>• **"Shh" Gesture:** `🎙️ / 🔇 MUTE MICROPHONE` | Micro-pill glyphs & hardware CoreAudio feedback |
| **🎵 Media / Default** | Spotify, YouTube, Netflix, VLC, System | • **Palm Hold (0.5s):** `⏯ PLAY / PAUSE`<br>• **Swipe Right / Left:** `⏭ / ⏮ TRACK NEXT / PREV`<br>• **Vertical Pinch:** `🔊 DYNAMIC VOLUME SLIDER` | Animated wrist loading arc & dynamic HUD rails |

---

## ✨ Core Spatial Gesture Suite

| Gesture | Physical Action | System Output | Feedback |
| :--- | :--- | :--- | :--- |
| **Open Palm Hold** | Hold an open palm facing forward for 0.5s | `Play/Pause` or `Slide Blank` or `Meeting Cam` | Circular wrist ring, warm dual-tone chime |
| **Back-of-Hand Swipe** | Show the **back of your hand** and swipe **Left / Right** | `Next Track / Slide` or `Prev Track / Slide` | Dynamic horizontal rail, crisp directional chimes |
| **Dynamic Volume Slider** | Form an "L-shape" (Thumb + Index) and slide vertically | `System Master Volume Up / Down` | Magenta pinch rail, live floating capsule updates |
| **Ghost-Mute (Boss Key)** | Bring index finger over mouth ("Shush" gesture) | `Toggle Windows Hardware Microphone Mute` | Red lip beacon, soft dampened audio drop sound |

---

## 🛡️ Privacy & Computer Vision Intelligence

### 1. Stage / Distance Mode (Presentation Stage Range)
Standard webcams struggle when users step 6–10 feet back onto a stage. ZeroTouch dynamically calculates distance via facial width ratio (`fw / w`). In Stage Mode:
* Focus/Gaze lockout is safely bypassed to eliminate distance false positives.
* Arm reach boundaries dynamically expand up to **6.0x face width**, allowing expressive stage gesturing.
* Grace periods extend so presenters can freely glance at slides or the audience without losing control.

### 2. Multi-App Camera Sharing (Google Meet / Zoom / OBS Compatibility)
ZeroTouch leverages the native **Windows Camera Frame Server** (`svchost.exe -k Camera`) and Windows 11 Multi-App streaming.
* Includes a 1-click **"⚙ Camera Sharing Setup"** button in the dashboard leading directly to Windows camera settings.
* Built-in walkthrough guidance walks users through toggling *"Allow multiple apps to use camera at the same time"*.
* ZeroTouch and Google Meet / Zoom / OBS can now run on the same physical webcam simultaneously with zero driver lockups.

### 3. Gaze-Clutch™ (Look-to-Control Focus Lock)
Tracks 3D head yaw and pupillary distance in real time. If you turn your head to look away from your display, gesture recognition automatically clutches to standby, preventing background false triggers.

### 4. ShoulderGuard™ (Intruder Screen Shield)
An ultra-lightweight `BlazeFace` detector continuously scans your workspace. If a second person peers over your shoulder (shoulder surfing), ZeroTouch automatically fires `Win + D` to minimize all windows and locks down controls until privacy is restored.

### 5. Body Ownership Lock-On
To prevent bystanders or passersby from hijacking your computer, ZeroTouch calculates the 3D Euclidean distance between detected hands and the primary face center. Hands outside your personal reach radius are rejected.

### 6. Anti-Hallucination Physics Engine
Monitors frame-to-frame palm height stability, fingertip acceleration, and knuckle aspect ratios. Hallucinated joints caused by holding a phone, pen, or mug are instantly frozen.

### 7. Smart Activity Lockout
A background hardware listener monitors physical keyboard keystrokes and mouse clicks (`pynput`). While typing or clicking, gesture recognition sleeps to eliminate interference.

---

## 🎨 Ambient UI & Sound Design

* **The Companion Widget:** A dark-mode dashboard styled in *Midnight Ink (`#0F0F14`)* and *Champagne Gold (`#D4AF6A`)*. Features an embedded low-latency shared-memory vision preview, live FPS and luminance telemetry, and toggles for all modules.
* **System Tray Minimization:** Minimizes cleanly to the Windows system tray with a custom gold emblem. Restores with a single click.
* **The Floating Capsule:** A sleek head-up micro-pill that drops down from top-center to confirm commands using crisp Unicode glyphs (`⏯`, `▶ SLIDE NEXT`, `🔇`, `🛡️`).
* **Bespoke Haptic Audio:** Synthesized acoustic waveforms for tactile confirmation without noisy, generic OS error dings.

---

## 📽️ Hackathon Pitch Deck (4-Minute Presentation)

The official executive presentation deck is included directly in the repository:
* **Presentation File:** [`ZeroTouch_PitchDeck.pptx`](ZeroTouch_PitchDeck.pptx)
* **How to Access & View from GitHub:**
  1. Click on [`ZeroTouch_PitchDeck.pptx`](ZeroTouch_PitchDeck.pptx) in this repository.
  2. Click the **Download raw file** button (or clone the repository).
  3. Open with Microsoft PowerPoint, Google Slides, or Apple Keynote.
  4. Press **F5** to start presentation mode. ZeroTouch automatically detects the presentation window so you can navigate slides using back-of-hand spatial swipes!

---

## 🚀 1-Click Launch & Setup Guide (For Judges & Presenters)

ZeroTouch is designed to boot smoothly on **any Windows machine**—even locked-down conference room computers with disabled PowerShell policies or custom editor file associations.

### 🌟 Option 1: 1-Click Zero-Console Launch (Recommended)
1. Download or clone this repository:
   * **Direct ZIP Download:** Click green **`<> Code`** at the top right → **`Download ZIP`** → Extract the folder.
   * **Or via Git:** `git clone https://github.com/Philphil-org/UAT-Hackathon.git`
2. Double-click **`ZeroTouch.vbs`** (or **`Start_Aero.bat`**):
   * **`ZeroTouch.vbs`** runs natively via Windows Script Host (`wscript.exe`), booting the app **with zero lingering terminal windows** and completely bypassing any text editors (like VS Code or Notepad).
   * First run will automatically build the isolated virtual environment (`venv`) and install all required models silently.
   * Subsequent runs launch instantly into the executive dark-gold dashboard.

### 💻 Option 2: Standard Command Prompt (`cmd.exe`)
If you prefer running via the standard Windows terminal:
```cmd
:: 1. Navigate into the project folder
cd UAT-Hackathon

:: 2. Run the automated launcher
Start_Aero.bat
```
*(Or manual step-by-step:*
```cmd
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python launcher.py
```*)*

---

## 🎮 60-Second Quick Demo Guide for Judges

Once the dashboard appears:
1. Click **`▶ START ENGINE`** (you'll see the embedded camera feed and live FPS/Luminance telemetry).
2. **Test Smart Activity Pause:** Type random keys on your keyboard → notice the telemetry pill shows **`SMART PAUSE (TYPING)`**, proving the system rejects accidental movement while working.
3. **Test Presentation Mode:** Open [`ZeroTouch_PitchDeck.pptx`](ZeroTouch_PitchDeck.pptx) in PowerPoint and press **F5**. Show the back of your hand to the camera and swipe **Right** to advance to the next slide!
4. **Test Ghost-Mute:** Bring your index finger to your lips ("Shh" gesture) → notice your Windows microphone mutes instantly with acoustic haptic confirmation.
5. **Test Gaze-Clutch™:** Look away at another monitor or person → notice the HUD immediately clutches to standby (`GAZE: AWAY`), preventing accidental triggers.

---

## 📦 Architecture & Technologies

* **Core Runtime:** Python 3.11+
* **Vision Pipeline:** MediaPipe Tasks API (`HandLandmarker`, `BlazeFace Short-Range`)
* **Inter-Process Communication:** High-throughput `multiprocessing.shared_memory` for 30 FPS zero-copy dashboard streaming
* **Hardware Audio Hook:** Windows Core Audio (`pycaw`) hardware microphone endpoint control
* **Context Engine:** Windows API (`pywin32`) foreground window process inspection
* **Frame Processing:** OpenCV (`cv2`) with native Media Foundation (`CAP_MSMF`) Frame Server sharing
* **OS Hooking & Keystroke Injection:** PyAutoGUI, Pynput
* **Interface:** CustomTkinter, Pystray, Pillow (PIL)
* **Audio Engine:** Native asynchronous Windows Sound API (`winsound`) with synthesized wave assets

---

<p align="center">
  <i>ZeroTouch OS — Built with precision for the 2026 UAT Computer Vision Hackathon.</i>
</p>
