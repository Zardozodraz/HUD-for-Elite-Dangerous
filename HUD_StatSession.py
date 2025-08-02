import os
import time
import json
import ctypes
import tkinter as tk
from string import ascii_uppercase
from pathlib import Path
from datetime import datetime

# ====================== HUD DE STATS ======================

class SessionHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HUD Session")
        self.root.geometry("300x150+1610+10")
        self.root.configure(bg="black")
        self.root.wm_attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        #self.root.wm_attributes("-transparentcolor", "black")
        self.root.overrideredirect(True)

        self.text = tk.Text(
            self.root,
            fg="lime",
            bg="black",
            font=("Consolas", 12, "bold"),
            wrap="word",
            state="disabled",
            borderwidth=0,
            highlightthickness=0
        )
        self.text.pack(fill="both", expand=True)

        self.make_click_through()
        self.session_start = datetime.utcnow()
        self.stats = {
            "credits": 0,
            "kills": 0,
            "distance": 0.0,
            "jumps": 0,
        }

    def make_click_through(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)

    def update(self):
        duration = datetime.utcnow() - self.session_start
        text_content = (            
            f"🤑 Crédits : {self.stats['credits']:,} cr\n"
            f"☠️ Kills : {self.stats['kills']}\n"
            f"🚀 Distance : {self.stats['distance']:.2f} AL\n"
            f"🧭 Sauts : {self.stats['jumps']}"
            f"⏱️ Session : {str(duration).split('.')[0]}\n"
        )

        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text_content)
        self.text.config(state="disabled")

    def run(self):
        self.root.mainloop()

# ====================== JOURNAL ======================

def find_latest_journal():
    candidate_dirs = []
    for drive_letter in ascii_uppercase:
        root = Path(f"{drive_letter}:\\")
        test_path = root / "Users"
        if test_path.exists():
            for user_dir in test_path.iterdir():
                journal_dir = user_dir / "Saved Games" / "Frontier Developments" / "Elite Dangerous"
                if journal_dir.exists():
                    candidate_dirs.append(journal_dir)

    journal_files = []
    for d in candidate_dirs:
        journal_files += list(d.glob("Journal.*.log"))

    if not journal_files:
        raise FileNotFoundError("Aucun fichier journal Elite Dangerous trouvé.")

    latest_file = max(journal_files, key=os.path.getmtime)
    return latest_file

def monitor_session(hud: SessionHUD):
    journal_path = find_latest_journal()
    print(f"[INFO] Lecture du journal : {journal_path}")

    with open(journal_path, 'r', encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            try:
                data = json.loads(line)
                event = data.get("event")

                if event == "Bounty":
                    reward = sum(e.get("Reward", 0) for e in data.get("Rewards", []))
                    hud.stats["credits"] += reward
                    hud.stats["kills"] += 1

                elif event == "FSDJump":
                    hud.stats["distance"] += data.get("JumpDist", 0.0)
                    hud.stats["jumps"] += 1

                hud.update()

            except json.JSONDecodeError:
                continue

# ====================== LANCEMENT ======================

if __name__ == "__main__":
    hud = SessionHUD()

    import threading
    t = threading.Thread(target=monitor_session, args=(hud,), daemon=True)
    t.start()

    hud.run()
