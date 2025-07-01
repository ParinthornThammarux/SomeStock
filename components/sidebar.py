# components/sidebar.py

import dearpygui.dearpygui as dpg
from utils import constants

def create_sidebar(parent_tag, toggle_callback, icon_button_callback, initial_width=constants.EXPANDED_WIDTH):
    """
    Creates the collapsible sidebar.

    Args:
        parent_tag (str): The tag of the parent item to add the sidebar to.
        toggle_callback (callable): The callback function for the toggle button.
        icon_button_callback (callable): The callback function for the icon buttons.
        initial_width (int): The initial width of the sidebar.
    """
    with dpg.child_window(tag="sidebar_window", width=initial_width, height=-1, show=True, parent=parent_tag):
        # Toggle button always visible
        dpg.add_button(label=constants.ICON_BARS, tag="toggle_button", callback=toggle_callback, width=-1)
        if constants.font_awesome_icon_font_id:
            dpg.bind_item_font("toggle_button", constants.font_awesome_icon_font_id)
        dpg.add_separator()

        # Group for full menu content (initially Invisible)
        with dpg.group(tag="sidebar_content_group", show=False):
            dpg.add_text("Menu Items")
            dpg.add_separator()
            dpg.add_button(label="Dashboard", width=-1, callback=icon_button_callback)
            dpg.add_button(label="Search", width=-1, callback=icon_button_callback)
            dpg.add_button(label="Portfolio", width=-1, callback=icon_button_callback)
            dpg.add_spacer(height=10)
            dpg.add_text("Sub-Menu")
            dpg.add_button(label="Add Item", width=-1, callback=icon_button_callback)
            dpg.add_button(label="Remove Item", width=-1, callback=icon_button_callback)

        # Group for icons (initially shown)
        with dpg.group(tag="sidebar_icons_group", show=True):
            if constants.font_awesome_icon_font_id:
                dpg.add_button(label=constants.ICON_HOME, width=-1, callback=icon_button_callback, tag="dashboard_icon_btn")
                dpg.bind_item_font("dashboard_icon_btn", constants.font_awesome_icon_font_id)

                dpg.add_button(label=constants.ICON_SEARCH, width=-1, callback=icon_button_callback, tag="search_icon_btn")
                dpg.bind_item_font("search_icon_btn", constants.font_awesome_icon_font_id)

                dpg.add_button(label=constants.ICON_CHART_BAR, width=-1, callback=icon_button_callback, tag="portfolio_icon_btn")
                dpg.bind_item_font("portfolio_icon_btn", constants.font_awesome_icon_font_id)

                dpg.add_separator()
                dpg.add_button(label=constants.ICON_PLUS, width=-1, callback=icon_button_callback, tag="add_icon_btn")
                dpg.bind_item_font("add_icon_btn", constants.font_awesome_icon_font_id)

                dpg.add_button(label=constants.ICON_MINUS, width=-1, callback=icon_button_callback, tag="remove_icon_btn")
                dpg.bind_item_font("remove_icon_btn", constants.font_awesome_icon_font_id)
            else:
                dpg.add_text("Icons not loaded. Check console for errors.", color=[255,0,0])