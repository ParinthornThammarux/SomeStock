# utils/constants.py - Updated with new chart icons

import dearpygui.dearpygui as dpg
import os
from pathlib import Path

VERSION = "v1.1.0 Table loaded and Indicator imported"
DEBUG = True
# --- Font Awesome Icon Setup ---
# IMPORTANT: You need the Font Awesome Free font file 'fa-solid-900.ttf'.
# Place it in the root directory of your project (your_project_folder/).
FONT_AWESOME_PATH = 'fa-solid-900.ttf'

# === BASIC NAVIGATION & UI ===
ICON_HOME = "\uf015"
ICON_COG = "\uf013"
ICON_BARS = "\uf0c9"
ICON_SEARCH = "\uf002"
ICON_PLUS = "\uf067"
ICON_MINUS = "\uf068"
ICON_TIMES = "\uf00d"  # X/close icon
ICON_ARROW_LEFT = "\uf060"
ICON_ARROW_RIGHT = "\uf061"
ICON_ARROW_UP = "\uf062"
ICON_ARROW_DOWN = "\uf063"
ICON_EYE = "\uf06e"
ICON_EYE_SLASH = "\uf070"

# === CHECKMARKS & STATUS ===
ICON_CHECK = "\uf00c"  # ✓ Simple checkmark
ICON_CHECK_CIRCLE = "\uf058"  # ✓ Checkmark in circle
ICON_CHECK_SQUARE = "\uf14a"  # ✓ Checkmark in square
ICON_TIMES_CIRCLE = "\uf057"  # ✗ X in circle (error)
ICON_EXCLAMATION = "\uf12a"  # ! Exclamation mark
ICON_EXCLAMATION_TRIANGLE = "\uf071"  # ⚠ Warning triangle
ICON_INFO_CIRCLE = "\uf05a"  # ℹ Info circle
ICON_QUESTION_CIRCLE = "\uf059"  # ? Question mark circle

# === FINANCIAL & BUSINESS ===
ICON_CHART_BAR = "\uf080"
ICON_CHART_LINE = "\uf201"
ICON_CHART_AREA = "\uf1fe"
ICON_CHART_PIE = "\uf200"
ICON_ANALYTICS = "\uf643"
ICON_CALCULATOR = "\uf1ec"
ICON_DOLLAR_SIGN = "\uf155"  # $ Dollar symbol
ICON_EURO_SIGN = "\uf153"    # € Euro symbol
ICON_YEN_SIGN = "\uf157"     # ¥ Yen symbol
ICON_POUND_SIGN = "\uf154"   # £ Pound symbol
ICON_COINS = "\uf51e"        # Coins icon
ICON_WALLET = "\uf555"       # Wallet icon
ICON_CREDIT_CARD = "\uf09d"  # Credit card
ICON_BANK = "\uf19c"         # Bank building
ICON_BRIEFCASE = "\uf0b1"    # Briefcase
ICON_HANDSHAKE = "\uf2b5"    # Handshake (deals)

# === CHARTS & ANALYSIS ===
ICON_GLOBE = "\uf0ac"
ICON_EXCHANGE_ALT = "\uf362"
ICON_TRENDING_UP = "\uf201"    # Same as chart_line but conceptually trending up
ICON_TRENDING_DOWN = "\uf200"  # Pie chart but can represent down trend
ICON_BALANCE_SCALE = "\uf24e"  # Balance/scales
ICON_PERCENTAGE = "\uf541"     # % Percentage symbol

