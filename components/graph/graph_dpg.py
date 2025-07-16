# components/graph_dpg.py

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock_search import create_stock_search

# Global variables to track current chart components
current_stock_line_tag = None
current_x_axis_tag = None
current_y_axis_tag = None
current_plot_tag = None

def create_main_graph(parent_tag, timestamp=None):
    """
    Creates a content page with a graph on top and a table below.
    Now works with the new caching system.
    """
    # GLOBAL DECLARATION MUST BE FIRST IN FUNCTION
    global current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
    
    print(f"Creating graph and table content in parent: {parent_tag}")
    
    # Create unique identifier for this instance
    if timestamp is None:
        timestamp = str(int(time.time() * 1000))
    
    # Create a main container with proper height management
    main_container_tag = f"main_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, tag=main_container_tag, no_scrollbar=False):

        # GRAPH SECTION - Fixed height container
        dpg.add_text("Stock Price Chart", color=[200, 200, 255])
        dpg.add_spacer(height=5)
        
        x_data = []
        y_data = []
        
        # Create the plot with unique tags - STORE ALL TAGS GLOBALLY
        plot_tag = f"plot_{timestamp}"
        x_axis_tag = f"x_axis_{timestamp}"
        y_axis_tag = f"y_axis_{timestamp}"
        line_tag = f"stock_line_{timestamp}"
        graph_container_tag = f"graph_container_{timestamp}"
        
        # Store tags globally for later access
        current_plot_tag = plot_tag
        current_x_axis_tag = x_axis_tag
        current_y_axis_tag = y_axis_tag
        current_stock_line_tag = line_tag
        
        print(f"📋 Created tags - Plot: {plot_tag}, X-axis: {x_axis_tag}, Y-axis: {y_axis_tag}, Line: {line_tag}")
        
        # Use a group to contain the plot with specific dimensions
        with dpg.group():
            with dpg.child_window(width=-1, height=300, tag=graph_container_tag, border=True):
                with dpg.plot(label="", height=-1, width=-1, tag=plot_tag, no_title=True):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag=x_axis_tag)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                    dpg.add_line_series(x_data, y_data, parent=y_axis_tag, tag=line_tag)
                    dpg.set_axis_limits(x_axis_tag, 0, 50)
                    dpg.set_axis_limits(y_axis_tag, 80, 120)
    
        # Small buttons below the graph - this holds the stock tags
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=True, tag='tags_container'):
                dpg.add_spacer(width=-1)
            with dpg.group(horizontal=True):
                # Create themes with unique tags
                green_theme_tag = f"green_button_theme_{timestamp}"
                red_theme_tag = f"red_button_theme_{timestamp}"
                
                # Only create themes if they don't exist
                if not dpg.does_item_exist(green_theme_tag):
                    with dpg.theme(tag=green_theme_tag):
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 128, 0, 255])
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 180, 0, 255])
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 100, 0, 255])
                
                if not dpg.does_item_exist(red_theme_tag):
                    with dpg.theme(tag=red_theme_tag):
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, [128, 0, 0, 255])
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [180, 0, 0, 255])
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 0, 0, 255])

                add_stock_btn_tag = f"add_stock_button_{timestamp}"
                add_fav_btn_tag = f"add_fav_stock_button_{timestamp}"
                
                dpg.add_button(tag=add_stock_btn_tag, label=constants.ICON_PLUS, width=30, height=30, callback=plus_button_callback)
                if constants.font_awesome_icon_font_id:
                    dpg.bind_item_font(add_stock_btn_tag, constants.font_awesome_icon_font_id)
                dpg.bind_item_theme(add_stock_btn_tag, green_theme_tag)
                
                # Heart button
                dpg.add_button(tag=add_fav_btn_tag, label=constants.ICON_HEART, width=30, height=30, callback=fav_button_callback)
                if constants.font_awesome_icon_font_id:
                    dpg.bind_item_font(add_fav_btn_tag, constants.font_awesome_icon_font_id)
                dpg.bind_item_theme(add_fav_btn_tag, red_theme_tag)

        dpg.add_spacer(height=10)
        
        # TABLE SECTION
        dpg.add_text("Stock Portfolio Data", color=[200, 255, 200])
        dpg.add_spacer(height=5)
        
        # Create table with unique tag
        global table_tag
        table_tag = f"portfolio_table_{timestamp}"
        table_container_tag = f"table_container_{timestamp}"
        
        with dpg.child_window(width=-1, height=-1, tag=table_container_tag, border=False):
            global current_table_tag
            current_table_tag = table_tag
            with dpg.table(
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                tag=table_tag,
                height=-1,
                scrollY=False
            ):
                # Table columns
                dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Company", width_fixed=True, init_width_or_weight=200)
                dpg.add_table_column(label="Price", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Change", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Volume", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Revenue", width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column(label="Net Income", width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column(label="Cash Flow", width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column(label="Cache", width_fixed=True, init_width_or_weight=80)  # New cache status column
                
        # Action buttons
        dpg.add_spacer(height=15)
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh Data", callback=refresh_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Refresh All Cache", callback=refresh_all_cache, width=150)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Save Cache", callback=save_cache, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Export CSV", callback=export_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

