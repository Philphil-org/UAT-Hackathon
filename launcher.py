import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import os
import sys

class AeroLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Aero - Zero-Touch OS")
        self.root.geometry("400x350")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        # Make it look somewhat modern
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=10, font=("Segoe UI", 12, "bold"))
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#00a8ff")
        
        # Header
        ttk.Label(root, text="A E R O", style="Header.TLabel").pack(pady=(30, 5))
        ttk.Label(root, text="Zero-Touch Spatial OS Engine").pack(pady=(0, 30))
        
        # Status Label
        self.status_var = tk.StringVar(value="Status: Standby")
        self.status_label = ttk.Label(root, textvariable=self.status_var, font=("Segoe UI", 10, "italic"))
        self.status_label.pack(pady=10)
        
        # Buttons
        self.start_btn = ttk.Button(root, text="▶ START ENGINE", command=self.start_engine)
        self.start_btn.pack(fill=tk.X, padx=50, pady=5)
        
        self.stop_btn = ttk.Button(root, text="⬛ STOP ENGINE", command=self.stop_engine, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, padx=50, pady=5)
        
        self.process = None

    def start_engine(self):
        if self.process is None:
            self.status_var.set("Status: Running...")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Determine correct python executable depending on if we are bundled or in venv
            python_exe = sys.executable
            # If running from source, prefer venv
            if not getattr(sys, 'frozen', False):
                if os.path.exists("venv/Scripts/python.exe"):
                    python_exe = "venv/Scripts/python.exe"
            
            # Start main.py in a background thread to prevent GUI freezing
            def run():
                self.process = subprocess.Popen([python_exe, "main.py"], 
                                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.process.wait()
                self.root.after(0, self.engine_stopped)
                
            threading.Thread(target=run, daemon=True).start()

    def stop_engine(self):
        if self.process is not None:
            self.status_var.set("Status: Stopping...")
            # Send terminate signal
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
