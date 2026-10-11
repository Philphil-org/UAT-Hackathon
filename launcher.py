import customtkinter as ctk
import subprocess
import threading
import os
import sys
import json
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import multiprocessing.shared_memory as shm_module

CONFIG_FILE = "config.json"

# Brand Palette (ZeroTouch Spec)
MIDNIGHT_INK = "#0F0F14"
HARD_GRAPHITE = "#181820"
HARD_GRAPHITE_LIGHT = "#22222C"
CHAMPAGNE_GOLD = "#D4AF6A"
SLATE_BLUE = "#4A6FA5"
SOFT_WHITE = "#F2EFE9"
COOL_GRAY = "#8A8D93"

def create_tray_icon_image():
    """Generate a clean dark-gold circular emblem for the system tray."""
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 60, 60], fill=MIDNIGHT_INK, outline=CHAMPAGNE_GOLD, width=3)
    d.ellipse([22, 22, 42, 42], fill=CHAMPAGNE_GOLD)
    return img

class ZeroTouchWidget(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZeroTouch")
        self.geometry("350x640")
        self.minsize(320, 600)
        self.configure(fg_color=MIDNIGHT_INK)
        self.resizable(False, False)
        
        # High DPI Support
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Load Config
        self.config = {
            "camera_index": 0,
            "show_camera_feed": True,
            "shoulder_guard": True,
            "typing_lockout": True,
            "gaze_clutch": True
        }
        self.load_config()
        self.process = None

        # Fonts
        self.font_brand = ctk.CTkFont(family="Georgia", size=28, weight="bold", slant="italic")
        self.font_primary = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_secondary = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_telemetry = ctk.CTkFont(family="Consolas", size=10, weight="bold")

        # Container Frame
        self.container = ctk.CTkFrame(self, fg_color=MIDNIGHT_INK, corner_radius=0)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self.brand_lbl = ctk.CTkLabel(self.container, text="ZeroTouch", font=self.font_brand, text_color=CHAMPAGNE_GOLD)
        self.brand_lbl.pack(pady=(5, 0), anchor="center")
        
        self.sub_lbl = ctk.CTkLabel(self.container, text="SPATIAL OS COMPANION", font=self.font_telemetry, text_color=COOL_GRAY)
        self.sub_lbl.pack(pady=(0, 16), anchor="center")

        # Hero Action Button (Start / Stop)
        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=(0, 16))

        self.start_btn = ctk.CTkButton(
            self.btn_frame, text="▶ START ENGINE", font=self.font_primary,
            fg_color=CHAMPAGNE_GOLD, text_color=MIDNIGHT_INK, hover_color="#B59350",
            height=42, command=self.start_engine
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = ctk.CTkButton(
            self.btn_frame, text="⬛ STOP", font=self.font_primary,
            fg_color=HARD_GRAPHITE_LIGHT, text_color=SOFT_WHITE, hover_color="#333344",
            height=42, state="disabled", command=self.stop_engine
        )
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Settings Card
        self.card = ctk.CTkFrame(self.container, fg_color=HARD_GRAPHITE, corner_radius=10, border_width=1, border_color="#262633")
        self.card.pack(fill="x", pady=(0, 14), padx=2, ipady=8)

        # Switches
        self.show_cam_var = ctk.BooleanVar(value=self.config["show_camera_feed"])
        self.sw1 = ctk.CTkSwitch(self.card, text="Camera Preview (Debug)", font=self.font_secondary, text_color=SOFT_WHITE, 
                                 variable=self.show_cam_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw1.pack(pady=(8, 6), padx=16, anchor="w")

        self.shoulder_var = ctk.BooleanVar(value=self.config["shoulder_guard"])
        self.sw2 = ctk.CTkSwitch(self.card, text="ShoulderGuard™ Privacy", font=self.font_secondary, text_color=SOFT_WHITE, 
                                 variable=self.shoulder_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw2.pack(pady=6, padx=16, anchor="w")

        self.typing_var = ctk.BooleanVar(value=self.config["typing_lockout"])
        self.sw3 = ctk.CTkSwitch(self.card, text="Smart Typing Lockout", font=self.font_secondary, text_color=SOFT_WHITE, 
                                 variable=self.typing_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw3.pack(pady=6, padx=16, anchor="w")

        self.gaze_var = ctk.BooleanVar(value=self.config.get("gaze_clutch", True))
        self.sw4 = ctk.CTkSwitch(self.card, text="Gaze-Clutch™ (Look-to-Control)", font=self.font_secondary, text_color=SOFT_WHITE, 
                                 variable=self.gaze_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw4.pack(pady=6, padx=16, anchor="w")

        # Live Vision Preview & Telemetry Subpanel (Embedded Dashboard Feed)
        self.preview_frame = ctk.CTkFrame(self.card, fg_color="#121218", corner_radius=8, border_width=1, border_color="#2A2A38")
        self.preview_frame.pack(fill="x", padx=16, pady=(10, 4))

        self.telemetry_header = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.telemetry_header.pack(fill="x", padx=8, pady=(6, 2))

        self.fps_lbl = ctk.CTkLabel(self.telemetry_header, text="FPS: --", font=self.font_telemetry, text_color=COOL_GRAY)
        self.fps_lbl.pack(side="left")

        self.lum_lbl = ctk.CTkLabel(self.telemetry_header, text="LUM: --", font=self.font_telemetry, text_color=COOL_GRAY)
        self.lum_lbl.pack(side="left", padx=(10, 0))

        self.gaze_pill = ctk.CTkLabel(self.telemetry_header, text="GAZE: STANDBY", font=self.font_telemetry, text_color=COOL_GRAY)
        self.gaze_pill.pack(side="right")

        # 300x168 Preview Image Display
        self.preview_canvas = ctk.CTkLabel(self.preview_frame, text="", fg_color="#0A0A0E", corner_radius=6, height=168)
        self.preview_canvas.pack(fill="x", padx=6, pady=(0, 6))

        # Camera Dropdown
        ctk.CTkLabel(self.card, text="CAMERA INPUT", font=self.font_telemetry, text_color=COOL_GRAY).pack(pady=(8, 2), padx=16, anchor="w")
        idx_val = str(self.config["camera_index"])
        cams = self.get_cameras()
        matched_cam = next((c for c in cams if c.startswith(f"{idx_val}:")), cams[0])
        self.cam_idx_var = ctk.StringVar(value=matched_cam)
        self.cam_combo = ctk.CTkOptionMenu(
            self.card, values=cams, variable=self.cam_idx_var,
            fg_color=HARD_GRAPHITE_LIGHT, button_color=SLATE_BLUE,
            font=self.font_secondary, text_color=SOFT_WHITE,
            command=self.save_config_combo
        )
        self.cam_combo.pack(pady=(2, 6), padx=16, fill="x")

        # Hide to Tray Button
        self.tray_btn = ctk.CTkButton(
            self.container, text="Minimize to Tray", font=self.font_secondary,
            fg_color="transparent", border_width=1, border_color="#333344",
            text_color=COOL_GRAY, hover_color="#22222C", height=32,
            command=self.hide_to_tray
        )
        self.tray_btn.pack(fill="x", pady=(0, 10))

        # Trust Badge Footer
        self.badge = ctk.CTkLabel(
            self.container, text="🔒 Local RAM Inference • Zero Frames Stored",
            font=self.font_telemetry, text_color=SLATE_BLUE
        )
        self.badge.pack(side="bottom", pady=(0, 2))

        # Shared Memory Reader Setup
        self.shm_client = None
        self.after(500, self.update_telemetry_loop)

        # Window Close Protocol -> Minimize to Tray
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # Setup System Tray
        self.setup_tray()

    def get_cameras(self):
        try:
            res = subprocess.check_output(['powershell', '-NoProfile', '-Command', 
                "Get-PnpDevice -Class Camera -Status OK | Select-Object -ExpandProperty FriendlyName"], text=True, creationflags=0x08000000)
            cams = [line.strip() for line in res.split('\n') if line.strip()]
            if not cams: return ["0: Default Camera"]
            return [f"{i}: {name}" for i, name in enumerate(cams)]
        except:
            return ["0", "1", "2"]

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

    def save_config_combo(self, choice):
        self.save_config()

    def save_config(self):
        try:
            self.config["camera_index"] = int(self.cam_idx_var.get().split(":")[0])
        except Exception:
            self.config["camera_index"] = 0
        self.config["show_camera_feed"] = self.show_cam_var.get()
        self.config["shoulder_guard"] = self.shoulder_var.get()
        self.config["typing_lockout"] = self.typing_var.get()
        self.config["gaze_clutch"] = self.gaze_var.get()
        
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def start_engine(self):
        if self.process is None:
            self.save_config()
            self.start_btn.configure(state="disabled", fg_color=HARD_GRAPHITE_LIGHT, text_color=COOL_GRAY)
            self.stop_btn.configure(state="normal", fg_color="#C0392B", text_color=SOFT_WHITE)
            
            python_exe = sys.executable
            if not getattr(sys, 'frozen', False):
                if os.path.exists("venv/Scripts/python.exe"):
                    python_exe = "venv/Scripts/python.exe"
            
            def run():
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x08000000
                self.process = subprocess.Popen([python_exe, "main.py"], creationflags=flags)
                self.process.wait()
                self.after(0, self.engine_stopped)
                
            threading.Thread(target=run, daemon=True).start()

    def stop_engine(self):
        if self.process is not None:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)], creationflags=0x08000000)
            
    def update_telemetry_loop(self):
        """Poll shared memory for live engine telemetry and downscaled feed."""
        SHM_NAME = "zerotouch_feed_shm"
        SHM_W, SHM_H = 320, 180
        SHM_FRAME_SIZE = SHM_W * SHM_H * 3
        SHM_TOTAL_SIZE = SHM_FRAME_SIZE + 32

        # Connect to SHM if not connected
        if self.shm_client is None:
            try:
                self.shm_client = shm_module.SharedMemory(name=SHM_NAME, create=False, size=SHM_TOTAL_SIZE)
            except Exception:
                self.shm_client = None

        if self.shm_client is not None and self.process is not None:
            try:
                hdr = self.shm_client.buf[:32]
                is_active = hdr[0]
                fps = hdr[1]
                lum = hdr[2]
                low_light = hdr[3]
                gaze_engaged = hdr[4]

                # Update Telemetry Labels
                self.fps_lbl.configure(text=f"FPS: {fps}", text_color="#2ECC71" if fps > 15 else "#E74C3C")
                
                lum_text = f"LUM: {lum} (BOOST)" if low_light else f"LUM: {lum}"
                lum_color = CHAMPAGNE_GOLD if low_light else COOL_GRAY
                self.lum_lbl.configure(text=lum_text, text_color=lum_color)

                if gaze_engaged:
                    self.gaze_pill.configure(text="GAZE: ENGAGED", text_color=CHAMPAGNE_GOLD)
                else:
                    self.gaze_pill.configure(text="GAZE: AWAY", text_color="#E74C3C")

                # If camera feed is toggled ON, update embedded image preview
                if is_active == 1 and self.show_cam_var.get():
                    raw_rgb = bytes(self.shm_client.buf[32:32 + SHM_FRAME_SIZE])
                    img = Image.frombytes("RGB", (SHM_W, SHM_H), raw_rgb)
                    img = img.resize((300, 168), Image.Resampling.NEAREST)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 168))
                    self.preview_canvas.configure(image=ctk_img, text="")
                    self.preview_canvas._current_img = ctk_img # Retain reference
                else:
                    self.preview_canvas.configure(image="", text="[PREVIEW PAUSED]", text_color=COOL_GRAY)
            except Exception:
                # Memory might have unlinked or closed during engine restart
                try:
                    self.shm_client.close()
                except Exception:
                    pass
                self.shm_client = None
        else:
            # Engine not running or shm unavailable
            self.fps_lbl.configure(text="FPS: --", text_color=COOL_GRAY)
            self.lum_lbl.configure(text="LUM: --", text_color=COOL_GRAY)
            self.gaze_pill.configure(text="GAZE: STANDBY", text_color=COOL_GRAY)
            self.preview_canvas.configure(image="", text="ENGINE OFFLINE" if self.process is None else "INITIALIZING...", text_color=COOL_GRAY)

        # Schedule next refresh at ~25-30 fps for smooth, lightweight UI response
        self.after(35, self.update_telemetry_loop)

    def engine_stopped(self):
        self.process = None
        if self.shm_client is not None:
            try:
                self.shm_client.close()
            except Exception:
                pass
            self.shm_client = None
        self.start_btn.configure(state="normal", fg_color=CHAMPAGNE_GOLD, text_color=MIDNIGHT_INK)
        self.stop_btn.configure(state="disabled", fg_color=HARD_GRAPHITE_LIGHT, text_color=SOFT_WHITE)
        self.fps_lbl.configure(text="FPS: --", text_color=COOL_GRAY)
        self.lum_lbl.configure(text="LUM: --", text_color=COOL_GRAY)
        self.gaze_pill.configure(text="GAZE: STANDBY", text_color=COOL_GRAY)
        self.preview_canvas.configure(image="", text="ENGINE OFFLINE", text_color=COOL_GRAY)

    # --- System Tray Logic ---
    def setup_tray(self):
        tray_image = create_tray_icon_image()
        menu = (
            item('Show ZeroTouch', self.show_window, default=True),
            item('Toggle Engine', self.toggle_engine_from_tray),
            item('Quit Completely', self.quit_app)
        )
        self.tray_icon = pystray.Icon("ZeroTouch", tray_image, "ZeroTouch OS", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def hide_to_tray(self):
        self.withdraw()

    def show_window(self, icon=None, item=None):
        self.after(0, self._restore_window)

    def _restore_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def toggle_engine_from_tray(self, icon=None, item=None):
        if self.process is None:
            self.after(0, self.start_engine)
        else:
            self.after(0, self.stop_engine)

    def quit_app(self, icon=None, item=None):
        self.stop_engine()
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = ZeroTouchWidget()
    app.mainloop()
