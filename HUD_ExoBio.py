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

interesting_keywords = [ # Penser à enlever "Thin ", "Thick " et "Hot " dans le resultats des requètes
    ("Carbon dioxyde", "High metal content world", [("Aleolda x2", "7M"), ("Osseus", "7M"), ("Tubus", "7M"), ("Clypeus x3", "7M-15M"), ("Stratum", "15M")]),
    ("Carbon dioxide-rich", "High metal content world", [("Aleolda x2", "7M"), ("Osseus", "7M"), ("Tubus", "7M"), ("Clypeus x3", "7M-15M"), ("Stratum", "15M")]),
    
    ("Ammonia", "High metal content world", [("Concha", "7M"), ("Tubus", "7M"), ("Stratum", "15M")]),
    ("Ammonia-rich", "High metal content world", [("Concha", "7M"), ("Tubus", "7M"), ("Stratum", "15M")]),
    
    ("Ammonia", "Rocky body", [("Concha", "7M"), ("Frutexa", "7M"), ("Tubus", "7M")]),
    ("Ammonia-rich", "Rocky body", [("Concha", "7M"), ("Frutexa", "7M"), ("Tubus", "7M")]),
    
    ("Water", "Rocky body", [("Cactoida", "15M"), ("Clypeus x3", "7M-15M"), ("Osseus", "7M"), ("Tussock", "7M")]),
    ("Water-rich", "Rocky body", [("Cactoida", "15M"), ("Clypeus x3", "7M-15M"), ("Osseus", "7M"), ("Tussock", "7M")]),
    
    ("Water", "High metal content world", [("Cactoida", "15M"), ("Clypeus x3", "7M-15M"), ("Osseus", "7M"), ("Stratum", "15M")]),
    ("Water-rich", "High metal content world", [("Cactoida", "15M"), ("Clypeus x3", "7M-15M"), ("Osseus", "7M"), ("Stratum", "15M")]),
    
    ("Nitrogen", None, [("Concha", "15M"), ("Bacterium", "7M")]),
    
    ("Carbon dioxyde", "Rocky body", [("Frutexa", "7M"), ("Aleolda x2", "7M"), ("Osseus", "7M"), ("Tussock", "7M"), ("Clypeus x2", "7M"), ("Stratum", "15M")]),
    ("Carbon dioxide-rich", "Rocky body", [("Frutexa", "7M"), ("Aleolda x2", "7M"), ("Osseus", "7M"), ("Tussock", "7M"), ("Clypeus x2", "7M"), ("Stratum", "15M")]),
    
    ("Argon", None, [("Tussock", "7M")]),
    ("Argon-rich", None, [("Tussock", "7M")]),
    
    #("Helium", None, [("", "")]),
    
    ("Neon", None, [("Fonticulua", "15M")]),
    ("Neon-rich", None, [("Fonticulua", "15M")]),
    
    ("Methane", None, [("Tussock", "7M"), ("Bacterium", "7M")]),
    ("Methane-rich", None, [("Tussock", "7M"), ("Bacterium", "7M")]),
    
    ("Oxygen", None, [("Fonticulua", "15M"), ("Bacterium", "7M"), ("Stratum", "15M")]),
    
    ("Sulphur dioxide", "Rocky body", [("Recepta x2", "7M-15M"), ("Tussock", "15M"), ("Stratum", "15M")]),
    ("Sulphur dioxide", "High metal content world", [("Recepta", "7M-15M"), ("Stratum", "15M")]),
    ("Sulphur dioxide", "Icy body", [("Recepta", "7M")]),
    ("Sulphur dioxide", "Rocky Ice world", [("Recepta x2", "7M")]),
    
    #("Suitable for water-based life", None, [("", "")])
]

