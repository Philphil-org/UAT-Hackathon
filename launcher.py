import customtkinter as ctk
import subprocess
import threading
import os
import sys
import json

CONFIG_FILE = "config.json"

# Brand Palette (ZeroTouch Spec)
MIDNIGHT_INK = "#0F0F14"
HARD_GRAPHITE = "#181820"
HARD_GRAPHITE_LIGHT = "#22222C"
CHAMPAGNE_GOLD = "#D4AF6A"
SLATE_BLUE = "#4A6FA5"
SOFT_WHITE = "#F2EFE9"
COOL_GRAY = "#8A8D93"

class AeroLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZeroTouch OS")
        self.geometry("750x480")
        self.configure(fg_color=MIDNIGHT_INK)
        self.resizable(False, False)
        
        # Load Config
        self.config = {
            "camera_index": 0,
            "show_camera_feed": True,
            "shoulder_guard": True,
            "typing_lockout": True
        }
        self.load_config()
        self.process = None

        # Fonts
        self.font_brand = ctk.CTkFont(family="Georgia", size=36, weight="bold", slant="italic")
        self.font_primary = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.font_secondary = ctk.CTkFont(family="Segoe UI", size=12)
        self.font_telemetry = ctk.CTkFont(family="Consolas", size=11, weight="bold")

        # Grid layout (2 columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT PANE: MATRIX MAPPER / SETTINGS ---
        self.left_pane = ctk.CTkFrame(self, fg_color=HARD_GRAPHITE, corner_radius=0)
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        # Brand Header
        self.brand_lbl = ctk.CTkLabel(self.left_pane, text="ZeroTouch", font=self.font_brand, text_color=CHAMPAGNE_GOLD)
        self.brand_lbl.pack(pady=(40, 0), padx=30, anchor="w")
        
        self.sub_lbl = ctk.CTkLabel(self.left_pane, text="SPATIAL OS ENGINE", font=self.font_telemetry, text_color=COOL_GRAY)
        self.sub_lbl.pack(pady=(0, 30), padx=33, anchor="w")

        # Switches / Settings
        self.show_cam_var = ctk.BooleanVar(value=self.config["show_camera_feed"])
        self.sw1 = ctk.CTkSwitch(self.left_pane, text="Debug Camera Feed", font=self.font_primary, text_color=SOFT_WHITE, 
                                 variable=self.show_cam_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw1.pack(pady=15, padx=30, anchor="w")

        self.shoulder_var = ctk.BooleanVar(value=self.config["shoulder_guard"])
        self.sw2 = ctk.CTkSwitch(self.left_pane, text="ShoulderGuard™", font=self.font_primary, text_color=SOFT_WHITE, 
                                 variable=self.shoulder_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw2.pack(pady=15, padx=30, anchor="w")

        self.typing_var = ctk.BooleanVar(value=self.config["typing_lockout"])
        self.sw3 = ctk.CTkSwitch(self.left_pane, text="Smart Typing Lockout", font=self.font_primary, text_color=SOFT_WHITE, 
                                 variable=self.typing_var, progress_color=CHAMPAGNE_GOLD, button_color=SOFT_WHITE, button_hover_color=COOL_GRAY, command=self.save_config)
        self.sw3.pack(pady=15, padx=30, anchor="w")
        
        ctk.CTkLabel(self.left_pane, text="CAMERA HARDWARE INDEX", font=self.font_telemetry, text_color=COOL_GRAY).pack(pady=(30,0), padx=30, anchor="w")
        self.cam_idx_var = ctk.StringVar(value=str(self.config["camera_index"]))
        self.cam_combo = ctk.CTkOptionMenu(self.left_pane, values=["0", "1", "2"], variable=self.cam_idx_var, fg_color=HARD_GRAPHITE_LIGHT, button_color=SLATE_BLUE, font=self.font_primary, text_color=SOFT_WHITE, command=self.save_config_combo)
        self.cam_combo.pack(pady=10, padx=30, anchor="w")

        # Trust Badge
        self.badge = ctk.CTkLabel(self.left_pane, text="🔒 OPTICAL INFERENCING IN LOCAL RAM\nZERO FRAMES WRITTEN TO DISK", font=self.font_telemetry, text_color=SLATE_BLUE, justify="left")
        self.badge.pack(side="bottom", pady=30, padx=30, anchor="w")

        # --- RIGHT PANE: CALIBRATION & LAUNCH ---
        self.right_pane = ctk.CTkFrame(self, fg_color=MIDNIGHT_INK, corner_radius=0)
        self.right_pane.grid(row=0, column=1, sticky="nsew")

        # Telemetry UI Box
        self.telemetry_box = ctk.CTkFrame(self.right_pane, fg_color=HARD_GRAPHITE, corner_radius=8, border_width=1, border_color=SLATE_BLUE)
        self.telemetry_box.pack(pady=40, padx=30, fill="x")
        
        self.status_lbl = ctk.CTkLabel(self.telemetry_box, text="ENGINE STATUS: DORMANT", font=self.font_telemetry, text_color=COOL_GRAY)
        self.status_lbl.pack(pady=(15, 5), padx=20, anchor="w")

        self.console_text = ctk.CTkTextbox(self.telemetry_box, height=120, fg_color=MIDNIGHT_INK, text_color=SLATE_BLUE, font=self.font_telemetry)
        self.console_text.pack(pady=(0, 15), padx=15, fill="x")
        self.console_text.insert("0.0", "Awaiting execution command...\nReady to bind hardware hooks.\n")
        self.console_text.configure(state="disabled")

        # Launch Buttons
        self.start_btn = ctk.CTkButton(self.right_pane, text="INITIALIZE ZERO-TOUCH", font=self.font_primary, 
                                       fg_color=CHAMPAGNE_GOLD, text_color=MIDNIGHT_INK, hover_color="#B59350",
                                       height=45, command=self.start_engine)
        self.start_btn.pack(pady=10, padx=30, fill="x")

        self.stop_btn = ctk.CTkButton(self.right_pane, text="TERMINATE ENGINE", font=self.font_primary, 
                                      fg_color=HARD_GRAPHITE_LIGHT, text_color=SOFT_WHITE, hover_color="#333344",
                                      height=45, state="disabled", command=self.stop_engine)
        self.stop_btn.pack(pady=10, padx=30, fill="x")

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
        self.config["camera_index"] = int(self.cam_idx_var.get())
        self.config["show_camera_feed"] = self.show_cam_var.get()
        self.config["shoulder_guard"] = self.shoulder_var.get()
        self.config["typing_lockout"] = self.typing_var.get()
        
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def log(self, text):
        self.console_text.configure(state="normal")
        self.console_text.insert("end", text + "\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def start_engine(self):
        if self.process is None:
            self.save_config()
            self.status_lbl.configure(text="ENGINE STATUS: ENGAGED", text_color=CHAMPAGNE_GOLD)
            self.log("> Binding spatial hooks...")
            self.log("> Warming up TensorFlow Lite models...")
            
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            
            python_exe = sys.executable
            if not getattr(sys, 'frozen', False):
                if os.path.exists("venv/Scripts/python.exe"):
                    python_exe = "venv/Scripts/python.exe"
            
            def run():
                self.process = subprocess.Popen([python_exe, "main.py"], 
                                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.process.wait()
                self.after(0, self.engine_stopped)
                
            threading.Thread(target=run, daemon=True).start()
            self.log("> ZeroTouch Core running in background.")

    def stop_engine(self):
        if self.process is not None:
            self.status_lbl.configure(text="ENGINE STATUS: TERMINATING", text_color=COOL_GRAY)
            self.log("> Terminating daemon...")
            import signal
            os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
            
    def engine_stopped(self):
        self.process = None
        self.status_lbl.configure(text="ENGINE STATUS: DORMANT", text_color=COOL_GRAY)
        self.log("> Engine halted successfully.")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    app = AeroLauncher()
    app.mainloop()
