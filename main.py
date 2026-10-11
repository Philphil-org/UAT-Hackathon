import cv2
import mediapipe as mp
import time
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pynput import keyboard
import tkinter as tk
import threading
import queue
import winsound

# --- Floating Capsule (Ambient UI) ---
class FloatingCapsule:
    def __init__(self):
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        # Center top of screen (Micro-Pill for Icons)
        screen_width = self.root.winfo_screenwidth()
        x = (screen_width // 2) - 40
        self.root.geometry(f"80x50+{x}+40")
        
        self.root.configure(bg="#0F0F14")
        self.frame = tk.Frame(self.root, bg="#0F0F14", highlightbackground="#D4AF6A", highlightthickness=1)
        self.frame.pack(fill="both", expand=True)
        
        # Larger font for crisp Unicode icons
        self.label = tk.Label(self.frame, text="", fg="#D4AF6A", bg="#0F0F14", font=("Segoe UI", 22))
        self.label.pack(expand=True)
        
        self.root.withdraw()
        self.hide_id = None
        
        self.root.after(10, self._check_queue)
        self.root.mainloop()

    def _check_queue(self):
        try:
            msg = self.q.get_nowait()
            self.label.config(text=msg)
            self.root.deiconify()
            
            if self.hide_id:
                self.root.after_cancel(self.hide_id)
            self.hide_id = self.root.after(1500, self.root.withdraw)
        except queue.Empty:
            pass
        self.root.after(50, self._check_queue)

    def show(self, text, beep="default"):
        self.q.put(text)
        try:
            sound_map = {
                "playpause": "sounds/playpause.wav",
                "next": "sounds/next.wav",
                "prev": "sounds/prev.wav",
                "shush": "sounds/mute.wav",
                "shield": "sounds/shield.wav",
                "tap": "sounds/next.wav",
            }
            sound_file = sound_map.get(beep)
            if sound_file and os.path.exists(sound_file):
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

# --- Smart Typing Detection (Background Listener) ---
last_keypress_time = 0

def on_key_press(key):
    global last_keypress_time
    # Ignore simulated media keys sent by pyautogui so our gestures don't lock us out
    try:
        ignore_keys = [
            keyboard.Key.media_play_pause, keyboard.Key.media_next, keyboard.Key.media_previous,
            keyboard.Key.media_volume_up, keyboard.Key.media_volume_down, keyboard.Key.media_volume_mute,
            keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r
        ]
        if key in ignore_keys:
            return
    except Exception:
        pass
    last_keypress_time = time.time()

keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.daemon = True
keyboard_listener.start()

# Disable pyautogui's default 0.1s delay so volume sliding is instantly responsive
pyautogui.PAUSE = 0

def draw_landmarks(frame, hand_landmarks):
    """Manually draw circles for the joints (landmarks)."""
    h, w, c = frame.shape
    for lm in hand_landmarks:
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

def is_palm_open(hand_landmarks, handedness):
    """Check if the hand is in an open palm pose."""
    wrist = hand_landmarks[0]
    palm_height = get_dist(wrist, hand_landmarks[9])
    
    # 1. Main fingertips must be extended. 
    # Relaxed to 1.2 so your fingers can have a natural, comfortable curve instead of being perfectly straight
    for tip in [8, 12, 16, 20]:
        if get_dist(hand_landmarks[tip], wrist) < palm_height * 1.2:
            return False
            
    # 2. Fingers must be somewhat spread (distance between index and pinky)
    index_tip = hand_landmarks[8]
    pinky_tip = hand_landmarks[20]
    if get_dist(index_tip, pinky_tip) < palm_height * 0.6:
        return False
        
    # 3. Thumb must be explicitly extended away from the index finger
    thumb_tip = hand_landmarks[4]
    if get_dist(thumb_tip, index_tip) < palm_height * 0.6:
        return False
        
    # 4. Ensure palm is facing the camera (not the back of the hand)
    # Due to the mirrored camera, MediaPipe's "Left" is the physical Right hand
    if handedness == "Left":
        if thumb_tip.x > pinky_tip.x:
            return False
    else:
        if thumb_tip.x < pinky_tip.x:
            return False
            
    return True

def is_back_of_hand_open(hand_landmarks, handedness):
    """Check if the hand is in an open pose with the BACK OF THE HAND facing the camera."""
    wrist = hand_landmarks[0]
    palm_height = get_dist3d(wrist, hand_landmarks[9])
    
    # 1. Main fingertips must be extended.
    # Measured from knuckles (MCPs) so wrist tilting/dropping doesn't compress distance
    for tip, mcp in [(8, 5), (12, 9), (16, 13), (20, 17)]:
        if get_dist3d(hand_landmarks[tip], hand_landmarks[mcp]) < palm_height * 0.45:
            return False
            
    # 2. Fingers reasonably spread
    index_tip = hand_landmarks[8]
    pinky_tip = hand_landmarks[20]
    if get_dist3d(index_tip, pinky_tip) < palm_height * 0.35:
        return False
        
    # 3. Ensure BACK of the hand is facing the camera
    # Due to mirrored camera: Left (physical Right) has thumb_tip.x > pinky_tip.x for back of hand
    thumb_tip = hand_landmarks[4]
    if handedness == "Left":
        if thumb_tip.x <= pinky_tip.x:
            return False
    else:
        if thumb_tip.x >= pinky_tip.x:
            return False
            
    return True

def get_dist(lm1, lm2):
    return ((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)**0.5

def get_dist3d(lm1, lm2):
    # MediaPipe z-coordinates are roughly proportional to x/y scale.
    # Including Z heavily penalizes "overlapping" fingers that aren't actually touching in 3D depth (e.g. gripping a phone)
    return ((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2 + (lm1.z - lm2.z)**2)**0.5







def check_pinch_active(hand_landmarks):
    """Check if the hand is in a 'Pinch' or 'L' shape (Index out, Thumb out, others curled)."""
    wrist = hand_landmarks[0]
    index_mcp = hand_landmarks[5]
    palm_height = get_dist(wrist, hand_landmarks[9])
    
    # 1. Middle, Ring, and Pinky must be curled
    for tip in [12, 16, 20]:
        if get_dist(hand_landmarks[tip], wrist) > palm_height * 1.2:
            return False
            
    # 2. Index finger must be extended
    if get_dist(hand_landmarks[8], wrist) < palm_height * 1.4:
        return False
        
    return True

import os
import json

def get_hand_size(hand_landmarks):
    """Calculate an approximate bounding box area for the hand to determine proximity."""
    x_coords = [lm.x for lm in hand_landmarks]
    y_coords = [lm.y for lm in hand_landmarks]
    return (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))

def main():
    capsule = FloatingCapsule()
    
    # Load Settings from config.json (managed by launcher)
    config = {
        "camera_index": 0,
        "show_camera_feed": True,
        "shoulder_guard": True,
        "typing_lockout": True
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Failed to load config: {e}")

    # Setup HandLandmarker using the new Tasks API
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.85,
        min_hand_presence_confidence=0.85,
        min_tracking_confidence=0.85)
    
    # Initialize the detector
    detector = vision.HandLandmarker.create_from_options(options)
    
    # Setup FaceDetector for ShoulderGuard
    base_options_face = python.BaseOptions(model_asset_path='blaze_face_short_range.tflite')
    options_face = vision.FaceDetectorOptions(
        base_options=base_options_face,
        running_mode=vision.RunningMode.VIDEO,
        min_detection_confidence=0.6,
        min_suppression_threshold=0.5)
    face_detector = vision.FaceDetector.create_from_options(options_face)
    
    cap = cv2.VideoCapture(config['camera_index'])
    # Force higher resolution (720p)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Aero Vision Engine. Press 'q' to quit.")
    
    # We need a monotonically increasing timestamp in MS for the video mode
    start_time_ms = int(time.time() * 1000)
    prev_time = time.time()
    
    last_palm_time = 0
    palm_start_time = None
    prev_points = None
    
    back_swipe_anchor_x = None
    back_swipe_anchor_y = None
    back_swipe_start_time = 0
    last_track_swipe_time = 0
    back_swipe_locked_out = False
    swipe_grace_frames = 0
    
    prev_pinch_dist = None
    pinch_start_time = None
    volume_active = False
    volume_last_change_time = 0
    pinch_locked_out = False
    volume_initial_dir = None
    
    privacy_mode = False
    privacy_trigger_start = None
    
    prev_palm_height = None
    prev_thumb_tip = None
    prev_index_tip = None
    jitter_cooldown = 0
    
    shush_active = False
    last_shush_time = 0
    was_hand_present = False
    
    last_config_check_time = 0
    last_config_mtime = 0
    prev_show_camera = config.get('show_camera_feed', True)
    
    smoothed_yaw = 0.0
    last_gaze_engaged = True
    last_face_seen_time = 0

    while True:
        # Live config reload (responds instantly to toggles in launcher)
        if time.time() - last_config_check_time > 0.2:
            last_config_check_time = time.time()
            if os.path.exists("config.json"):
                try:
                    mtime = os.path.getmtime("config.json")
                    if mtime != last_config_mtime:
                        last_config_mtime = mtime
                        with open("config.json", "r") as f:
                            config.update(json.load(f))
                        
                        # Live toggle camera debug window
                        cur_show = config.get('show_camera_feed', True)
                        if prev_show_camera and not cur_show:
                            cv2.destroyAllWindows()
                            cv2.waitKey(1)
                        prev_show_camera = cur_show
                except Exception:
                    pass

        success, frame = cap.read()
        if not success:
            print("Failed to grab frame.")
            break

        # Flip the frame for a selfie-view
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape # Define here so HUD can use it even when no hands are in frame
        
        # --- Environmental Adaptive Exposure (CLAHE Low-Light Boost) ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_luminance = cv2.mean(gray)[0]
        low_light_active = False
        
        if avg_luminance < 65.0: # Dim or backlit environment
            low_light_active = True
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_chan, a_chan, b_chan = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
            cl = clahe.apply(l_chan)
            enhanced_lab = cv2.merge((cl, a_chan, b_chan))
            frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert numpy array to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Calculate timestamp offset
        current_time_ms = int(time.time() * 1000)
        timestamp_ms = current_time_ms - start_time_ms
        
        results = None
        try:
            # Process the frame for hands and faces
            results = detector.detect_for_video(mp_image, timestamp_ms)
            
            # Run face detection if ShoulderGuard OR Gaze-Clutch is enabled
            if config.get('shoulder_guard', True) or config.get('gaze_clutch', True):
                face_results = face_detector.detect_for_video(mp_image, timestamp_ms)
            else:
                class EmptyResults: detections = []
                face_results = EmptyResults()
            
            # --- ShoulderGuard: Face Tracking & Privacy ---
            faces_detected = 0
            primary_face_center = None
            max_face_area = 0
            is_gaze_engaged = True
            
            if face_results.detections:
                faces_detected = len(face_results.detections)
                last_face_seen_time = time.time()
                for detection in face_results.detections:
                    bbox = detection.bounding_box
                    x, y, fw, fh = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
                    
                    area = fw * fh
                    if area > max_face_area:
                        max_face_area = area
                        primary_face_center = (x + fw//2, y + fh//2)
                        
                        # --- Gaze-Clutch™ Head Yaw Telemetry with Smoothing ---
                        if hasattr(detection, 'keypoints') and len(detection.keypoints) >= 3:
                            kp = detection.keypoints
                            r_eye, l_eye, nose = kp[0], kp[1], kp[2]
                            eye_center_x = (r_eye.x + l_eye.x) / 2.0
                            eye_dist = abs(l_eye.x - r_eye.x)
                            if eye_dist > 0.01:
                                raw_yaw = abs(nose.x - eye_center_x) / eye_dist
                                # Smooth with Exponential Moving Average to prevent hand clipping spikes
                                smoothed_yaw = 0.65 * smoothed_yaw + 0.35 * raw_yaw
                                is_gaze_engaged = smoothed_yaw <= 0.28
                                last_gaze_engaged = is_gaze_engaged
                                    
                # Draw facial telemetry
                for detection in face_results.detections:
                    bbox = detection.bounding_box
                    x, y, fw, fh = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
                    box_color = (0, 215, 255) if is_gaze_engaged else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + fw, y + fh), box_color, 2)
                    if config.get('gaze_clutch', True):
                        gaze_text = "GAZE: ENGAGED" if is_gaze_engaged else "GAZE: LOOKING AWAY"
                        cv2.putText(frame, gaze_text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_color, 2)
            else:
                # Face occluded by hand or off-screen
                if config.get('gaze_clutch', True):
                    # If face missing for >0.25s, cannot verify gaze -> keep gestures paused!
                    if time.time() - last_face_seen_time > 0.25:
                        is_gaze_engaged = False
                    else:
                        is_gaze_engaged = last_gaze_engaged
                        
            # Privacy Mode Trigger (Shoulder Surfer)
            if config.get('shoulder_guard', True) and faces_detected > 1:
                if privacy_trigger_start is None:
                    privacy_trigger_start = time.time()
                elif time.time() - privacy_trigger_start > 0.5: # 0.5s requirement to prevent blips
                    if not privacy_mode:
                        privacy_mode = True
                        capsule.show('🛡️', 'shield')
                        try: pyautogui.hotkey('win', 'd') # Show Desktop
                        except: pass
            else:
                privacy_trigger_start = None
                if privacy_mode:
                    privacy_mode = False
                    capsule.show("?", "default")
                    try: pyautogui.hotkey('win', 'd') # Restore windows
                    except: pass
                    
            if privacy_mode:
                # Draw massive warning and skip all hand gestures
                cv2.putText(frame, "PRIVACY SHIELD ACTIVE", (w//2 - 250, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
                if config.get('show_camera_feed', True):
                    cv2.imshow('Aero Vision Engine (Debug)', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                else:
                    time.sleep(0.03) # Match camera framerate pacing roughly
                continue # Skip gesture processing
            
            hand_is_present = bool(results.hand_landmarks)
            if hand_is_present and not was_hand_present:
                capsule.show('✋', beep=None)
            was_hand_present = hand_is_present
            
            # Draw green circles on the joints for all hands
            if results.hand_landmarks and results.handedness:
                primary_hand_idx = -1
                max_size = 0
                
                # First pass: Draw all hands and find the largest one (primary user)
                for idx, hand_landmarks in enumerate(results.hand_landmarks):
                    draw_landmarks(frame, hand_landmarks)
                    
                    size = get_hand_size(hand_landmarks)
                    if size > max_size:
                        max_size = size
                        primary_hand_idx = idx

                # Second pass: Only check gestures for the primary hand
                if primary_hand_idx != -1:
                    primary_landmarks = results.hand_landmarks[primary_hand_idx]
                    primary_handedness = results.handedness[primary_hand_idx][0].category_name
                    
                    # --- ShoulderGuard: Body Ownership Lock-On ---
                    # We tie the hand to the primary face to ensure background people can't steal control!
                    owns_hand = True
                    if primary_face_center is not None:
                        wrist = primary_landmarks[0]
                        wrist_px = (int(wrist.x * w), int(wrist.y * h))
                        face_px = primary_face_center
                        
                        dist_to_face = ((wrist_px[0] - face_px[0])**2 + (wrist_px[1] - face_px[1])**2)**0.5
                        face_width = max_face_area**0.5 # Approximate width
                        
                        # If the hand is more than 3.5x the width of your face away from your face, it's not yours!
                        if dist_to_face > face_width * 3.5:
                            owns_hand = False
                            cv2.putText(frame, "HAND REJECTED (Too Far)", (wrist_px[0]-80, wrist_px[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    if owns_hand:
                        # Highlight the primary hand's wrist with a blue circle to show who has control
                        wrist_x, wrist_y = int(primary_landmarks[0].x * w), int(primary_landmarks[0].y * h)
                        cv2.circle(frame, (wrist_x, wrist_y), 15, (255, 0, 0), -1)
                        
                        # --- Anti-Jitter Physics Engine ---
                        # When holding a phone, MediaPipe hallucinates the hand structure and jitters wildly.
                        # We use simple physics (teleportation speed + rigid bone length) to detect this hallucination!
                        is_jittering = False
                        palm_height = get_dist(primary_landmarks[0], primary_landmarks[9])
                        current_thumb_tip = (primary_landmarks[4].x, primary_landmarks[4].y)
                        current_index_tip = (primary_landmarks[8].x, primary_landmarks[8].y)
                        
                        if prev_palm_height is not None and prev_thumb_tip is not None and prev_index_tip is not None:
                            # 1. Bone Length Change: The palm cannot physically change size.
                            if abs(palm_height - prev_palm_height) / prev_palm_height > 0.25:
                                is_jittering = True
                            
                            # 2. Teleportation: A finger cannot move >20% of the screen in a single frame.
                            thumb_jump = ((current_thumb_tip[0] - prev_thumb_tip[0])**2 + (current_thumb_tip[1] - prev_thumb_tip[1])**2)**0.5
                            index_jump = ((current_index_tip[0] - prev_index_tip[0])**2 + (current_index_tip[1] - prev_index_tip[1])**2)**0.5
                            if thumb_jump > 0.20 or index_jump > 0.20:
                                is_jittering = True
                                
                        # 3. Structural Deformity (Holding an object):
                        # The hand knuckles should form a relatively stable width.
                        # If the palm width is impossibly narrow compared to its height, the hand is either
                        # edge-on (unusable for gestures anyway) or it's hallucinating around a phone.
                        palm_width = get_dist(primary_landmarks[5], primary_landmarks[17])
                        if palm_width < palm_height * 0.30:
                            is_jittering = True
                                
                        # Update physics state for next frame
                        prev_palm_height = palm_height
                        prev_thumb_tip = current_thumb_tip
                        prev_index_tip = current_index_tip
                        
                        if is_jittering:
                            jitter_cooldown = time.time()
                            
                        # If the hand has jittered in the last 0.5 seconds, pause all gesture processing!
                        jitter_paused = time.time() - jitter_cooldown < 0.5
                        
                        # If the user has typed on the keyboard in the last 2 seconds, pause gestures!
                        typing_paused = False
                        if config.get('typing_lockout', True):
                            typing_paused = time.time() - last_keypress_time < 2.0
                        
                        # If Gaze-Clutch is enabled and user is looking away, pause gestures!
                        gaze_paused = False
                        if config.get('gaze_clutch', True) and not is_gaze_engaged:
                            gaze_paused = True
                        
                        gestures_paused = jitter_paused or typing_paused or gaze_paused
                        
                        if jitter_paused:
                            cv2.putText(frame, "JITTER PAUSE", (wrist_x - 60, wrist_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                        elif typing_paused:
                            cv2.putText(frame, "TYPING - STANDBY", (wrist_x - 80, wrist_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                        elif gaze_paused:
                            cv2.putText(frame, "GAZE PAUSE (LOOKING AWAY)", (wrist_x - 110, wrist_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 2)
                            
                        # Calculate Motion (Stillness Check on Wrist and Index Tip)
                        current_points = (
                        primary_landmarks[0].x, primary_landmarks[0].y, # Wrist
                        primary_landmarks[8].x, primary_landmarks[8].y  # Index Tip
                    )
                        is_still = False
                        if prev_points:
                            # Calculate Euclidean distance between current and previous positions
                            wrist_dist = ((current_points[0] - prev_points[0])**2 + (current_points[1] - prev_points[1])**2)**0.5
                            tip_dist = ((current_points[2] - prev_points[2])**2 + (current_points[3] - prev_points[3])**2)**0.5
                            
                            if wrist_dist < 0.03 and tip_dist < 0.04: # Threshold for "still"
                                is_still = True
                        prev_points = current_points
    
                        # Check for open palm gesture AND stillness
                        if is_palm_open(primary_landmarks, primary_handedness) and is_still and not gestures_paused:
                            if palm_start_time is None:
                                palm_start_time = time.time()
                                
                            # Calculate hold progress (0.0 to 1.0)
                            hold_duration = time.time() - palm_start_time
                            progress = min(1.0, hold_duration / 0.5)
                            end_angle = int(360 * progress)
                            
                            # Draw the animated loading ring (Yellow arc) around the wrist
                            # (center_x, center_y), (axes_x, axes_y), angle, startAngle, endAngle, color, thickness
                            cv2.ellipse(frame, (wrist_x, wrist_y), (35, 35), -90, 0, end_angle, (0, 255, 255), 5)
                            
                            # Require the gesture to be held steady for 0.5 seconds
                            if progress >= 1.0:
                                # Flash green to indicate success
                                cv2.circle(frame, (wrist_x, wrist_y), 40, (0, 255, 0), -1)
                                
                                # Debounce / Cooldown: Only trigger once every 1.5 seconds
                                if time.time() - last_palm_time > 1.5:
                                    capsule.show('⏯', 'playpause')
                                    
                                    # Execute the OS-level media command
                                    try:
                                        pyautogui.press('playpause')
                                    except Exception as e:
                                        print(f"Failed to press media key: {e}")
                                        
                                    last_palm_time = time.time()
                                    palm_start_time = None # Reset after trigger
                        else:
                            # Reset the hold timer if the gesture breaks or hand moves
                            palm_start_time = None
                            
                        # --- "Shush" Instant Mute (Boss Key) ---
                        # If the index finger is extended and placed over the mouth area
                        if primary_face_center is not None and not gestures_paused:
                            index_tip = primary_landmarks[8]
                            index_px = (int(index_tip.x * w), int(index_tip.y * h))
                            dist_to_face = ((index_px[0] - primary_face_center[0])**2 + (index_px[1] - primary_face_center[1])**2)**0.5
                            
                            # The face_width is approx max_face_area**0.5
                            face_width = max_face_area**0.5
                            
                            # If index finger is very close to the center of the face (nose/mouth)
                            if dist_to_face < face_width * 0.7:
                                # Ensure it's a shush (index extended, middle curled)
                                middle_dist = get_dist(primary_landmarks[12], primary_landmarks[0])
                                index_dist = get_dist(primary_landmarks[8], primary_landmarks[0])
                                
                                if index_dist > palm_height * 1.3 and middle_dist < palm_height * 1.1:
                                    cv2.circle(frame, index_px, 20, (0, 0, 255), -1) # Red indicator for mute
                                    if time.time() - last_shush_time > 1.5:
                                        capsule.show('🔇', 'shush')
                                        try: pyautogui.press('volumemute')
                                        except: pass
                                        last_shush_time = time.time()
                                        shush_active = True
                                else:
                                    shush_active = False
                            else:
                                shush_active = False
    
                        # --- Back-of-Hand Swipe (Next/Prev Track) ---
                        # Open hand with the BACK of the hand facing the camera, swiped Left/Right
                        if is_back_of_hand_open(primary_landmarks, primary_handedness) and not gestures_paused:
                            swipe_grace_frames = 0
                            # Use Landmark 9 (Middle MCP / palm center) so wrist flexing/tilting doesn't skew motion
                            hand_ref = primary_landmarks[9]
                            current_time = time.time()
                            
                            # Auto-unlock cooldown after 1.2s if hand is still held up
                            if back_swipe_locked_out and (current_time - last_track_swipe_time > 1.2):
                                back_swipe_locked_out = False
                                
                            if back_swipe_locked_out:
                                # Show subtle cooldown indicator while user lowers hand or resets
                                cv2.putText(frame, "COOLDOWN", (wrist_x - 50, wrist_y + 35),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                                back_swipe_anchor_x = None
                                back_swipe_anchor_y = None
                            else:
                                if back_swipe_anchor_x is None:
                                    back_swipe_anchor_x = hand_ref.x
                                    back_swipe_anchor_y = hand_ref.y
                                    back_swipe_start_time = current_time
                                else:
                                    elapsed = current_time - back_swipe_start_time
                                    dx = hand_ref.x - back_swipe_anchor_x
                                    swipe_threshold = 0.09 # Responsive deadzone
                                    
                                    # --- Visual Guide in Debug Window (Rail glides with hand height) ---
                                    curr_y = int(hand_ref.y * h)
                                    anchor_px = (int(back_swipe_anchor_x * w), curr_y)
                                    curr_px = (int(hand_ref.x * w), curr_y)
                                    left_bound = (int((back_swipe_anchor_x - swipe_threshold) * w), curr_y)
                                    right_bound = (int((back_swipe_anchor_x + swipe_threshold) * w), curr_y)
                                    
                                    # Draw level rail and boundary targets
                                    cv2.line(frame, left_bound, right_bound, (80, 80, 80), 2)
                                    cv2.circle(frame, left_bound, 9, (0, 165, 255), -1)   # Orange: Prev
                                    cv2.circle(frame, right_bound, 9, (0, 255, 0), -1)   # Green: Next
                                    cv2.circle(frame, anchor_px, 6, (255, 255, 255), -1) # Static Anchor
                                    
                                    line_col = (0, 215, 255)
                                    if dx > swipe_threshold or dx < -swipe_threshold:
                                        line_col = (0, 255, 0)
                                    cv2.line(frame, anchor_px, curr_px, line_col, 3)
                                    cv2.circle(frame, curr_px, 12, line_col, -1)
                                    cv2.putText(frame, "BACK-HAND SWIPE", (wrist_x - 80, wrist_y + 35),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 215, 255), 2)
                                    
                                    # --- Trigger Gesture on Threshold Cross ---
                                    if current_time - last_track_swipe_time > 0.9:
                                        if dx > swipe_threshold: # Swiped Right -> Next Track
                                            capsule.show('⏭', 'next')
                                            try: pyautogui.press('nexttrack')
                                            except: pass
                                            last_track_swipe_time = current_time
                                            back_swipe_locked_out = True
                                            back_swipe_anchor_x = None
                                            back_swipe_anchor_y = None
                                        elif dx < -swipe_threshold: # Swiped Left -> Prev Track
                                            capsule.show('⏮', 'prev')
                                            try: pyautogui.press('prevtrack')
                                            except: pass
                                            last_track_swipe_time = current_time
                                            back_swipe_locked_out = True
                                            back_swipe_anchor_x = None
                                            back_swipe_anchor_y = None
                                            
                                    # Anchor Stability:
                                    # Freeze anchor during motion (abs(dx) >= 0.025); drift gently when idle
                                    if abs(dx) < 0.025 and elapsed > 0.35:
                                        back_swipe_anchor_x = hand_ref.x
                                        back_swipe_anchor_y = hand_ref.y
                                        back_swipe_start_time = current_time
                        else:
                            # Grace buffer: don't abort active swipe on a 1-2 frame tracking dip
                            if back_swipe_anchor_x is not None and swipe_grace_frames < 3:
                                swipe_grace_frames += 1
                            else:
                                back_swipe_anchor_x = None
                                back_swipe_anchor_y = None
                                back_swipe_locked_out = False
                                swipe_grace_frames = 0
                                
                        # --- Dynamic Volume Control (Pinch Slider) ---
                        # This runs if palm is not active
                        if not is_palm_open(primary_landmarks, primary_handedness) and not gestures_paused:
                            if check_pinch_active(primary_landmarks):
                                if pinch_locked_out:
                                    # We are waiting for them to break the L-Shape pose before allowing another volume change
                                    pass
                                else:
                                    pinch_dist = get_dist3d(primary_landmarks[4], primary_landmarks[8])
                                    
                                    # Draw a line between thumb and index for visual UI feedback
                                    x1, y1 = int(primary_landmarks[4].x * w), int(primary_landmarks[4].y * h)
                                    x2, y2 = int(primary_landmarks[8].x * w), int(primary_landmarks[8].y * h)
                                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 4) # Magenta line
                                    cv2.circle(frame, ((x1+x2)//2, (y1+y2)//2), 8, (255, 0, 255), -1)
                                    
                                    if not volume_active:
                                        if is_still:
                                            if pinch_start_time is None:
                                                pinch_start_time = time.time()
                                                
                                            progress = min(1.0, (time.time() - pinch_start_time) / 0.5)
                                            end_angle = int(360 * progress)
                                            # Draw loading ring on the thumb tip
                                            cv2.ellipse(frame, (x1, y1), (30, 30), -90, 0, end_angle, (0, 255, 255), 5)
                                            
                                            if progress >= 1.0:
                                                volume_active = True
                                                prev_pinch_dist = pinch_dist
                                                volume_last_change_time = time.time()
                                                volume_initial_dir = None
                                                cv2.circle(frame, (x1, y1), 35, (0, 255, 0), -1)
                                        else:
                                            pinch_start_time = None
                                    
                                    elif volume_active and prev_pinch_dist is not None:
                                        delta = pinch_dist - prev_pinch_dist
                                        
                                        # For every 0.4% screen distance change, press volume key once
                                        steps = int(abs(delta) / 0.004) 
                                        if steps > 0:
                                            if delta > 0:
                                                if volume_initial_dir == "DOWN":
                                                    # Require a deliberate 1.6% reverse flick (4 steps) to cancel, ignoring natural hand jitter
                                                    if steps >= 4:
                                                        print("🛑 VOLUME CANCELLED (Deliberate Direction Reversed)")
                                                        volume_active = False
                                                        pinch_start_time = None
                                                        prev_pinch_dist = None
                                                        pinch_locked_out = True
                                                        volume_initial_dir = None
                                                else:
                                                    volume_initial_dir = "UP"
                                                    capsule.show('🔊', beep=None)
                                                    for _ in range(steps): pyautogui.press('volumeup')
                                                    prev_pinch_dist = pinch_dist
                                                    volume_last_change_time = time.time()
                                            else:
                                                if volume_initial_dir == "UP":
                                                    # Require a deliberate 1.6% reverse flick (4 steps) to cancel
                                                    if steps >= 4:
                                                        print("🛑 VOLUME CANCELLED (Deliberate Direction Reversed)")
                                                        volume_active = False
                                                        pinch_start_time = None
                                                        prev_pinch_dist = None
                                                        pinch_locked_out = True
                                                        volume_initial_dir = None
                                                else:
                                                    volume_initial_dir = "DOWN"
                                                    capsule.show('🔉', beep=None)
                                                    for _ in range(steps): pyautogui.press('volumedown')
                                                    prev_pinch_dist = pinch_dist
                                                    volume_last_change_time = time.time()
                                                    
                                        elif time.time() - volume_last_change_time > 0.4:
                                            # If held still for 0.4 seconds, lock it out
                                            volume_active = False
                                            pinch_start_time = None
                                            prev_pinch_dist = None
                                            pinch_locked_out = True
                                            volume_initial_dir = None
                            else:
                                # They broke the pose
                                pinch_locked_out = False
                                volume_active = False
                                pinch_start_time = None
                                prev_pinch_dist = None
                                volume_initial_dir = None
                        else:
                            pinch_locked_out = False
                            volume_active = False
                            pinch_start_time = None
                            prev_pinch_dist = None
                            volume_initial_dir = None
                            
        except Exception as e:
            # Safely catch any timestamp overlapping errors and continue
            pass
                
        if not results or not results.hand_landmarks:
            prev_points = None
            hitchhiker_start_x = None
            prev_pinch_dist = None
            prev_palm_height = None
            prev_thumb_tip = None
            prev_index_tip = None
            pinch_start_time = None
            volume_active = False
            back_swipe_anchor_x = None
            back_swipe_anchor_y = None
            back_swipe_locked_out = False

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 1e-5)
        prev_time = curr_time
        cv2.putText(frame, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Environmental Lighting Telemetry
        lum_text = f"LIGHT BOOST: ACTIVE (LUM {int(avg_luminance)})" if low_light_active else f"LIGHT: NORMAL (LUM {int(avg_luminance)})"
        lum_color = (0, 215, 255) if low_light_active else (180, 180, 180)
        cv2.putText(frame, lum_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, lum_color, 2)
    
            # Show the video
        if config.get('show_camera_feed', True):
            cv2.imshow('Aero Vision Engine (Debug)', frame)
    
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            time.sleep(0.01)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()