# ==================================== HUD ====================================
class ExoBioHUD:
    def __init__(self, fenetreDecalee="False"):
        self.root = tk.Tk()
        self.root.title("HUD Exo-Biology")
        self.root.geometry("500x500+10+10")
        self.root.configure(bg="black")
        self.root.wm_attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.overrideredirect(True)
        
        if fenetreDecalee == "True": # si le HUD des systèmes est lancé (avant)
            self.root.geometry("500x500+10+120")

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

    def update(self, system, body_list, docked, use_save):
        global lang
        
        if not docked:
            text_content = f"{Language.languages[lang]["HUD_ExoBio"]["Exo_Biology"]} : {system}\n"

            if body_list:
                # Une ligne par corps : Atmosphère, Type, Nom
                for b in body_list:
                    vie = ""
                    for i in range(len(b[3])):
                        nom, valeur = b[3][i]
                        vie += f"{nom} ({valeur}) • "
                        vieFormat = vie.strip(" • ")
                    lines = [f"{b[0]}, {b[1]}, {b[2]}, {vieFormat}\n"] # Format : "Atmosphère, Type, Nom, Vie (valeur)"
                    text_content += "\n".join(lines)
            else:
                text_content += Language.languages[lang]["HUD_ExoBio"]["No_interesting_body"]
            
            text_content_sauvegarde = text_content
        
        if use_save:
            self.text.config(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", text_content_sauvegarde)
            self.text.config(state="disabled")
        elif docked:
            text_content = "Docké."
            self.text.config(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", text_content)
            self.text.config(state="disabled")
        else:
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
        if b_type == "Planet":
            b_subtype = body.get("subType")
            b_atmosphereType = body.get("atmosphereType").replace("Thin ", "").replace("Thick ", "").replace("thick ", "").replace("Hot ", "")
            is_landable = body.get("isLandable")
            b_name = body.get("name").replace(system_name + " ", "")
            
            if is_landable:
                temp = (b_atmosphereType, b_subtype, b_name)
                types.append(temp)
                
                for i in range(len(interesting_keywords)):
                    if temp[0] == interesting_keywords[i][0]:
                        if temp[1] == interesting_keywords[i][1] or interesting_keywords[i][1] is None:
                            temp = (b_atmosphereType, b_subtype, b_name, interesting_keywords[i][2]) # ajout des noms des vie intéressants
                            interesting_type.append(temp)
                            break
    
    """print(types)
    if interesting_type:
        print(interesting_type)
    else:
        print("Aucun corps intéressant/atterrissable trouvé.")
    print("")"""

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
def monitor_journal(hud: ExoBioHUD):
    last_system = None
    journal_path = find_latest_journal()
    print(f"[INFO] Reading journal : {journal_path}")

    with open(journal_path, 'r', encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)
        
        docked = False

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            try:
                data = json.loads(line)
                
                if data.get("event") == "Docked":
                    docked = True
                    hud.update("", [], docked, use_save=False)
                if data.get("event") == "Undocked":
                    docked = False
                    hud.update("", [], docked, use_save=True)
                
                if data.get("event") == "FSDJump":
                    system = data.get("StarSystem", "Inconnu")
                    if system != last_system:
                        last_system = system
                        #print(f"[SYSTÈME] {system}")

                        try:
                            interesting = get_body_types(system)
                            hud.update(system, interesting, docked, use_save=True)
                        except Exception as e:
                            hud.update(system, [f"Error: {e}"])
                
                    
            except json.JSONDecodeError:
                continue

# ==================================== MAIN ====================================
def main():
    fenetreDecalee = False

    # Lecture d'un argument eventuel passé par le launcher
    if len(sys.argv) > 1:
        fenetreDecalee = sys.argv[1]
        print(f"[HUD-ExoBio] HUD System running : Recieved value : {fenetreDecalee}")
        
    hud = ExoBioHUD(fenetreDecalee)
    threading.Thread(target=monitor_journal, args=(hud,), daemon=True).start()
    
    hud.update("", "", "", "")
    hud.run()

if __name__ == "__main__":
    main()
