# pages/content_container.py - Updated with enhanced charts

import dearpygui.dearpygui as dpg
from .welcome_page import create_welcome_content
from .example_page_b import create_example_page_b_content
from .main_graph_page import create_main_graph
from .enhanced_main_graph_page import create_enhanced_main_graph  # New import

# Global variable to track current page
current_page = "welcome"

def create_main_content(parent_tag):
    """
    Creates the main content area with a single container that gets cleared and repopulated.
    """
    with dpg.child_window(tag="content_window", width=-1, height=-1, parent=parent_tag, border=False):
        # Apply black background theme
        with dpg.theme(tag="content_window_black_bg_theme"):
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [0, 0, 0, 255])
        dpg.bind_item_theme("content_window", "content_window_black_bg_theme")
        
        # Single container for all page content
        with dpg.group(tag="page_content_container", width=-1, height=-1):
            # Initially load welcome page
            show_page("welcome")

def show_page(page_name):
    """
    Clears the page container and loads the specified page content.
    """
    global current_page
    
    print(f"Switching to page: {page_name}")
    
    # Clear existing content
    if dpg.does_item_exist("page_content_container"):
        dpg.delete_item("page_content_container", children_only=True)
        print("Cleared existing page content")
    
    # Load new page content based on page name
    if page_name == "welcome":
        create_welcome_content("page_content_container")
        current_page = "welcome"
    elif page_name == "main":
        create_main_graph("page_content_container")  # Original simple chart
        current_page = "main"
    elif page_name == "enhanced":  # New enhanced page
        create_enhanced_main_graph("page_content_container")
        current_page = "enhanced"
    elif page_name == "page_b":
        create_example_page_b_content("page_content_container")
        current_page = "page_b"
        print("Loaded page B content")
    else:
        # Default fallback
        dpg.add_text("Page not found", parent="page_content_container", color=[255, 0, 0])
        print(f"Unknown page: {page_name}")

def get_current_page():
    """Returns the current page name"""
    return current_page

# Updated pages dictionary
PAGES = {
    "welcome": {"tag": "welcome"},
    "main": {"tag": "main"},
    "enhanced": {"tag": "enhanced"},  # New enhanced page
    "page_b": {"tag": "page_b"},
}