# components/welcome_page.py - Updated for new system

import dearpygui.dearpygui as dpg
import os
from utils import constants

def create_welcome_content(parent_tag):
    """
    Creates the welcome page content directly in the parent container.
    No child windows - just content.
    """
    print(f"Creating welcome content in parent: {parent_tag}")
    
    # Create large font for welcome page
    with dpg.font_registry():
        large_font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
        if not os.path.exists(large_font_path):
            large_font_path = ""
        
        with dpg.font(large_font_path, 28) as large_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        
        with dpg.font(large_font_path, 18) as medium_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
    
    # Add flexible spacer to center content vertically
    dpg.add_spacer(height=-1, parent=parent_tag)
    
    # Create a centered group for the welcome content
    with dpg.group(horizontal=False, parent=parent_tag):
        # Horizontal centering wrapper
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=-1)  # Left spacer
            
            # Centered content group
            with dpg.group(horizontal=False):
                # Welcome Title (large font)
                title_text = dpg.add_text("Welcome to SomeStock", color=[255, 255, 255])
                dpg.bind_item_font(title_text, large_font)
                dpg.add_spacer(height=15)
                
                # Subtitle (medium font)
                subtitle_text = dpg.add_text("A Stock Analysis Tool using algorithms and AI", color=[150, 150, 150])
                dpg.bind_item_font(subtitle_text, medium_font)
                dpg.add_spacer(height=30)
                
                # Icon and Version - centered
                with dpg.group(horizontal=True):
                    if constants.font_awesome_icon_font_id:
                        icon_text = dpg.add_text(constants.ICON_BOLT, color=[255, 200, 0])
                        dpg.bind_item_font(icon_text, constants.font_awesome_icon_font_id)
                        dpg.add_spacer(width=10)
                    version_text = dpg.add_text(f"Version {constants.VERSION}", color=[180, 180, 180])
                    dpg.bind_item_font(version_text, medium_font)
                
                dpg.add_spacer(height=50)
                
                # Test button to switch to Page B (centered)
                #dpg.add_button(label="Test: Go to Page B", callback=test_show_page_b, width=250, height=40)
            
            dpg.add_spacer(width=-1)  # Right spacer
    
    # Add flexible spacer to center content vertically
    dpg.add_spacer(height=-1, parent=parent_tag)

def test_show_page_b():
    """Test function to show Page B using the new system"""
    print("Test button clicked - switching to Page B")
    from .main_content import show_page
    show_page("page_b")

# Keep the old function for backward compatibility, but make it use the new system
def create_welcome(parent_tag):
    """Legacy function - redirects to new system"""
    return create_welcome_content(parent_tag)