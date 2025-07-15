# containers/content_container.py

# Wraps everything on the right side (excluding sidebar) 

import dearpygui.dearpygui as dpg
from components.user.user_create import create_user_creation_content
from components.user.user_login import create_user_login_content
from pages.welcome_page import create_welcome_content
from pages.example_page_b import create_example_page_b_content
from components.graph.graph_dpg import create_main_graph
from containers.container_graph_tabs import create_graph_tabs

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

# Switches Pages in the content container
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
    match page_name:
        case "welcome":
            create_welcome_content("page_content_container")
            current_page = "welcome"
        case "main":
            create_main_graph("page_content_container")  # Original simple chart
            current_page = "main"
        case "enhanced":
            create_main_graph("page_content_container")
            current_page = "enhanced"
        case "create_hailun_content":
            # Hailun page content
            from pages.Hailun_page import create_hailun_content
            create_hailun_content("page_content_container")
            current_page = "hailun"
            print("Loaded indicator page content")
        case "page_b":
            create_graph_tabs("page_content_container")
            current_page = "page_b"
            print("Loaded page B content")
        case "user_create":
            current_page = "user_create"
            create_user_creation_content("page_content_container")
            print("Loaded User_create")
        case "user_login":
            current_page = "user_login"
            create_user_login_content("page_content_container")
            print("Loaded User_create")
        case "indicator":
            # Import here to avoid circular import issues
            from pages.Indicator_page import Create_Indicator_page
            Create_Indicator_page("page_content_container")
            current_page = "indicator"
            print("Loaded indicator page content")
        case _:  # Default case
            dpg.add_text("Page not found", parent="page_content_container", color=[255, 0, 0])
            print(f"Unknown page: {page_name}")
            current_page = None

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