def plus_button_callback():
    """Open stock search dialog"""
    print("Plus button clicked!")
    create_stock_search(
        current_stock_line_tag,
        current_x_axis_tag,
        current_y_axis_tag,
        current_plot_tag
    )

def fav_button_callback():
    """Heart button callback"""
    print("Heart button clicked!")
    # Show favorited stocks
    from components.stock.stock_data_manager import get_favorited_stocks
    favorites = get_favorited_stocks()
    print(f"Favorited stocks: {favorites}")

def refresh_data():
    """Refresh the graph with random data"""
    global current_stock_line_tag, current_x_axis_tag, current_y_axis_tag
    
    print("Refreshing stock data...")
    
    # Generate new data
    x_data = list(range(50))
    y_data = []
    base_price = random.uniform(90, 110)
    for i in range(50):
        change = random.uniform(-2, 2)
        base_price += change
        y_data.append(max(80, min(120, base_price)))
    
    # Update the line series using stored tag
    if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
        dpg.set_value(current_stock_line_tag, [x_data, y_data])
        
        # Update axis limits using stored tags
        if current_x_axis_tag and dpg.does_item_exist(current_x_axis_tag):
            dpg.set_axis_limits(current_x_axis_tag, 0, 50)
        if current_y_axis_tag and dpg.does_item_exist(current_y_axis_tag):
            dpg.set_axis_limits(current_y_axis_tag, 80, 120)
            
        print("Graph data refreshed!")
    else:
        print("Graph not found for refresh")

def refresh_all_cache():
    """Refresh cache for all stocks"""
    print("🔄 Refreshing all cached stock data...")
    
    try:
        from components.stock.stock_data_manager import get_all_stock_tags
        
        stock_tags = get_all_stock_tags()
        
        if not stock_tags:
            print("📋 No stocks to refresh")
            return
        
        for tag in stock_tags:
            try:
                print(f"🔄 Refreshing {tag.symbol}...")
                tag.refresh_data()
                time.sleep(0.1)  # Small delay to avoid overwhelming the API
            except Exception as e:
                print(f"❌ Error refreshing {tag.symbol}: {e}")
        
        # Refresh the table
        refresh_table_data()
        
        print(f"✅ Refreshed cache for {len(stock_tags)} stocks")
        
    except Exception as e:
        print(f"❌ Error refreshing all cache: {e}")

def save_cache():
    """Save cache to file"""
    try:
        from components.stock.stock_data_manager import save_cache_to_file, cleanup_cache
        
        cleanup_cache()  # Clean up old entries first
        save_cache_to_file()
        
        print("✅ Cache saved successfully")
        
    except Exception as e:
        print(f"❌ Error saving cache: {e}")

