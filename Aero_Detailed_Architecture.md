# Aero (The Zero-Touch OS Pilot) - Detailed Architecture & Feature Outline

## 1. System Architecture Overview
Aero will run as a local Python desktop application sitting in the system tray. It relies on a modular architecture:
*   **Vision Engine:** Continuously captures webcam frames and processes them using MediaPipe (Hand & Face tracking).
*   **Logic Controller:** Interprets the vectors from the Vision Engine, maintains state (e.g., is the user currently swiping?), and triggers actions.
*   **Action Executor:** Interacts with the OS (Windows) using `pyautogui` / `pynput` for keyboard/mouse simulation, and system APIs for volume/microphone control.
*   **UI Overlay:** A borderless, transparent window that sits on top of other applications to provide the "Glass HUD" feedback and privacy blurs.

---

## 2. Detailed Feature Breakdown & Implementation Notes

### A. The Ambient Gesture Engine (Core)
*   **Feature 1: Media Control (Open Palm)**
    *   **Description:** An open palm facing the camera toggles Play/Pause.
    *   **Implementation Note:** Use MediaPipe Hand Tracking. Detect when all 5 fingers are extended and the palm is facing forward. We need a "cooldown" or debounce mechanism (e.g., 1-2 seconds) so it doesn't spam the Play/Pause keystroke if the user holds their hand up.
    *   **Action:** Simulate the Media Play/Pause media key (`pyautogui.press('playpause')`).

*   **Feature 2: Navigation (Swipe Left/Right)**
    *   **Description:** A swift horizontal hand movement advances slides or skips tracks.
    *   **Implementation Note:** Track the x-coordinate of the wrist landmark over a short time window (e.g., 0.5 seconds). If the delta $x$ exceeds a certain threshold (speed/distance), trigger the action.
    *   **Action:** Simulate Right/Left Arrow keys or Media Next/Prev keys.

*   **Feature 3: Ghost-Mute ("Shh" Gesture)**
    *   **Description:** Holding a finger over the lips mutes the system microphone.
    *   **Implementation Note:** Requires both Face and Hand tracking. Measure the distance between the tip of the index finger and the mouth landmarks. If the distance is below a threshold, toggle mute.
    *   **Action:** Windows API call to toggle microphone mute.

### B. Auto-Privacy & Security (ShoulderGuard) (Core)
*   **Feature 1: Intruder Blur**
    *   **Description:** Blurs the screen if a secondary face is detected looking at the monitor.
    *   **Implementation Note:** Use MediaPipe Face Detection. Count the number of detected bounding boxes. If `count > 1`, trigger the UI overlay to maximize and turn opaque/blur. 
    *   **Action:** Summon a borderless, full-screen PyQt/Tkinter window that obscures the screen content until the second face leaves the frame.

*   **Feature 2: Walk-Away Lock**
    *   **Description:** Locks the OS if the primary user leaves the frame.
    *   **Implementation Note:** If face count goes from 1 to 0 for more than $X$ seconds (e.g., 3 seconds to account for dropping a pen), lock the system.
    *   **Action:** Simulate `Win + L` (`os.system('rundll32.exe user32.dll,LockWorkStation')`).

### C. Context-Aware Voice Assistant (Secondary/Stretch)
*   **Feature: Visual-Verbal Commands**
    *   **Description:** Combines pointing with voice (e.g., "Aero, close this").
    *   **Implementation Note:** *High complexity for a 48hr hackathon.* We would need `SpeechRecognition` running concurrently. If "close this" is heard, check where the index finger is pointing (raycasting from webcam to screen coordinates) and send an `Alt+F4` to that specific window. 
    *   **Recommendation:** Deprioritize for the MVP unless visual features are finished early.

### D. Polish & Quality of Life (Secondary)
*   **Feature 1: The "Glass HUD" User Interface**
    *   **Description:** Subtle visual feedback when gestures are recognized.
    *   **Implementation Note:** A small, transparent PyQt window in the corner of the screen. When the Logic Controller triggers an action, update the HUD with a temporary icon (e.g., ⏸️) that fades out after 1 second.

*   **Feature 2: 20-20-20 Wellness Monitor**
    *   **Description:** Reminds user to look away if staring too long.
    *   **Implementation Note:** Use MediaPipe Face Mesh to calculate the Eye Aspect Ratio (EAR). Track time where EAR indicates open eyes.
    *   **Recommendation:** Easy to implement visually, but tracking over 20 minutes is hard to demo live. We can set the demo threshold to 10 seconds for the presentation.

---

## 3. Proposed App Layout (Configuration Window)

While Aero runs invisibly in the background most of the time, users need a central hub to configure it. This configuration window will be accessible via a system tray icon.

**Layout Structure:**

1.  **Header:**
    *   App Logo / Title ("Aero Dashboard")
    *   Global Toggle Switch (Enable/Disable Aero entirely)

2.  **Live Feed & Confidence Meter (Left Panel):**
    *   A small, processed video feed (optional, can be toggled for privacy) showing what Aero sees.
    *   Visual overlays showing skeletal hand tracking and face bounding boxes (great for the demo!).
    *   "Tracking Confidence" progress bar.

3.  **Modules & Settings (Right Panel - Tabbed):**
    *   **Tab 1: Gestures**
        *   Toggles for individual gestures (Enable Palm Pause, Enable Swipe Navigation).
        *   Sensitivity Slider (Distance Calibration - adjusts the thresholds for what constitutes a "swipe").
    *   **Tab 2: Privacy (ShoulderGuard)**
        *   Toggle Enable Intruder Blur.
        *   Toggle Enable Walk-Away Lock.
        *   Slider: Timeout duration for Walk-Away Lock.
    *   **Tab 3: HUD & Wellness**
        *   Toggle Visual Feedback (Glass HUD).
        *   Toggle 20-20-20 Rule (Eye strain monitor).

4.  **Footer:**
    *   "Minimize to Tray" button.
    *   "Quit" button.
