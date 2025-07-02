# components/graph_advanced.py

import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np

from utils import constants

def create_advanced_analysis_tab(parent_tag, timestamp):
    """Advanced analysis with pandas and matplotlib"""
    global matplotlib_helper
    
    dpg.add_spacer(height=20)
    dpg.add_text("Advanced Financial Analysis", color=[200, 200, 255])
    dpg.add_text("Powered by Pandas & Matplotlib", color=[150, 150, 150])
    dpg.add_spacer(height=10)
    
    # Control buttons
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="📊 Generate Advanced Charts",
            callback=lambda: generate_advanced_charts(parent_tag, timestamp),
            width=250, height=40
        )
        dpg.add_spacer(width=20)
        dpg.add_button(
            label="📈 Timeframe Analysis",
            callback=lambda: generate_timeframe_analysis(parent_tag, timestamp),
            width=200, height=40
        )
    
    dpg.add_spacer(height=20)
    
    # Container for generated charts
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, tag=chart_container_tag, border=False):
        dpg.add_text("Click the buttons above to generate advanced analysis charts", 
                    color=[150, 150, 150])
        
        
        
        
def generate_advanced_charts(parent_tag, timestamp):
    """Generate advanced matplotlib charts"""
    global matplotlib_helper
    
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    
    # Clear existing content
    if dpg.does_item_exist(chart_container_tag):
        dpg.delete_item(chart_container_tag, children_only=True)
    
    # Generate new charts
    dpg.add_text("Generating advanced analysis...", parent=chart_container_tag, color=[255, 255, 0])
    
    # Create advanced pandas chart
    matplotlib_helper.create_advanced_pandas_chart(chart_container_tag, width=1000, height=600)
    
    dpg.add_spacer(height=20, parent=chart_container_tag)
    dpg.add_button(label="Refresh Charts", 
                  callback=lambda: generate_advanced_charts(parent_tag, timestamp),
                  parent=chart_container_tag)

def generate_timeframe_analysis(parent_tag, timestamp):
    """Generate timeframe-specific analysis"""
    global matplotlib_helper
    
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    
    # Clear existing content
    if dpg.does_item_exist(chart_container_tag):
        dpg.delete_item(chart_container_tag, children_only=True)
    
    # Create sample timeframe data
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'price': 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, len(dates))))
    })
    
    # Generate timeframe chart
    matplotlib_helper.create_pandas_timeframe_chart(sample_data, chart_container_tag, width=1000, height=400)
    
    dpg.add_spacer(height=20, parent=chart_container_tag)
    dpg.add_text("Timeframe Analysis Complete", parent=chart_container_tag, color=[0, 255, 0])