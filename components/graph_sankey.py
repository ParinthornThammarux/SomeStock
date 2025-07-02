# components/graph_sankey.py

import dearpygui.dearpygui as dpg
import random

from utils import constants

def create_sankey_tab(parent_tag, timestamp):
    """Sankey flow analysis tab"""
    global plotly_helper
    
    dpg.add_spacer(height=20)
    dpg.add_text("Financial Flow Analysis", color=[255, 200, 100])
    dpg.add_text("Sankey Diagrams for Cash Flow & Portfolio Analysis", color=[150, 150, 150])
    dpg.add_spacer(height=20)
    
    # Sankey options
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="💰 Cash Flow Analysis",
            callback=lambda: open_cashflow_sankey(),
            width=200, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="🏦 Revenue Breakdown",
            callback=lambda: open_revenue_sankey(),
            width=200, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="📊 Asset Allocation",
            callback=lambda: open_asset_allocation_sankey(),
            width=200, height=50
        )
    
    dpg.add_spacer(height=30)
    
    # Sample data display
    dpg.add_text("Sample Financial Flow Structure:", color=[200, 200, 255])
    
    with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, 
                   borders_innerV=True, borders_outerV=True, height=200):
        dpg.add_table_column(label="Source", width_fixed=True, init_width_or_weight=150)
        dpg.add_table_column(label="Target", width_fixed=True, init_width_or_weight=150)
        dpg.add_table_column(label="Amount ($M)", width_fixed=True, init_width_or_weight=100)
        
        flows = [
            ("Revenue", "Operating Expenses", "800"),
            ("Revenue", "Net Income", "200"),
            ("Operating Expenses", "COGS", "400"),
            ("Operating Expenses", "SG&A", "250"),
            ("Operating Expenses", "R&D", "150"),
            ("Net Income", "Retained Earnings", "120"),
            ("Net Income", "Dividends", "80")
        ]
        
        for source, target, amount in flows:
            with dpg.table_row():
                dpg.add_text(source)
                dpg.add_text(target)
                dpg.add_text(amount, color=[150, 255, 150])

# Callback functions
def plus_button_callback():
    """Callback for the plus button"""
    print("Plus button clicked!")

def fav_button_callback():
    """Callback for the heart button"""
    print("Heart button clicked!")

def refresh_data():
    """Refresh the graph data"""
    global current_stock_line_tag
    print("Refreshing stock data...")
    
    # Generate new data
    x_data = list(range(50))
    y_data = []
    base_price = random.uniform(90, 110)
    for i in range(50):
        change = random.uniform(-2, 2)
        base_price += change
        y_data.append(max(80, min(120, base_price)))
    
    # Update the line series
    if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
        dpg.set_value(current_stock_line_tag, [x_data, y_data])
        print("Graph data refreshed!")
    else:
        print("Graph not found for refresh")



def open_cashflow_sankey():
    """Open cash flow Sankey diagram"""
    global plotly_helper
    filepath = plotly_helper.create_interactive_sankey()
    plotly_helper.open_in_browser(filepath)
    print(f"Opened cash flow Sankey: {filepath}")

def open_revenue_sankey():
    """Open revenue breakdown Sankey"""
    global plotly_helper
    
    # Custom revenue data
    revenue_data = {
        'labels': [
            'Total Revenue', 'Product Sales', 'Services', 'Subscriptions',
            'North America', 'Europe', 'Asia Pacific', 'Other',
            'Enterprise', 'Consumer', 'Government'
        ],
        'sources': [0, 0, 0, 1, 1, 1, 1, 2, 2, 2],
        'targets': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'values': [700, 200, 100, 300, 250, 100, 50, 120, 60, 20]
    }
    
    filepath = plotly_helper.create_interactive_sankey(revenue_data)
    plotly_helper.open_in_browser(filepath)
    print(f"Opened revenue Sankey: {filepath}")

def open_asset_allocation_sankey():
    """Open asset allocation Sankey"""
    global plotly_helper
    
    # Asset allocation data
    asset_data = {
        'labels': [
            'Portfolio', 'Equities', 'Bonds', 'Alternatives',
            'US Stocks', 'International', 'Emerging Markets',
            'Government Bonds', 'Corporate Bonds', 'REITs', 'Commodities'
        ],
        'sources': [0, 0, 0, 1, 1, 1, 2, 2, 3, 3],
        'targets': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'values': [600, 300, 100, 350, 150, 100, 200, 100, 60, 40]
    }
    
    filepath = plotly_helper.create_interactive_sankey(asset_data)
    plotly_helper.open_in_browser(filepath)
    print(f"Opened asset allocation Sankey: {filepath}")