# components/main_graph.py

import dearpygui.dearpygui as dpg
import os
from utils import constants

def create_main_graph(parent_tag):
    
   # Add some padding from the top
    dpg.add_spacer(height=50, parent=parent_tag)
    
    # Page B content
    with dpg.group(horizontal=False, parent=parent_tag):
        dpg.add_text("Main page", color=[255, 255, 255])
        dpg.add_separator()
        
        dpg.add_text("SUCCESS! Page B is now loaded and visible!", color=[0, 255, 0])
        dpg.add_separator()
        
        dpg.add_spacer(height=20)
        
        # Some interactive elements
        dpg.add_input_text(label="Page B Input", default_value="Type something here...")
        dpg.add_spacer(height=10)
        
        dpg.add_button(label="Page B Action", callback=lambda: print("Page B button clicked!"))
        dpg.add_spacer(height=20)
        
        dpg.add_text("More Page B content:", color=[200, 200, 200])
        dpg.add_text("• Feature 1", color=[150, 150, 255])
        dpg.add_text("• Feature 2", color=[150, 150, 255])
        dpg.add_text("• Feature 3", color=[150, 150, 255])
        
        dpg.add_spacer(height=30)
