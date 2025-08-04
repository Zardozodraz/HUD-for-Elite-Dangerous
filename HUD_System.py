import os
import sys
import json
import time
import ctypes
import threading
import tkinter as tk
from pathlib import Path
import requests
from string import ascii_uppercase

import Language # Language file
lang = "english"

interesting_keywords = [
    "White Dwarf", "Neutron", "Black", "Ammonia", "Water",
    "O (Blue-White)", "Herbig Ae/Be", "Wolf-Rayet",
    "CN", "CJ", "MS", "S-type", "Helium", "Class V", "Earth-like"
] # Add other key-words if necessary :
"High metal content world"
"Rocky body"
"Icy body"
"Rocky Ice world"

# ==================================== HUD ====================================
class SystemHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HUD System")
        self.root.geometry("500x100+10+10")
        self.root.configure(bg="black")
        self.root.wm_attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.wm_attributes("-transparentcolor", "black")
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

    def make_click_through(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)

    def update(self, system, body_list):
        text_content = f"{Language.languages[lang]["HUD_System"]["System"]} : {system}\n"

        if body_list:
            flat_line = " • ".join(body_list) # On sépare les corps par " • "
            max_chars = 100

            if len(flat_line) <= max_chars:
                text_content += flat_line
            else:
                # Essayer de couper à un " • " avant max_chars
                split_index = flat_line.rfind(" • ", 0, max_chars)
                if split_index == -1:
                    # Si aucun " • " trouvé avant max_chars, chercher le dernier espace
                    split_index = flat_line.rfind(" ", 0, max_chars)
                if split_index == -1:
                    # Si aucun espace non plus, forcer une coupure brutale
                    split_index = max_chars

                # On découpe sans inclure le séparateur si trouvé
                line1 = flat_line[:split_index].strip()
                line2 = flat_line[split_index:].lstrip(" • ")  # Supprime les espaces et séparateurs inutiles à la fin
                text_content += line1 + "\n" + line2
        else:
            text_content += Language.languages[lang]["HUD_System"]["No_interesting_body"]

        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text_content)
        self.text.config(state="disabled")

    def run(self):
        self.root.mainloop()

# ==================================== RÉCUPÉRATION DES DONNÉES ====================================
def get_body_types(system_name):
    url = "https://www.edsm.net/api-system-v1/bodies"
    params = {"systemName": system_name, "showBodies": True}
    response = requests.get(url, params=params)
    #print("Request sent")
    response.raise_for_status()
    data = response.json()

    types = []
    interesting_type = []
    for body in data.get("bodies", []):
        b_type = body.get("type")
        b_subtype = body.get("subType")
        types.append(f"{b_type} - {b_subtype}")

        if any(keyword in b_subtype for keyword in interesting_keywords):
            interesting_type.append(b_subtype)
    #print(types)
    #print(interesting_type)

    return interesting_type

def find_latest_journal():
    # Recherche sur tous les disques montés (Windows uniquement)
    candidate_dirs = []
    for drive_letter in ascii_uppercase:
        root = Path(f"{drive_letter}:\\") # Exemple : C:\, D:\, ...
        test_path = root / "Users" # Vérifie s'il existe un dossier "Users"
        if test_path.exists():
            for user_dir in test_path.iterdir(): # Parcours de tous les dossiers utilisateurs trouvés
                journal_dir = user_dir / "Saved Games" / "Frontier Developments" / "Elite Dangerous" # Construit le chemin vers le journal pour chaque utilisateur
                if journal_dir.exists():
                    candidate_dirs.append(journal_dir) # Si le dossier existe, on l’ajoute à la liste des candidats

    journal_files = []
    for d in candidate_dirs: # Rassemble tous les fichiers Journal .log dans chaque dossier candidat
        journal_files += list(d.glob("Journal.*.log"))

    if not journal_files: # Si aucun fichier journal n’a été trouvé, on lève une erreur
        raise FileNotFoundError("No Elite Dangerous log files found.")

    latest_file = max(journal_files, key=os.path.getmtime) # Retourne le fichier le plus récent (le dernier modifié)
    return latest_file

# ==================================== SURVEILLANCE DU JOURNAL ====================================
def monitor_journal(hud: SystemHUD):
    last_system = None
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
                if data.get("event") == "FSDJump":
                    system = data.get("StarSystem", "Inconnu")
                    if system != last_system:
                        last_system = system
                        #print(f"[SYSTÈME] {system}")

                        try:
                            interesting = get_body_types(system)
                            hud.update(system, interesting)
                        except Exception as e:
                            hud.update(system, [f"Error: {e}"])
            except json.JSONDecodeError:
                continue

# ==================================== MAIN ====================================
def main():
    global lang
    
    # Lecture d'un argument eventuel passé par le launcher
    if len(sys.argv) > 1:
        lang = sys.argv[1]
    
    hud = SystemHUD()
    threading.Thread(target=monitor_journal, args=(hud,), daemon=True).start()
    
    hud.update("", "")
    hud.run()

if __name__ == "__main__":
    main()