# === ACTIONS & OPERATIONS ===
ICON_DOWNLOAD = "\uf019"
ICON_UPLOAD = "\uf093"
ICON_SAVE = "\uf0c7"        # Floppy disk save icon
ICON_FOLDER = "\uf07b"      # Folder
ICON_FILE = "\uf15b"        # File
ICON_FILE_EXCEL = "\uf1c3"  # Excel file
ICON_FILE_CSV = "\uf6dd"    # CSV file
ICON_PRINT = "\uf02f"       # Printer
ICON_SHARE = "\uf064"       # Share arrow
ICON_COPY = "\uf0c5"        # Copy/duplicate
ICON_EDIT = "\uf044"        # Edit/pencil
ICON_TRASH = "\uf1f8"       # Trash can
ICON_SYNC = "\uf021"        # Refresh/sync arrows
ICON_UNDO = "\uf0e2"        # Undo arrow
ICON_REDO = "\uf01e"        # Redo arrow

# === FAVORITES & SOCIAL ===
ICON_HEART = "\uf004"
ICON_HEART_BROKEN = "\uf7a9"
ICON_STAR = "\uf005"        # ★ Filled star
ICON_STAR_HALF = "\uf089"   # ☆ Half star
ICON_THUMBS_UP = "\uf164"   # 👍 Thumbs up
ICON_THUMBS_DOWN = "\uf165" # 👎 Thumbs down
ICON_BOOKMARK = "\uf02e"    # Bookmark
ICON_FLAG = "\uf024"        # Flag

# === TIME & SCHEDULING ===
ICON_CLOCK = "\uf017"       # Clock
ICON_CALENDAR = "\uf073"    # Calendar
ICON_CALENDAR_ALT = "\uf455" # Alternative calendar
ICON_HISTORY = "\uf1da"     # History/clock with arrow

# === NOTIFICATIONS & ALERTS ===
ICON_BELL = "\uf0f3"        # Bell (notifications)
ICON_BELL_SLASH = "\uf1f6"  # Bell with slash (muted)
ICON_ENVELOPE = "\uf0e0"    # Email
ICON_COMMENT = "\uf075"     # Comment bubble

# === SETTINGS & TOOLS ===
ICON_WRENCH = "\uf0ad"      # Wrench (tools)
ICON_SCREWDRIVER = "\uf54a" # Screwdriver
ICON_HAMMER = "\uf6e3"      # Hammer
ICON_TOOLS = "\uf7d9"       # Multiple tools
ICON_SLIDERS = "\uf1de"     # Sliders (settings)
ICON_FILTER = "\uf0b0"      # Filter

# === CONNECTIVITY & TECH ===
ICON_WIFI = "\uf1eb"        # WiFi signal
ICON_SIGNAL = "\uf012"      # Signal bars
ICON_PLUG = "\uf1e6"        # Power plug
ICON_USB = "\uf287"         # USB icon
ICON_DATABASE = "\uf1c0"    # Database
ICON_SERVER = "\uf233"      # Server
ICON_CLOUD = "\uf0c2"       # Cloud
ICON_LINK = "\uf0c1"        # Link/chain

# === MEDIA & CONTENT ===
ICON_PLAY = "\uf04b"        # Play button
ICON_PAUSE = "\uf04c"       # Pause button
ICON_STOP = "\uf04d"        # Stop button
ICON_VOLUME_UP = "\uf028"   # Speaker with sound
ICON_VOLUME_MUTE = "\uf6a9" # Muted speaker
ICON_IMAGE = "\uf03e"       # Image/picture
ICON_VIDEO = "\uf03d"       # Video camera

# === SPECIAL & MISC ===
ICON_BOLT = "\uf0e7"        # Lightning bolt (energy/fast)
ICON_FIRE = "\uf06d"        # Fire (hot/trending)
ICON_SNOWFLAKE = "\uf2dc"   # Snowflake (cold/frozen)
ICON_SUN = "\uf185"         # Sun
ICON_MOON = "\uf186"        # Moon
ICON_MAGIC = "\uf0d0"       # Magic wand
ICON_GIFT = "\uf06b"        # Gift box
ICON_TROPHY = "\uf091"      # Trophy (winner)
ICON_MEDAL = "\uf5a2"       # Medal
ICON_CROWN = "\uf521"       # Crown
ICON_KEY = "\uf084"         # Key
ICON_LOCK = "\uf023"        # Lock (closed)
ICON_UNLOCK = "\uf09c"      # Lock (open)
ICON_SHIELD = "\uf132"      # Shield (security)
ICON_SEARCH_DOLLAR = "\uf688"    # Magnifying glass with dollar (financial analysis)

