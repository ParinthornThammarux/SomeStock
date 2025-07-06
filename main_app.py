# main_app.py - Updated for new page system

import dearpygui.dearpygui as dpg
import time
from components.sidebar import create_sidebar
from containers.container_content import create_main_content, show_page
from components.stock_search import load_stock_data
from components.topbar_stuff import create_top_menu
from utils import constants

# --- Animation State Variables ---
animation_state = {
    "is_animating": False,
    "start_time": 0.0,
    "start_width": 0,
    "target_width": 0,
    "current_direction": None
}

# --- Animation Function ---
def animate_sidebar():
    if not animation_state["is_animating"]:
        return

    elapsed_time = time.time() - animation_state["start_time"]
    progress = min(1.0, elapsed_time / constants.ANIMATION_DURATION)

    current_width = animation_state["start_width"] + \
                    (animation_state["target_width"] - animation_state["start_width"]) * progress

    dpg.set_item_width("sidebar_window", int(current_width))

    if progress >= 1.0:
        animation_state["is_animating"] = False
        dpg.set_item_width("sidebar_window", animation_state["target_width"])

        if animation_state["current_direction"] == "expand":
            dpg.show_item("sidebar_content_group")
            dpg.hide_item("sidebar_icons_group")
        elif animation_state["current_direction"] == "collapse":
            dpg.hide_item("sidebar_content_group")
            dpg.show_item("sidebar_icons_group")
    else:
        dpg.set_frame_callback(dpg.get_frame_count() + 1, animate_sidebar)

def toggle_sidebar(sender, app_data, user_data):
    if animation_state["is_animating"]:
        return

    current_width = dpg.get_item_width("sidebar_window")

    animation_state["start_width"] = current_width
    animation_state["start_time"] = time.time()
    animation_state["is_animating"] = True

    if current_width > constants.COLLAPSED_WIDTH + 10:
        # Currently expanded - collapse it
        animation_state["target_width"] = constants.COLLAPSED_WIDTH
        animation_state["current_direction"] = "collapse"
        #dpg.set_item_label("toggle_button", constants.ICON_BARS)
        dpg.hide_item("sidebar_content_group")
    else:
        # Currently collapsed - expand it
        animation_state["target_width"] = constants.EXPANDED_WIDTH
        animation_state["current_direction"] = "expand"
        #dpg.set_item_label("toggle_button", constants.ICON_BARS)
        dpg.hide_item("sidebar_icons_group")

    dpg.set_frame_callback(dpg.get_frame_count() + 1, animate_sidebar)

# Updated callback function for main_app.py

def icon_button_callback(sender, app_data, user_data):
    """Updated callback to use the new page system including enhanced charts"""
    button_label = dpg.get_item_label(sender)
    print(f"Button '{button_label}' (tag: {sender}) clicked!")

    # Show page stuff put here!!! if we have more pages we can put it
    if sender == "dashboard_icon_btn" or button_label == "Dashboard":
        show_page("enhanced")  # send to graph container
    elif sender == "search_icon_btn" or button_label == "Search":
        show_page("page_b")
    elif sender == "portfolio_icon_btn" or button_label == "Portfolio":
        show_page("welcome")  # main as forback
    elif sender == "add_icon_btn" or button_label == "Add Item":
        show_page("page_b")
    elif sender == "remove_icon_btn" or button_label == "Remove Item":
        show_page("page_b")
    elif sender == "Indicator_icon_btn" or button_label == "Indicator":
        # Import here to avoid circular import issues
        from pages.Indicator_page import Create_Indicator_page
        Create_Indicator_page("page_content_container")

def main():
    dpg.create_context()
    dpg.create_viewport(title='SomeStock', width=constants.WinW, height=constants.WinH, x_pos=0, y_pos=0, vsync=True)

    constants.load_fonts()
    dpg.setup_dearpygui()
    dpg.set_viewport_vsync(True)
    with dpg.window(tag="main_window", label="SomeStock", autosize=True, no_resize=True, 
                    no_collapse=True, no_move=True, no_title_bar=True):
        create_top_menu()
        with dpg.group(horizontal=True, tag="root_group"):
            create_sidebar(
                parent_tag="root_group",
                toggle_callback=toggle_sidebar,
                icon_button_callback=icon_button_callback,
                initial_width=constants.COLLAPSED_WIDTH  
            )
            create_main_content(parent_tag="root_group")
            
    load_stock_data()
    dpg.set_primary_window("main_window", True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()