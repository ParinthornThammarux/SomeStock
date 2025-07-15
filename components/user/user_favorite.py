# components/user/user_favorite.py

import json
import os
from datetime import datetime as dt
from typing import List, Tuple, Optional
from components.user.user_helper import load_user_data, save_user_data
from utils import constants

# Global variable to track current logged-in user

def get_user_favorites(username: str = None) -> List[Tuple[str, str]]:
    """
    Get user's favorite stocks as a list of tuples (symbol, company_name).
    Returns empty list if no favorites or user not found.
    """
    
    username = constants.Cur_User
    
    if not username:
        print("⚠️ No user logged in")
        return []
    
    user_data = load_user_data(username)
    if not user_data:
        return []
    
    # Get favorites list, default to empty list if not exists
    favorites = user_data.get("favorite_stocks", [])
    
    # Ensure all items are tuples with 2 elements
    valid_favorites = []
    for item in favorites:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            valid_favorites.append((str(item[0]), str(item[1])))
        elif isinstance(item, str):
            # Handle legacy single string format
            valid_favorites.append((item, f"{item} Corp."))
    
    return valid_favorites

def add_favorite_stock(stock_symbol: str, company_name: str = None, username: str = None) -> bool:
    """
    Add a stock to the user's favorite list.
    
    Args:
        stock_symbol: Stock symbol (e.g., 'AAPL')
        company_name: Company name (e.g., 'Apple Inc.')
        username: Username (uses current logged-in user if None)
    
    Returns:
        bool: True if successfully added, False otherwise
    """
    
    username = constants.Cur_User
        
    
    if not username:
        print("❌ No user logged in - cannot add favorite")
        return False
    
    if not stock_symbol:
        print("❌ Invalid stock symbol")
        return False
    
    # Clean up inputs
    stock_symbol = stock_symbol.strip().upper()
    if company_name:
        company_name = company_name.strip()
    else:
        company_name = f"{stock_symbol} Corp."
    
    # Load user data
    user_data = load_user_data(username)
    if not user_data:
        print(f"❌ Could not load user data for {username}")
        return False
    
    # Initialize favorites list if it doesn't exist
    if "favorite_stocks" not in user_data:
        user_data["favorite_stocks"] = []
    
    # Check if stock is already in favorites (by symbol)
    existing_favorites = get_user_favorites(username)
    for existing_symbol, _ in existing_favorites:
        if existing_symbol == stock_symbol:
            print(f"📊 {stock_symbol} is already in {username}'s favorites")
            return True  # Already exists, consider it success
    
    # Add new favorite as tuple
    new_favorite = (stock_symbol, company_name)
    user_data["favorite_stocks"].append(new_favorite)
    
    # Save updated data
    if save_user_data(username, user_data):
        print(f"✅ Added {stock_symbol} ({company_name}) to {username}'s favorites")
        return True
    else:
        print(f"❌ Failed to save favorite {stock_symbol} for {username}")
        return False
    

def remove_favorite_stock(stock_symbol: str, username: str = None) -> bool:
    """
    Remove a stock from the user's favorite list.
    
    Args:
        stock_symbol: Stock symbol to remove
        username: Username (uses current logged-in user if None)
    
    Returns:
        bool: True if successfully removed, False otherwise
    """
    
    username = constants.Cur_User
    
    if not constants.Cur_User:
        print("❌ No user logged in - cannot remove favorite")
        return False
    
    stock_symbol = stock_symbol.strip().upper()
    
    # Load user data
    user_data = load_user_data(username)
    if not user_data or "favorite_stocks" not in user_data:
        print(f"⚠️ No favorites found for {username}")
        return False
    
    # Find and remove the stock
    original_count = len(user_data["favorite_stocks"])
    user_data["favorite_stocks"] = [
        fav for fav in user_data["favorite_stocks"]
        if not (
            (isinstance(fav, (list, tuple)) and len(fav) >= 1 and str(fav[0]).upper() == stock_symbol) or
            (isinstance(fav, str) and fav.upper() == stock_symbol)
        )
    ]
    
    # Check if anything was removed
    if len(user_data["favorite_stocks"]) < original_count:
        # Save updated data
        if save_user_data(username, user_data):
            print(f"✅ Removed {stock_symbol} from {username}'s favorites")
            return True
        else:
            print(f"❌ Failed to save after removing {stock_symbol}")
            return False
    else:
        print(f"⚠️ {stock_symbol} was not found in {username}'s favorites")
        return False    