# === LAYOUT & ORGANIZATION ===
ICON_TH = "\uf00a"          # Grid (3x3)
ICON_TH_LARGE = "\uf009"    # Large grid (2x2)
ICON_TH_LIST = "\uf00b"     # List view
ICON_COLUMNS = "\uf0db"     # Columns
ICON_SORT = "\uf0dc"        # Sort arrows
ICON_SORT_UP = "\uf0de"     # Sort ascending
ICON_SORT_DOWN = "\uf0dd"   # Sort descending

# === USER & PEOPLE ===
ICON_USER = "\uf007"        # Single user
ICON_USERS = "\uf0c0"       # Multiple users
ICON_USER_PLUS = "\uf234"   # Add user
ICON_USER_MINUS = "\uf503"  # Remove user
ICON_USER_COG = "\uf4fe"    # User settings

# --- Animation Parameters ---
ANIMATION_DURATION = 0.2  # seconds
COLLAPSED_WIDTH = 50
EXPANDED_WIDTH = 200

# --- User variables
Cur_User = None
favorite_stocks = []
active_indicator_buttons = set()
# --- Global Font References (will be populated in main_app.py) ---
default_font_id = None
font_awesome_icon_font_id = None
small_font_awesome_icon_font_id = None

# --- SET screen size
WinW = 1400
WinH = 800

# --- Helper to load fonts ---
def load_fonts():
    global default_font_id, font_awesome_icon_font_id, small_font_awesome_icon_font_id

    with dpg.font_registry():
        # Default font for most text
        default_font_path = "C:\\Windows\\Fonts\\segoeui.ttf" # Windows example
        if not os.path.exists(default_font_path):
            default_font_path = "" # Use DPG's default font if specific path fails
            print(f"Warning: 'segoeui.ttf' not found. Using DearPyGUI's default font for text.")

        with dpg.font(default_font_path, 16) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            default_font_id = default_font

        # Font Awesome font for icons (regular size)
        if os.path.exists(FONT_AWESOME_PATH):
            try:
                with dpg.font(FONT_AWESOME_PATH, 20) as fa_font:
                    dpg.add_font_range(0xf000, 0xf2e0)
                    dpg.add_font_range(0xf300, 0xf5ff)
                    dpg.add_font_range(0xf600, 0xf8ff)
                    dpg.add_font_range(0xf0000, 0x10ffff)
                    font_awesome_icon_font_id = fa_font
                    print(f"Font Awesome font (size 20) loaded from: {FONT_AWESOME_PATH}")
                
                # Small Font Awesome font for smaller buttons
                with dpg.font(FONT_AWESOME_PATH, 10) as small_fa_font:
                    dpg.add_font_range(0xf000, 0xf2e0)
                    dpg.add_font_range(0xf300, 0xf5ff)
                    dpg.add_font_range(0xf600, 0xf8ff)
                    dpg.add_font_range(0xf0000, 0x10ffff)
                    small_font_awesome_icon_font_id = small_fa_font
                    print(f"Font Awesome font (size 14) loaded from: {FONT_AWESOME_PATH}")
                    
            except Exception as e:
                print(f"Error loading Font Awesome font from '{FONT_AWESOME_PATH}': {e}")
                print("Icons may not display correctly. Please ensure the font file is valid and accessible.")
                font_awesome_icon_font_id = None
                small_font_awesome_icon_font_id = None
        else:
            print(f"Error: Font Awesome font file '{FONT_AWESOME_PATH}' not found.")
            print("Please download 'fa-solid-900.ttf' and place it in the script directory or update the FONT_AWESOME_PATH.")
            font_awesome_icon_font_id = None
            small_font_awesome_icon_font_id = None