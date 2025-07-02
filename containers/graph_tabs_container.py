# containers/graph_tabs_container.py

# This acts as a container for all the graph types tabs

import dearpygui.dearpygui as dpg
import random
import time

from utils import constants
from utils.matplotlib_integration import DPGMatplotlibIntegration
from utils.plotly_integration import PlotlyInteractiveIntegration

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
    try:
        matplotlib_helper = DPGMatplotlibIntegration()
        plotly_helper = PlotlyInteractiveIntegration()
    except Exception as e:
        print(f"Warning: Could not initialize chart helpers: {e}")
        matplotlib_helper = None
        plotly_helper = None
    
    # Create unique identifier for this instance
    timestamp = str(int(time.time() * 1000))
    
    # Create unique tags to avoid conflicts
    main_container_tag = f"enhanced_main_container_{timestamp}"
    chart_tabs_tag = f"chart_tabs_{timestamp}"
    
    # Check if container already exists and delete it
    if dpg.does_item_exist(main_container_tag):
        dpg.delete_item(main_container_tag)
    
    try:
        # Create a main container with tabs for different chart types
        with dpg.child_window(
            width=-1, 
            height=-1, 
            parent=parent_tag, 
            tag=main_container_tag, 
            no_scrollbar=False,
            border=False
        ):
            
            # Title
            dpg.add_text("Advanced Stock Analysis Dashboard", color=[255, 255, 255])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Create tab bar for different chart types
            with dpg.tab_bar(tag=chart_tabs_tag):
                
                # Tab 1: Original DPG charts
                with dpg.tab(label="DPG Charts", tag=f"dpg_tab_{timestamp}") as dpg_tab:
                    try:
                        # Pass the tab itself as parent, not the tab bar
                        create_main_graph(dpg_tab, timestamp)
                    except Exception as e:
                        print(f"Error creating DPG charts tab: {e}")
                        dpg.add_text(f"Error loading DPG charts: {e}", color=[255, 0, 0])
                
                # Tab 2: Advanced Pandas/Matplotlib charts
                with dpg.tab(label="Advanced Analysis", tag=f"advanced_tab_{timestamp}") as advanced_tab:
                    try:
                        create_advanced_analysis_tab(advanced_tab, timestamp)
                    except Exception as e:
                        print(f"Error creating advanced analysis tab: {e}")
                        dpg.add_text(f"Error loading advanced analysis: {e}", color=[255, 0, 0])
                
                # Tab 3: Interactive Plotly charts
                with dpg.tab(label="Interactive Charts", tag=f"interactive_tab_{timestamp}") as interactive_tab:
                    try:
                        create_interactive_tab(interactive_tab, timestamp)
                    except Exception as e:
                        print(f"Error creating interactive charts tab: {e}")
                        dpg.add_text(f"Error loading interactive charts: {e}", color=[255, 0, 0])
                
                # Tab 4: Sankey Analysis
                with dpg.tab(label="Flow Analysis", tag=f"sankey_tab_{timestamp}") as sankey_tab:
                    try:
                        create_sankey_tab(sankey_tab, timestamp)
                    except Exception as e:
                        print(f"Error creating sankey tab: {e}")
                        dpg.add_text(f"Error loading flow analysis: {e}", color=[255, 0, 0])
   
    except Exception as e:
        print(f"Error creating graph tabs container: {e}")
        # Fallback to simple content
        dpg.add_text("Error loading enhanced charts", parent=parent_tag, color=[255, 0, 0])
        dpg.add_text(f"Error details: {str(e)}", parent=parent_tag, color=[255, 100, 100])
        

def refresh_tab_data(line_tag):
    """Refresh the data for a specific line chart"""
    try:
        if dpg.does_item_exist(line_tag):
            # Generate new data
            x_data = list(range(50))
            y_data = []
            base_price = random.uniform(90, 110)
            for i in range(50):
                change = random.uniform(-2, 2)
                base_price += change
                y_data.append(max(80, min(120, base_price)))
            
            # Update the line series
            dpg.set_value(line_tag, [x_data, y_data])
            print("Tab chart data refreshed!")
        else:
            print("Chart not found for refresh")
    except Exception as e:
        print(f"Error refreshing tab data: {e}")

def refresh_enhanced_page(parent_tag):
    """Refresh the entire enhanced page"""
    try:
        print("Refreshing enhanced page...")
        from .content_container import show_page
        show_page("enhanced")
    except Exception as e:
        print(f"Error refreshing enhanced page: {e}")

def cleanup_chart_helpers():
    """Clean up chart helpers"""
    global matplotlib_helper, plotly_helper
    
    try:
        if matplotlib_helper:
            matplotlib_helper.cleanup()
        if plotly_helper:
            plotly_helper.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")
