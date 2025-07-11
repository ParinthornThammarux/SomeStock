# Fetch/Manage_FAV.py

import json
import os

def loadfave(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def savefave(favorites, filepath):
    favorites.sort()
    with open(filepath, 'w') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def addfav(name, filepath):
    current = loadfave(filepath)
    if name not in current:
        current.append(name)
        savefave(current, filepath)

def removefave(name, filepath):
    current = loadfave(filepath)
    if name in current:
        current.remove(name)
        savefave(current, filepath)
