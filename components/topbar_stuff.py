import os
import time
import dearpygui.dearpygui as dpg
from containers.container_content import show_page
from utils import constants

import sys

def create_top_menu():
    create_close_dialog()
    dpg.set_item_pos("close_dialog", (constants.WinW // 2 - 150, constants.WinH // 2 - 75))
    with dpg.menu_bar():
        with dpg.menu(label="Profile", tag='user'):
            dpg.add_menu_item(label="Create User", callback=lambda: (dpg.show_item("option_window"), dpg.focus_item("option_window")))
            dpg.add_menu_item(label="Switch User", callback=lambda: (dpg.show_item("option_window"), dpg.focus_item("option_window")))
            dpg.add_menu_item(label="Save Data", callback=lambda: (dpg.show_item("option_window"), dpg.focus_item("option_window")))

        dpg.add_button(label="Options", callback=lambda: dpg.configure_item("about_window", show=True))
        dpg.add_button(label="About", callback=lambda: show_page("welcome"))
        dpg.add_button(label="Close", callback=lambda: (dpg.show_item("close_dialog"), dpg.focus_item("close_dialog")))

def create_close_dialog():
    with dpg.window(label="Exit Dialog", width=300, height=150, 
                    show=False, tag="close_dialog",
                    no_collapse=True, no_title_bar=False,
                    no_move=True, no_close=True, no_resize=True):
        dpg.add_spacer(height=5)
        dpg.add_text("Confirm abort and exit?", tag="cf_abort_txt", indent=61)
        dpg.add_text("Exiting...", tag="exit_txt", indent=120, show=False)
        dpg.add_spacer(height=25)
        
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=63)
            dpg.add_button(label="CANCEL", callback=close_cancel, tag="cancel_button")
            dpg.add_spacer(width=20)
            dpg.add_button(label="CONFIRM", callback=close_confirm, tag="confirm_button")
        
        dpg.add_progress_bar(label="Progress", tag="progress_bar", show=False, 
                           indent=45, width=200)

def close_cancel():
    dpg.hide_item("close_dialog")
    # Reset dialog state
    dpg.show_item("cf_abort_txt")
    dpg.show_item("cancel_button")
    dpg.show_item("confirm_button")
    dpg.hide_item("exit_txt")
    dpg.hide_item("progress_bar")
    dpg.set_value("progress_bar", 0.0)

def close_confirm():
    # Hide text and buttons, show progress
    dpg.hide_item("cf_abort_txt")
    dpg.hide_item("cancel_button")
    dpg.hide_item("confirm_button")
    dpg.show_item("exit_txt")
    dpg.show_item("progress_bar")
    
    # Quick progress and exit
    for i in range(101):
        dpg.set_value("progress_bar", i / 100.0)
        time.sleep(0.01)
    
    dpg.stop_dearpygui()
    
    dpg.destroy_context()
    os._exit(0)  # Force exit the Python process