import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os
import sys
import json

CONFIG_FILE = "config.json"

class AeroLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Aero - Zero-Touch OS")
        self.root.geometry("450x450")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        # Load Config
        self.config = {
            "camera_index": 0,
            "show_camera_feed": True,
            "shoulder_guard": True,
            "typing_lockout": True
        }
        self.load_config()
        
        # UI Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=8, font=("Segoe UI", 11, "bold"))
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#00a8ff")
        style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[10, 5], font=("Segoe UI", 10, "bold"))
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Dashboard
        self.tab_dashboard = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.tab_dashboard, text=" Dashboard ")
        
        ttk.Label(self.tab_dashboard, text="A E R O", style="Header.TLabel").pack(pady=(30, 5))
        ttk.Label(self.tab_dashboard, text="Zero-Touch Spatial OS Engine").pack(pady=(0, 30))
        
        self.status_var = tk.StringVar(value="Status: Standby")
        self.status_label = ttk.Label(self.tab_dashboard, textvariable=self.status_var, font=("Segoe UI", 10, "italic"))
        self.status_label.pack(pady=10)
        
        self.start_btn = ttk.Button(self.tab_dashboard, text="▶ START ENGINE", command=self.start_engine)
        self.start_btn.pack(fill=tk.X, padx=50, pady=5)
        
        self.stop_btn = ttk.Button(self.tab_dashboard, text="⬛ STOP ENGINE", command=self.stop_engine, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, padx=50, pady=5)
        
        # Tab 2: Settings
        self.tab_settings = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.tab_settings, text=" Settings ")
        
        self.build_settings_tab()
        
        self.process = None

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

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

    def build_settings_tab(self):
        ttk.Label(self.tab_settings, text="Camera Index:").pack(anchor=tk.W, padx=20, pady=(20, 5))
        self.cam_idx_var = tk.StringVar(value=str(self.config["camera_index"]))
        ttk.Spinbox(self.tab_settings, from_=0, to=10, textvariable=self.cam_idx_var, width=5).pack(anchor=tk.W, padx=20)
        
        self.show_cam_var = tk.BooleanVar(value=self.config["show_camera_feed"])
        ttk.Checkbutton(self.tab_settings, text="Show Camera Feed (Debug Window)", variable=self.show_cam_var).pack(anchor=tk.W, padx=20, pady=10)
        
        self.shoulder_var = tk.BooleanVar(value=self.config["shoulder_guard"])
        ttk.Checkbutton(self.tab_settings, text="Enable ShoulderGuard (Privacy Shield)", variable=self.shoulder_var).pack(anchor=tk.W, padx=20, pady=10)
        
        self.typing_var = tk.BooleanVar(value=self.config["typing_lockout"])
        ttk.Checkbutton(self.tab_settings, text="Enable Smart Typing Lockout", variable=self.typing_var).pack(anchor=tk.W, padx=20, pady=10)
        
        ttk.Button(self.tab_settings, text="Save Settings", command=self.save_config).pack(fill=tk.X, padx=50, pady=30)

    def start_engine(self):
        if self.process is None:
            self.save_config() # Always ensure latest settings are written before boot
            self.status_var.set("Status: Running...")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            python_exe = sys.executable
            if not getattr(sys, 'frozen', False):
                if os.path.exists("venv/Scripts/python.exe"):
                    python_exe = "venv/Scripts/python.exe"
            
            def run():
                self.process = subprocess.Popen([python_exe, "main.py"], 
                                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.process.wait()
                self.root.after(0, self.engine_stopped)
                
            threading.Thread(target=run, daemon=True).start()

    def stop_engine(self):
        if self.process is not None:
            self.status_var.set("Status: Stopping...")
            import signal
            os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
            
    def engine_stopped(self):
        self.process = None
        self.status_var.set("Status: Standby")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AeroLauncher(root)
    root.mainloop()
