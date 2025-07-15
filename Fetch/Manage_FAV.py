import json
import os

FAVORITE_FILE = 'favorite_stocks.json'
def loadfave():
    if not os.path.exists(FAVORITE_FILE):
        return []
    with open(FAVORITE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def savefave(favorites):
    with open(FAVORITE_FILE, 'w') as f:
        json.dump(favorites, f)

def addfav(name):
    current = loadfave()
    if name not in current:
        current.append(name)
        savefave(current)

def removefave(name):
    current = loadfave()
    if name in current: 
        current.remove(name)
        savefave(current)

