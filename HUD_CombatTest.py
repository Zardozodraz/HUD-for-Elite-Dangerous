"""
SYSTEME DE DECISION RAPIDE :
ANALYSE LE JOURNAL ET EXTRAIT LES INFORMATIONS REQUISES POUR LE HUD DE COMBAT.

TRAITE LES INFO POUR DEFINIR LE NIVEAU DE DANGER :
ANALYSE LES DEGATS AU BOUCLIER, A LA COQUE, AUX MODULES DU JOUEUR ET ENNEMIS
COMPTE LE NOMBRE D'ENNEMIS ET LEURS RANGS DE COMBAT
CALCULE LA VITESSE DE DESTRUCTION DES BOUCLIERS ET DE LA COQUE JOUEUR ET ENNEMIS : Δ% / Δt
Si la vitesse de destruction des boucliers ou de la coque est supérieure à un seuil, le HUD affiche un message d'alerte.

Faire un calcul pondéré en fonction de toutes les info : (à ajuster)
Joueur : degat au bouclier = *0.5, degat à la coque = *0.7, degat aux modules = *0.3
Ennemis : degat au bouclier = *0.5, degat à la coque = *0.7, degat aux modules = *0.3, nombre d'ennemis = *0.4, rang de combat = *0.8

On obtient un score de danger global qui est affiché sur le HUD.
AFFICHE LE NIVEAU DE DANGER SUR LE HUD
"""

import os
import json
import time
import ctypes
import threading
import tkinter as tk
from pathlib import Path
from string import ascii_uppercase

ListVaisseaux = []  # Liste globale pour stocker les vaisseaux détectés

class Vaisseau:
    def __init__(self, nom_cible, PilotRank, ShieldHealth, HullHealth, ship_type, bounty):
        self.nom = nom_cible
        self.PilotRank = PilotRank
        self.ShieldHealth = ShieldHealth
        self.HullHealth = HullHealth
        self.ship_type = ship_type
        self.bounty = bounty

    def __str__(self):
        return f"{self.nom} ({self.PilotRank}), Bouclier: {self.ShieldHealth}, Coque: {self.HullHealth}, Type: {self.ship_type}, Bounty: {self.bounty}"

class Joueur:
    def __init__(self, hull_health, shield_up):
        self.hull_health = hull_health
        self.shield_up = shield_up # bool

    def __str__(self):
        return f"Joueur - Santé: {self.hull_health}, Bouclier: {'Actif' if self.shield_up else 'Inactif'}"

joueur = Joueur(1, True)  # Initialisation du joueur avec des valeurs par défaut

# ==================================== HUD ====================================
class CombatHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HUD Combat")
        self.root.geometry("500x100+1620+10")
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

    def update(self, bounty):
        text_content = f"Bounty : {bounty}\n"

        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text_content)
        self.text.config(state="disabled")

    def run(self):
        self.root.mainloop()

# ==================================== Journal ====================================

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
        raise FileNotFoundError("Aucun fichier journal Elite Dangerous trouvé sur les disques.")

    latest_file = max(journal_files, key=os.path.getmtime) # Retourne le fichier le plus récent (le dernier modifié)

    return latest_file

# ==================================== MAJ VAISSEAUX ====================================

def maj_vaiseaux(nom_cible, PilotRank, ShieldHealth, HullHealth, ship_type, bounty):
    global ListVaisseaux
    is_modified = False
    # Fonction pour créer un vaisseau à partir des données du journal
    for i in range(len(ListVaisseaux)):
        if ListVaisseaux[i].nom == nom_cible:
            # Si le vaisseau existe déjà, on met à jour ses informations
            ListVaisseaux[i].PilotRank = PilotRank
            ListVaisseaux[i].ShieldHealth = ShieldHealth
            ListVaisseaux[i].HullHealth = HullHealth
            ListVaisseaux[i].ship_type = ship_type
            ListVaisseaux[i].bounty = bounty
            is_modified = True
            print(f"Vaisseau mis à jour : {ListVaisseaux[i]}")
        
    if not is_modified:
        # Si le vaisseau n'existe pas, on le crée et l'ajoute à la liste
        vaisseau = Vaisseau(nom_cible, PilotRank, ShieldHealth, HullHealth, ship_type, bounty)
        ListVaisseaux.append(vaisseau)
        print(f"Nouveau vaisseau détecté : {nom_cible} ({PilotRank}), Bouclier: {ShieldHealth}, Coque: {HullHealth}, Type: {ship_type}, Bounty: {bounty}")

