import json
import os

def loadfave(filepath):
    if not filepath or not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def savefave(favorites, filepath):
    if not filepath:
        return
    favorites.sort()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def addfav(name, filepath):
    favorites = loadfave(filepath)
    if name not in favorites:
        favorites.append(name)
        savefave(favorites, filepath)

def removefave(name, filepath):
    favorites = loadfave(filepath)
    if name in favorites:
        favorites.remove(name)
        savefave(favorites, filepath)
