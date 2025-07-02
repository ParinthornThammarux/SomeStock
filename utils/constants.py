# utils/constants.py - Updated with new chart icons

import dearpygui.dearpygui as dpg
import os
from pathlib import Path

VERSION = "v1.0.1 Graph demo"
# --- Font Awesome Icon Setup ---
# IMPORTANT: You need the Font Awesome Free font file 'fa-solid-900.ttf'.
# Place it in the root directory of your project (your_project_folder/).
FONT_AWESOME_PATH = 'fa-solid-900.ttf'

# Define Font Awesome 6 (Solid) icon codes (Unicode values)
ICON_HOME = "\uf015"
ICON_COG = "\uf013"
ICON_CHART_BAR = "\uf080"
ICON_PLUS = "\uf067"
ICON_MINUS = "\uf068"
ICON_ARROW_LEFT = "\uf060"
ICON_ARROW_RIGHT = "\uf061"
ICON_BOLT = "\uf0e7" # New icon for "AI" or "power"
ICON_BARS = "\uf0c9" # Three line menu (hamburger menu)
ICON_SEARCH = "\uf002" # Search/magnifying glass icon
ICON_HEART = "\uf004"  # Font Awesome solid heart icon

# New chart-specific icons
ICON_CHART_LINE = "\uf201"  # Line chart icon for DPG charts
ICON_CHART_AREA = "\uf1fe"  # Area chart icon for advanced analysis
ICON_GLOBE = "\uf0ac"       # Globe icon for interactive charts
ICON_EXCHANGE_ALT = "\uf362"  # Exchange/flow icon for Sankey analysis
ICON_CALCULATOR = "\uf1ec"  # Calculator icon for analysis
ICON_CHART_PIE = "\uf200"   # Pie chart icon
ICON_ANALYTICS = "\uf643"   # Analytics icon (alternative)

# --- Animation Parameters ---
ANIMATION_DURATION = 0.2  # seconds
COLLAPSED_WIDTH = 50
EXPANDED_WIDTH = 200

# --- Global Font References (will be populated in main_app.py) ---
default_font_id = None
font_awesome_icon_font_id = None

# --- Helper to load fonts ---
def load_fonts():
    global default_font_id, font_awesome_icon_font_id

    with dpg.font_registry():
        # Default font for most text
        default_font_path = "C:\\Windows\\Fonts\\segoeui.ttf" # Windows example
        if not os.path.exists(default_font_path):
            default_font_path = "" # Use DPG's default font if specific path fails
            print(f"Warning: 'segoeui.ttf' not found. Using DearPyGUI's default font for text.")

        with dpg.font(default_font_path, 16) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            default_font_id = default_font

        # Font Awesome font for icons
        if os.path.exists(FONT_AWESOME_PATH):
            try:
                with dpg.font(FONT_AWESOME_PATH, 20) as fa_font:
                    dpg.add_font_range(0xf000, 0xf2e0)
                    dpg.add_font_range(0xf300, 0xf5ff)
                    dpg.add_font_range(0xf600, 0xf8ff)
                    dpg.add_font_range(0xf0000, 0x10ffff)
                    font_awesome_icon_font_id = fa_font
                    print(f"Font Awesome font loaded from: {FONT_AWESOME_PATH}")
            except Exception as e:
                print(f"Error loading Font Awesome font from '{FONT_AWESOME_PATH}': {e}")
                print("Icons may not display correctly. Please ensure the font file is valid and accessible.")
        else:
            print(f"Error: Font Awesome font file '{FONT_AWESOME_PATH}' not found.")
            print("Please download 'fa-solid-900.ttf' and place it in the script directory or update the FONT_AWESOME_PATH.")