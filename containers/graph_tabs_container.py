# containers/graph_tabs_container.py

# This acts as a container for all the graph types tabs  this could be removed later if not used -H

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd
import numpy as np

from utils import constants
from utils.matplotlib_integration import DPGMatplotlibIntegration, create_stock_analysis_page
from utils.plotly_integration import PlotlyInteractiveIntegration, create_interactive_charts_page

# Import them from relative files
from components.graph_dpg import create_main_graph
from components.graph_advanced import create_advanced_analysis_tab
from components.graph_interactive import create_interactive_tab
from components.graph_sankey import create_sankey_tab
# Global variables
current_stock_line_tag = None
matplotlib_helper = None
plotly_helper = None

def create_graph_tabs(parent_tag):
    """
    Enhanced version of main graph page with advanced chart options
    """
    global matplotlib_helper, plotly_helper
    
    print(f"Creating enhanced graph content in parent: {parent_tag}")
    
    # Initialize helpers
    matplotlib_helper = DPGMatplotlibIntegration()
    plotly_helper = PlotlyInteractiveIntegration()
    
    # Create unique identifier for this instance
    timestamp = str(int(time.time() * 1000))
    
    # Create a main container with tabs for different chart types
    main_container_tag = f"enhanced_main_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, tag=main_container_tag, no_scrollbar=False):
        
        # Title
        dpg.add_text("Advanced Stock Analysis Dashboard", color=[255, 255, 255])
        dpg.add_separator()
        dpg.add_spacer(height=10)
        
        # Create tab bar for different chart types
        with dpg.tab_bar(tag=f"chart_tabs_{timestamp}"):
            
            # Tab 1: Original DPG charts
            with dpg.tab(label="DPG Charts"):
                create_main_graph(f"chart_tabs_{timestamp}",timestamp)
            
            # Tab 2: Advanced Pandas/Matplotlib charts
            with dpg.tab(label="Advanced Analysis"):
                create_advanced_analysis_tab(f"chart_tabs_{timestamp}", timestamp)
            
            # Tab 3: Interactive Plotly charts
            with dpg.tab(label="Interactive Charts"):
                create_interactive_tab(f"chart_tabs_{timestamp}", timestamp)
            
            # Tab 4: Sankey Analysis
            with dpg.tab(label="Flow Analysis"):
                create_sankey_tab(f"chart_tabs_{timestamp}", timestamp)






# Cleanup function
def cleanup_chart_helpers():
    """Clean up chart helpers"""
    global matplotlib_helper, plotly_helper
    
    if matplotlib_helper:
        matplotlib_helper.cleanup()
    if plotly_helper:
        plotly_helper.cleanup()

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    cleanup_chart_helpers()
    from .content_container import show_page
    show_page("welcome")