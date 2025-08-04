import os
import time
import json
import ctypes
import tkinter as tk
from string import ascii_uppercase
from pathlib import Path
from datetime import datetime
import threading

import Language # Language file
lang = "english"

# ====================== HUD DE STATS ======================

class SessionHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HUD Session")
        self.root.geometry("200x150+1710+10")
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
            "buy": 0,
            "sell": 0,
            "kills": 0,
            "distance": 0.0,
            "jumps": 0,
            "bounty": 0,
            "codex": 0,
            "ExplorationData": 0,
        }

    def make_click_through(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)

    def update(self):
        duration = datetime.utcnow() - self.session_start
        text_content = (
            f"{Language.languages[lang]["HUD_SessionStats"]["Kills"]} : {self.stats['kills']}\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Distance"]} : {self.stats['distance']:.2f} AL\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Jumps"]} : {self.stats['jumps']} \n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Bounty"]} : {self.stats['bounty']} cr\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Sell"]} : {self.stats['sell']} cr\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Buy"]} : {self.stats['buy']} cr\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Codex"]} : {self.stats['codex']}\n"
            f"{Language.languages[lang]["HUD_SessionStats"]["Exploration"]} : {self.stats['ExplorationData']}\n"

            f"{Language.languages[lang]["HUD_SessionStats"]["Session"]} : {str(duration).split('.')[0]}\n"
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
        raise FileNotFoundError("No Elite Dangerous log files found.")

    latest_file = max(journal_files, key=os.path.getmtime)
    return latest_file

def monitor_session(hud: SessionHUD):
    journal_path = find_latest_journal()
    print(f"[INFO] Reading journal : {journal_path}")

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
                    hud.stats["bounty"] += data.get("TotalReward")
                    hud.stats["kills"] += 1
                
                elif event == "PVPKill":
                    hud.stats["kills"] += 1

                elif event == "FSDJump":
                    hud.stats["distance"] += data.get("JumpDist", 0.0)
                    hud.stats["jumps"] += 1

                elif event == "MarketBuy":
                    hud.stats["buy"] += data.get("TotalCost")

                elif event == "MarketSell":
                    hud.stats["sell"] += data.get("TotalSale")
                
                elif event == "BuyTradeData" or event == "BuyExplorationData":
                    hud.stats["buy"] += data.get("Cost")
                
                elif event == "CodexEntry":
                    hud.stats["codex"] += 1
                
                elif event == "MultiSellExplorationData":
                    hud.stats["ExplorationData"] += data.get("TotalEarnings")

                hud.update()

            except json.JSONDecodeError:
                continue

# ====================== LANCEMENT ======================

def update_loop(hud: SessionHUD):
    while True:
        hud.update()
        time.sleep(1)  # met à jour toutes les secondes

if __name__ == "__main__":
    hud = SessionHUD()

    threading.Thread(target=monitor_session, args=(hud,), daemon=True).start()
    threading.Thread(target=update_loop, args=(hud,), daemon=True).start()

    hud.run()
