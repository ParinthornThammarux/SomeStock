# components/user/user_helper.py

from datetime import datetime as dt
import json
import os
from typing import Optional


def get_user_file_path(username: str) -> str:
    """Get the file path for a user's JSON file"""
    users_dir = "registered_users"
    return os.path.join(users_dir, f"{username}.json")

def load_user_data(username: str) -> Optional[dict]:
    """Load user data from JSON file"""
    try:
        user_file = get_user_file_path(username)
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"❌ User file not found: {user_file}")
            return None
    except Exception as e:
        print(f"❌ Error loading user data for {username}: {e}")
        return None

def save_user_data(username: str, user_data: dict) -> bool:
    """Save user data to JSON file"""
    try:
        user_file = get_user_file_path(username)
        
        # Ensure directory exists
        users_dir = os.path.dirname(user_file)
        if not os.path.exists(users_dir):
            os.makedirs(users_dir)
        
        # Update last modified timestamp
        user_data["last_modified"] = dt.now().isoformat()
        
        # Save to file
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ User data saved for {username}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving user data for {username}: {e}")
        return False