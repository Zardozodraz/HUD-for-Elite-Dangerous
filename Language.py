"""
This file defines all the words displayed on the HUDs, translated into multiple languages.
Structure:
  language_name = {
      "HUD_Name": {
          "Key": "Translated Text",
          ...
      },
      ...
  }
To add a new language, replicate the same structure using the appropriate translations.
"""

french = {
    "HUD_System": {
        "System": "Système",
        "No_interesting_body": "Aucun corps intéressant",
    },
    
    "HUD_ExoBio": {
        "Exo_Biology": "Exo-biologie",
        "No_interesting_body": "Aucun corps intéressant",
    },
    
    "HUD_SessionStats": {
        "Kills": "Kills",
        "Distance": "Distance",
        "Jumps": "Sauts",
        "Bounty": "Prime",
        "Sell": "Ventes",
        "Buy": "Achats",
        "Codex": "Codex",
        "Exploration": "Exploration",
        "Session": "Session",
    },
    
    "Launcher": {
        "Systems": "Systèmes",
        "ExoBio": "Exo-Bio",
        "Combat": "Combat",
        "Stats": "Stats",
        "Lang": "Langue",
    },
}

english = {
    "HUD_System": {
        "System": "System",
        "No_interesting_body": "No interesting body",
    },
    
    "HUD_ExoBio": {
        "Exo_Biology": "Exo-biology",
        "No_interesting_body": "No interesting body",
    },
    
    "HUD_SessionStats": {
        "Kills": "Kills",
        "Distance": "Distance",
        "Jumps": "Jumps",
        "Bounty": "Bounty",
        "Sell": "Sell",
        "Buy": "Buy",
        "Codex": "Codex",
        "Exploration": "Exploration",
        "Session": "Session",
    },
    
    "Launcher": {
        "Systems": "Systems",
        "ExoBio": "Exo-Biology",
        "Combat": "Combat",
        "Stats": "Stats",
        "Lang": "Language",
    },
}



# All the languages traducted

languages = {
    "french": french,
    "english": english,
}