def maj_joueur(hull_health, shield_up):
    # Fonction pour mettre à jour les informations du joueur
    global joueur
    joueur.hull_health = hull_health
    joueur.shield_up = shield_up
    print(f"Joueur mis à jour : {joueur}")

# ==================================== TRAITEMENT ====================================

def traitement(nom_cible, rang_cible, degat_bouclier, degat_coque, degat_modules):
    # Fonction de traitement des données du journal
    
    pass

# ==================================== SURVEILLANCE DU JOURNAL ====================================
def monitor_journal(hud: CombatHUD):
    journal_path = find_latest_journal()
    print(f"[INFO] Lecture du journal : {journal_path}")
    
    ship_type = ""
    nom_cible = ""
    PilotRank = ""
    ShieldHealth = 0
    HullHealth = 0
    bounty = 0
    time_stamp = ""
    
    player_hull_health = 1 # Valeur par défaut pour la santé du joueur
    shield_up = True
    
    maj_vaisseau_ennemis = False
    maj_vaisseau_joueur = False

    with open(journal_path, 'r', encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            try:
                data = json.loads(line)
                # Ennemis
                if data.get("event") == "ShipTargeted" and data.get("TargetLocked"): # TargetLocked est un bool
                    if data.get("ScanStage") == 0:
                        ship_type = data.get("Ship_Localised")
                        nom_cible = ""
                        PilotRank = ""
                        ShieldHealth = 0
                        HullHealth = 0
                        bounty = 0
                        time_stamp = data.get("timestamp")
                        maj_vaisseau_ennemis = True
                    
                    elif data.get("ScanStage") == 1:
                        ship_type = data.get("Ship_Localised")
                        nom_cible = data.get("PilotName_Localised")
                        PilotRank = data.get("PilotRank")
                        time_stamp = data.get("timestamp")
                        maj_vaisseau_ennemis = True
                    
                    elif data.get("ScanStage") == 2:
                        ship_type = data.get("Ship_Localised")
                        nom_cible = data.get("PilotName_Localised")
                        PilotRank = data.get("PilotRank")
                        ShieldHealth = data.get("ShieldHealth")
                        HullHealth = data.get("HullHealth")
                        time_stamp = data.get("timestamp")
                        maj_vaisseau_ennemis = True
                    
                    elif data.get("ScanStage") == 3:
                        bounty = data.get("Bounty", 0)
                        nom_cible = data.get("PilotName_Localised")
                        PilotRank = data.get("PilotRank")
                        ShieldHealth = data.get("ShieldHealth")
                        HullHealth = data.get("HullHealth")
                        ship_type = data.get("Ship_Localised")
                        time_stamp = data.get("timestamp")
                        maj_vaisseau_ennemis = True
                
                if data.get("event") == "Bounty": # cible (recherchée) détruite
                    nom_cible_detruite = data.get("PilotName_Localised")
                    total_reward = data.get("TotalReward")
                    time_stamp = data.get("timestamp")
                
                # Joueur
                if data.get("event") == "HullDamage":
                    if data.get("PlayerPilot"): # bool
                        player_hull_health = data.get("Health")
                        time_stamp = data.get("timestamp")
                        maj_vaisseau_joueur = True
                
                if data.get("event") == "ShieldState":
                    shield_up = data.get("ShieldsUp") # bool
                    time_stamp = data.get("timestamp")
                    maj_vaisseau_joueur = True
                
            except json.JSONDecodeError:
                continue
            
            # Mise à jour des vaisseaux et du joueur
            if maj_vaisseau_ennemis:
                maj_vaiseaux(nom_cible, PilotRank, ShieldHealth, HullHealth, ship_type, bounty)
                maj_vaisseau_ennemis = False
            if maj_vaisseau_joueur:
                maj_joueur(player_hull_health, shield_up)
                maj_vaisseau_joueur = False

# ==================================== MAIN ====================================
def main():
    hud = CombatHUD()
    threading.Thread(target=monitor_journal, args=(hud,), daemon=True).start()
    hud.run()

if __name__ == "__main__":
    main()