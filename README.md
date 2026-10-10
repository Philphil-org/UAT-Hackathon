# Aero: The Zero-Touch OS

Aero is a background vision engine that brings spatial, zero-touch gesture controls to any Windows PC. Built in 48 hours for the UAT "Computer Vision: See / Analyze / Build" Hackathon.

Aero allows you to control your media, volume, and system privacy entirely hands-free using your webcam and advanced physics-based structural hand tracking.

## ✨ Features

- **Media Control (Play/Pause):** Hold up an open palm for 0.5s to play or pause your media.
- **Air Taps (Next/Prev Track):** Double-tap your middle finger to your thumb to skip tracks, or your ring finger for previous tracks.
- **Volume Slider (Pinch):** Make an "L" shape with your hand and pinch to dynamically slide your system volume up and down.
- **ShoulderGuard (Privacy Shield):** Uses facial recognition to count the number of people looking at your screen. If someone shoulder-surfs you, Aero instantly triggers `Win + D` to hide your windows and locks gesture controls until they leave.
- **Body Ownership Lock-On:** Binds your hand to your face using geometric distance. If a background person waves their hand, Aero rejects it.
- **"Shush" Boss Key:** Bring your index finger to your lips to instantly mute your system volume.
- **Anti-Hallucination Physics Engine:** MediaPipe can hallucinate hands when holding objects like phones. Aero calculates the frame-to-frame change in palm bone length and finger teleportation speed to detect hallucinations and instantly pause inputs.
- **Smart Typing Lockout:** Background listener detects keyboard activity and suspends gesture recognition while you are typing.

## 🚀 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aero-vision.git
   cd aero-vision
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the engine:
   ```bash
   python main.py
   ```

## 🧠 Tech Stack

*   **Python 3.14**
*   **OpenCV (`cv2`)**: Real-time webcam feed rendering and HUD.
*   **MediaPipe Tasks API**: Accelerated `HandLandmarker` and `FaceDetector` models.
*   **PyAutoGUI**: OS-level key injection for media and system controls.
*   **Pynput**: Low-level background keyboard hooking for typing lockout.
