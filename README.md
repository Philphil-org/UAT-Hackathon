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
</p>

---

## 🧭 Philosophy: "The Invisible Peripheral"

ZeroTouch rejects distracting, neon "cyber/hacker" gimmicks in favor of an **executive, precision-engineered instrument**. It runs quietly in the background as a zero-footprint companion, surfacing visually and acoustically *only* when deliberate spatial intent is mathematically verified.

* **100% Local Inferencing:** Zero video frames are written to disk or transmitted across a network. All computer vision models execute in volatile memory (RAM).
* **Zero Accidental Triggers:** Multimodal verification (typing detection, body-ownership binding, anti-jitter bone geometry) ensures the system never misinterprets everyday casual hand movements or object holding.

---

## ✨ Core Spatial Gesture Suite

| Gesture | Physical Action | System Output | Feedback |
| :--- | :--- | :--- | :--- |
| **Play / Pause** | Hold an open palm facing forward for 0.5s | `Media Play / Pause` | Circular wrist ring, warm dual-tone chime |
| **Track Skip / Slide Advance** | Show the **back of your hand** and swipe **Right** | `Next Track / Next Slide` | Dynamic horizontal rail, crisp upward flick sound |
| **Track Prev / Slide Return** | Show the **back of your hand** and swipe **Left** | `Previous Track / Previous Slide` | Dynamic horizontal rail, crisp downward flick sound |
| **Dynamic Volume Slider** | Form an "L-shape" (Thumb + Index) and pinch vertically | `Volume Up / Volume Down` | Magenta pinch rail, live floating capsule updates |
| **Boss Key (Instant Mute)** | Bring index finger over mouth ("Shush" gesture) | `Toggle Audio Mute` | Red lip beacon, soft dampened drop sound |

---

## 🛡️ Privacy & Computer Vision Intelligence

### 1. ShoulderGuard™ (Intruder Screen Shield)
An ultra-lightweight `BlazeFace` detector continuously scans the user's workspace. If a second person looks over your shoulder (shoulder surfing), ZeroTouch automatically fires `Win + D` to minimize all desktop windows and suspends gesture control until the intruder leaves.

### 2. Body Ownership Lock-On
To prevent background bystanders or passersby from hijacking your computer, ZeroTouch calculates the 3D Euclidean distance between detected hands and the primary user's face center. Hands outside the user's personal reach envelope are rejected.

### 3. Anti-Hallucination Physics Engine
When holding a phone, pen, or mug, standard vision models often hallucinate overlapping finger joints. ZeroTouch monitors frame-to-frame palm height stability, fingertip acceleration, and knuckle aspect ratios. Hallucinated joints are instantly frozen to prevent false inputs.

### 4. Smart Typing Lockout
A low-level background hardware listener monitors physical keyboard keystrokes. While you are typing or resting your hands above the keyboard, gesture recognition gracefully sleeps for 2.0 seconds.

---

## 🎨 Ambient UI & Sound Design

* **The Companion Widget:** A compact 350x520 dark-mode dashboard styled in *Midnight Ink (`#0F0F14`)* and *Champagne Gold (`#D4AF6A`)*. Configure camera hardware, toggle debug feeds, or adjust security modules live without restarting.
* **System Tray Minimization:** Clicking the close button (`X`) or "Minimize to Tray" tucks the app into your Windows system tray with a custom gold emblem. Restores with a single click.
* **The Floating Capsule:** A sleek, micro-pill head-up display that drops down from the top-center of your monitor for 1.2s to confirm commands using crisp Unicode glyphs (`⏯`, `⏭`, `⏮`, `🔇`, `🛡️`).
* **Bespoke Haptic Audio:** Synthesized acoustic waveforms for tactile confirmation without noisy, generic OS error dings.

---

## 🚀 1-Click Setup & Launch (Windows)

### Option A: 1-Click Batch Launcher (Recommended)
1. Clone the repository:
   ```powershell
   git clone https://github.com/Philphil-org/UAT-Hackathon.git
   cd UAT-Hackathon
   ```
2. Double-click **`Start_Aero.bat`**.
   * Automatically sets up an isolated Python virtual environment.
   * Silently installs all required AI models and dependencies.
   * Boots the companion widget.

### Option B: Manual Setup
```powershell
# Create and activate environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run the companion widget
python launcher.py

# Or run the core vision daemon directly
python main.py
```

---

## 📦 Architecture & Technologies

* **Core Runtime:** Python 3.11+
* **Vision Pipeline:** MediaPipe Tasks API (`HandLandmarker`, `BlazeFace Short-Range`)
* **Frame Processing:** OpenCV (`cv2`) with real-time HUD vector rendering
* **OS Hooking & Keystroke Injection:** PyAutoGUI, Pynput
* **Interface:** CustomTkinter, Pystray, Pillow (PIL)
* **Audio Engine:** Native asynchronous Windows Sound API (`winsound`) with synthesized wave assets

---

<p align="center">
  <i>ZeroTouch OS — Built with precision for the 2026 UAT Computer Vision Hackathon.</i>
</p>