def refresh_table_data():
    """Refresh all table data from cache"""
    global current_table_tag
    
    try:
        if not current_table_tag or not dpg.does_item_exist(current_table_tag):
            print("❌ Table not found")
            return
        
        # Clear existing table data
        dpg.delete_item(current_table_tag, children_only=True)
        
        # Recreate table columns
        dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80, parent=current_table_tag)
        dpg.add_table_column(label="Company", width_fixed=True, init_width_or_weight=200, parent=current_table_tag)
        dpg.add_table_column(label="Price", width_fixed=True, init_width_or_weight=100, parent=current_table_tag)
        dpg.add_table_column(label="Change", width_fixed=True, init_width_or_weight=100, parent=current_table_tag)
        dpg.add_table_column(label="Volume", width_fixed=True, init_width_or_weight=100, parent=current_table_tag)
        dpg.add_table_column(label="Revenue", width_fixed=True, init_width_or_weight=120, parent=current_table_tag)
        dpg.add_table_column(label="Net Income", width_fixed=True, init_width_or_weight=120, parent=current_table_tag)
        dpg.add_table_column(label="Cash Flow", width_fixed=True, init_width_or_weight=120, parent=current_table_tag)
        dpg.add_table_column(label="Cache", width_fixed=True, init_width_or_weight=80, parent=current_table_tag)
        
        # Repopulate with all stocks
        from components.stock.stock_data_manager import get_all_stock_tags
        
        stock_tags = get_all_stock_tags()
        for tag in stock_tags:
            add_stock_to_portfolio_table(tag.symbol)
        
        print(f"✅ Table refreshed with {len(stock_tags)} stocks")
        
    except Exception as e:
        print(f"❌ Error refreshing table: {e}")

def export_data():
    """Export portfolio data to CSV"""
    try:
        from components.stock.stock_data_manager import stock_data_cache, get_all_stock_tags
        import csv
        import datetime
        
        # Get current timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_export_{timestamp}.csv"
        
        # Get all active stocks
        stock_tags = get_all_stock_tags()
        
        if not stock_tags:
            print("❌ No stocks to export")
            return
        
        # Create CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Symbol', 'Company', 'Current Price', 'Change', 'Change %', 
                'Volume', 'Revenue', 'Net Income', 'Cash Flow', 'Last Updated', 
                'Cache Status', 'Favorited'
            ])
            
            # Write data for each stock
            for tag in stock_tags:
                stock_data = tag.get_stock_data()
                
                writer.writerow([
                    stock_data.symbol,
                    stock_data.company_name,
                    stock_data.current_price or 'N/A',
                    stock_data.change or 'N/A',
                    f"{stock_data.change_percent:.2f}%" if stock_data.change_percent else 'N/A',
                    stock_data.volume or 'N/A',
                    stock_data.revenue or 'N/A',
                    stock_data.net_income or 'N/A',
                    stock_data.cash_flow or 'N/A',
                    datetime.datetime.fromtimestamp(stock_data.last_updated).strftime("%Y-%m-%d %H:%M:%S") if stock_data.last_updated else 'N/A',
                    'Valid' if stock_data.is_cache_valid() else 'Expired',
                    'Yes' if tag.get_favorite_status() else 'No'
                ])
        
        print(f"✅ Portfolio exported to {filename}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

def add_stock_to_portfolio_table(symbol):
    """Add a stock row to the portfolio table using cached data"""
    global current_table_tag
    
    try:
        if not current_table_tag or not dpg.does_item_exist(current_table_tag):
            print("❌ Portfolio table not found")
            return
        
        # Get cached data
        from components.stock.stock_data_manager import get_stock_data_for_table
        
        data = get_stock_data_for_table(symbol)
        
        if not data:
            print(f"❌ No data available for {symbol}")
            return
        
        # Add new row to the table
        with dpg.table_row(parent=current_table_tag):
            dpg.add_text(data['symbol'])
            dpg.add_text(data['company_name'][:20] + "..." if len(data['company_name']) > 20 else data['company_name'])
            dpg.add_text(data['current_price'])
            dpg.add_text(data['change'], color=data['change_color'])
            dpg.add_text(data['volume'])
            dpg.add_text(data['revenue'])
            
            # Color-code net income
            ni_color = [255, 255, 255]  # Default white
            if data['net_income'] != "N/A":
                if not data['net_income'].startswith("-"):
                    ni_color = [0, 255, 0]  # Green for positive
                else:
                    ni_color = [255, 0, 0]  # Red for negative
            
            dpg.add_text(data['net_income'], color=ni_color)
            dpg.add_text(data['cash_flow'])
            
            # Cache status indicator
            cache_status = "Fresh" if data['is_cached'] else "Stale"
            cache_color = [0, 255, 0] if data['is_cached'] else [255, 150, 0]
            dpg.add_text(cache_status, color=cache_color)
        
        print(f"✅ Added {symbol} to table with cached data")
        
    except Exception as e:
        print(f"❌ Failed to add {symbol} to table: {e}")
        import traceback
        traceback.print_exc()

# Keep the old function for backward compatibility
def create_graph_table_page(parent_tag):
    """Legacy function - redirects to new system"""
    return create_main_graph(parent_tag)