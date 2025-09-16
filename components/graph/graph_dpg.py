# components/graph/graph_dpg.py

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from components.stock.stock_data_manager import restore_tags_to_container

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock_search import create_stock_search

# Global variables to track current chart components
current_stock_line_tag = None
current_x_axis_tag = None
current_y_axis_tag = None
current_plot_tag = None
current_table_tag = None
current_period_combo_tag = None
current_interval_combo_tag = None

# Thread lock for table operations
table_lock = threading.Lock()

def create_main_graph(parent_tag, timestamp=None):
    """
    Creates a content page with a graph on top and a table below.
    Now works with the new caching system and prevents duplicates.
    """
    # GLOBAL DECLARATION MUST BE FIRST IN FUNCTION
    global current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag, current_table_tag
    
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
    
        # Controls section with dropdowns
        dpg.add_spacer(height=5)

        # Period and Interval selectors
        with dpg.group(horizontal=True):
            dpg.add_text("Period:", color=[200, 200, 200])
            dpg.add_spacer(width=5)

            period_combo_tag = f"period_combo_{timestamp}"
            dpg.add_combo(
                ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                default_value="1y",
                width=80,
                tag=period_combo_tag,
                callback=on_period_interval_change
            )

            dpg.add_spacer(width=20)
            dpg.add_text("Interval:", color=[200, 200, 200])
            dpg.add_spacer(width=5)

            interval_combo_tag = f"interval_combo_{timestamp}"
            dpg.add_combo(
                ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
                default_value="1d",
                width=80,
                tag=interval_combo_tag,
                callback=on_period_interval_change
            )

            # Store combo tags globally for access
            global current_period_combo_tag, current_interval_combo_tag
            current_period_combo_tag = period_combo_tag
            current_interval_combo_tag = interval_combo_tag

            dpg.add_spacer(width=20)
            dpg.add_button(
                label="Apply",
                callback=apply_period_interval_changes,
                width=60,
                height=25
            )

        dpg.add_spacer(height=8)

        # Small buttons below the graph - this holds the stock tags
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=True, tag='tags_container'):
                dpg.add_spacer(width=-1)
            restore_tags_to_container('tags_container')
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
        table_tag = f"portfolio_table_{timestamp}"
        table_container_tag = f"table_container_{timestamp}"
        
        # Store table tag globally
        current_table_tag = table_tag
        
        with dpg.child_window(width=-1, height=-1, tag=table_container_tag, border=False):
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
            dpg.add_button(label="Clear Table", callback=clear_table, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

    # Auto-repopulate table on page load
    _auto_repopulate_table_on_load()

def _auto_repopulate_table_on_load():
    """Auto-repopulate the stock table on page load using cached data or refetch if expired"""
    try:
        print("🔄 Auto-repopulating stock table on page load...")

        from components.stock.stock_data_manager import get_all_stock_tags, get_cached_stock_data

        # Get all existing stock tags from cache
        stock_tags = get_all_stock_tags()

        if not stock_tags:
            print("📋 No cached stocks found, table will remain empty")
            return

        repopulated_count = 0
        expired_count = 0

        # Process each cached stock
        for stock_tag in stock_tags:
            try:
                symbol = stock_tag.symbol
                print(f"📦 Processing cached stock: {symbol}")

                # Check if cache is valid for this stock
                cached_data = get_cached_stock_data(symbol, f"{symbol} Corp.", "1y", "1d")

                if cached_data and cached_data.is_cache_valid():
                    # Cache is valid, add directly to table
                    print(f"✅ Using valid cache for {symbol}")
                    add_stock_to_portfolio_table(symbol)
                    repopulated_count += 1
                else:
                    # Cache is expired, trigger refresh in background
                    print(f"🔄 Cache expired for {symbol}, triggering refresh...")
                    expired_count += 1

                    # Start background thread to refetch data
                    def refresh_expired_stock(sym):
                        try:
                            from utils.stock_fetch_layer import fetch_stock_data
                            fetch_stock_data(sym, None, None, None, None, period="1y", interval="1d")

                            # Add to table after refresh (with small delay to ensure data is cached)
                            import time
                            time.sleep(2)
                            add_stock_to_portfolio_table(sym)
                            print(f"✅ Refreshed and added {sym} to table")
                        except Exception as e:
                            print(f"❌ Error refreshing expired stock {sym}: {e}")

                    import threading
                    refresh_thread = threading.Thread(target=refresh_expired_stock, args=(symbol,))
                    refresh_thread.daemon = True
                    refresh_thread.start()

            except Exception as e:
                print(f"❌ Error processing stock {stock_tag.symbol}: {e}")
                continue

        if repopulated_count > 0:
            print(f"✅ Auto-repopulated table with {repopulated_count} stocks from cache")
        if expired_count > 0:
            print(f"🔄 Refreshing {expired_count} expired stocks in background")

        if repopulated_count == 0 and expired_count == 0:
            print("📋 No valid cached stocks found for repopulation")

    except Exception as e:
        print(f"❌ Error in auto-repopulation: {e}")
        import traceback
        traceback.print_exc()

def plus_button_callback():
    """Open stock search dialog with current period/interval settings"""
    global current_period_combo_tag, current_interval_combo_tag

    print("Plus button clicked!")

    # Get current period and interval from dropdowns
    period = "1y"  # Default fallback
    interval = "1d"  # Default fallback

    try:
        if current_period_combo_tag and dpg.does_item_exist(current_period_combo_tag):
            period = dpg.get_value(current_period_combo_tag)
        if current_interval_combo_tag and dpg.does_item_exist(current_interval_combo_tag):
            interval = dpg.get_value(current_interval_combo_tag)

        # Validate the combination
        period, interval = validate_period_interval_combination(period, interval)
        print(f"📊 Using period: {period}, interval: {interval} for new stock")

    except Exception as e:
        print(f"⚠️ Error getting period/interval, using defaults: {e}")

    create_stock_search(
        mode="chart",
        line_tag=current_stock_line_tag,
        x_axis_tag=current_x_axis_tag,
        y_axis_tag=current_y_axis_tag,
        plot_tag=current_plot_tag,
        period=period,
        interval=interval
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

def clear_table():
    """Clear all entries from the table"""
    global current_table_tag, table_lock
    
    with table_lock:
        try:
            if not current_table_tag or not dpg.does_item_exist(current_table_tag):
                print("❌ Table not found")
                return
            
            # Get table children (rows)
            children = dpg.get_item_children(current_table_tag, slot=1)  # slot 1 = table rows
            if children:
                for row_id in children:
                    if dpg.get_item_type(row_id) == "mvAppItemType::mvTableRow":
                        dpg.delete_item(row_id)
            
            print("✅ Table cleared")
            
        except Exception as e:
            print(f"❌ Error clearing table: {e}")

def symbol_exists_in_table(symbol):
    """Thread-safe check if symbol already exists in the portfolio table"""
    global current_table_tag, table_lock
    
    with table_lock:
        try:
            if not current_table_tag or not dpg.does_item_exist(current_table_tag):
                return False
            
            # Get table children (rows)
            children = dpg.get_item_children(current_table_tag, slot=1)  # slot 1 = table rows
            if not children:
                return False
            
            # Check each row for the symbol
            for row_id in children:
                if dpg.get_item_type(row_id) == "mvAppItemType::mvTableRow":
                    row_children = dpg.get_item_children(row_id, slot=1)
                    if row_children and len(row_children) > 0:
                        # First cell should contain the symbol
                        first_cell = row_children[0]
                        if dpg.does_item_exist(first_cell):
                            cell_value = dpg.get_value(first_cell)
                            if cell_value == symbol:
                                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking table for symbol {symbol}: {e}")
            return False

def refresh_table_data():
    """Refresh all table data from cache - THREAD SAFE"""
    global current_table_tag, table_lock
    
    with table_lock:
        try:
            if not current_table_tag or not dpg.does_item_exist(current_table_tag):
                print("❌ Table not found")
                return
            
            # Clear existing table data (keep headers)
            children = dpg.get_item_children(current_table_tag, slot=1)  # slot 1 = table rows
            if children:
                for row_id in children:
                    if dpg.get_item_type(row_id) == "mvAppItemType::mvTableRow":
                        dpg.delete_item(row_id)
            
            # Repopulate with all stocks
            from components.stock.stock_data_manager import get_all_stock_tags
            
            stock_tags = get_all_stock_tags()
            for tag in stock_tags:
                _add_stock_to_table_internal(tag.symbol)
            
            print(f"✅ Table refreshed with {len(stock_tags)} stocks")
            
        except Exception as e:
            print(f"❌ Error refreshing table: {e}")

def add_stock_to_portfolio_table(symbol):
    """Public interface - Add a stock row to the portfolio table using cached data - THREAD SAFE"""
    global table_lock
    
    with table_lock:
        try:
            # Check if symbol already exists
            if symbol_exists_in_table(symbol):
                print(f"📋 {symbol} already exists in table, skipping addition")
                return
            
            _add_stock_to_table_internal(symbol)
            print(f"✅ Added {symbol} to table (thread-safe)")
            
        except Exception as e:
            print(f"❌ Failed to add {symbol} to table: {e}")

def _add_stock_to_table_internal(symbol):
    """Internal function to add stock to table - assumes lock is held"""
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
        
    except Exception as e:
        print(f"❌ Internal error adding {symbol} to table: {e}")
        import traceback
        traceback.print_exc()

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
                    'Yes' if tag.is_favorite() else 'No'
                ])
        
        print(f"✅ Portfolio exported to {filename}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

def validate_period_interval_combination(period, interval):
    """
    Validate and auto-correct period/interval combinations
    Ensures: Interval Cannot be bigger than Period

    Args:
        period (str): The range of the price data to retrieve
        valid values are "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        interval (str): The granularity of the data to retrieve (interval)
        valid values are "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"

    Returns:
        tuple: (corrected_period, corrected_interval)
    """
    # Convert periods and intervals to minutes for comparison
    time_to_minutes = {
        # Intervals
        "1m": 1, "2m": 2, "5m": 5, "15m": 15, "30m": 30,
        "60m": 60, "90m": 90, "1h": 60,
        "1d": 1440, "5d": 7200, "1wk": 10080, "1mo": 43200, "3mo": 129600,
        # Periods (approximate durations)
        "1d": 1440,      # 1 day = 1440 minutes
        "5d": 7200,      # 5 days = 7200 minutes
        "1mo": 43200,    # 1 month = 30 days = 43200 minutes
        "3mo": 129600,   # 3 months = 90 days = 129600 minutes
        "6mo": 259200,   # 6 months = 180 days = 259200 minutes
        "1y": 525600,    # 1 year = 365 days = 525600 minutes
        "2y": 1051200,   # 2 years = 730 days = 1051200 minutes
        "5y": 2628000,   # 5 years = 1825 days = 2628000 minutes
        "10y": 5256000,  # 10 years = 3650 days = 5256000 minutes
        "ytd": 262800,   # YTD = ~6 months = 262800 minutes
        "max": 10512000  # Max = ~20 years = 10512000 minutes
    }

    # Define period to minimum interval mapping (API limitations)
    period_min_intervals = {
        "1d": "1m",     # 1 day can use minute intervals
        "5d": "1m",     # 5 days can use minute intervals
        "1mo": "30m",   # 1 month minimum 30min
        "3mo": "1h",    # 3 months minimum 1 hour
        "6mo": "1d",    # 6 months minimum 1 day
        "1y": "1d",     # 1 year minimum 1 day
        "2y": "1d",     # 2 years minimum 1 day
        "5y": "1wk",    # 5 years minimum 1 week
        "10y": "1wk",   # 10 years minimum 1 week
        "ytd": "1d",    # Year to date minimum 1 day
        "max": "1wk"    # Max period minimum 1 week
    }

    period_minutes = time_to_minutes.get(period, 525600)  # Default to 1 year
    interval_minutes = time_to_minutes.get(interval, 1440)  # Default to 1 day

    # Rule 1: Interval Cannot be bigger than Period
    if interval_minutes > period_minutes:
        # Find the largest valid interval that's smaller than or equal to period
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        corrected_interval = "1d"  # Default fallback

        for valid_interval in reversed(valid_intervals):  # Start from largest
            if time_to_minutes.get(valid_interval, 1440) <= period_minutes:
                corrected_interval = valid_interval
                break

        print(f"⚠️ Interval {interval} is bigger than period {period}! Auto-corrected to {corrected_interval}")
        interval = corrected_interval
        interval_minutes = time_to_minutes.get(interval, 1440)

    # Rule 2: Check API minimum interval requirements
    min_interval = period_min_intervals.get(period, "1d")
    min_interval_mins = time_to_minutes.get(min_interval, 1440)

    if interval_minutes < min_interval_mins:
        corrected_interval = min_interval
        print(f"⚠️ Auto-corrected interval from {interval} to {corrected_interval} (API minimum for period {period})")
        return period, corrected_interval

    return period, interval

def on_period_interval_change(sender, app_data, user_data):
    """Callback when period or interval dropdown changes"""
    global current_period_combo_tag, current_interval_combo_tag

    try:
        # Get current values from both dropdowns
        if current_period_combo_tag and current_interval_combo_tag:
            period = dpg.get_value(current_period_combo_tag)
            interval = dpg.get_value(current_interval_combo_tag)

            # Validate the combination
            corrected_period, corrected_interval = validate_period_interval_combination(period, interval)

            # If interval was auto-corrected, update the dropdown immediately
            if corrected_interval != interval:
                print(f"🔄 Auto-updating interval dropdown from {interval} to {corrected_interval}")
                dpg.set_value(current_interval_combo_tag, corrected_interval)
                print(f"✅ Corrected combination: {period} + {corrected_interval}")
            else:
                print(f"✅ Valid combination: {period} + {interval}")

    except Exception as e:
        print(f"⚠️ Error validating period/interval: {e}")

def apply_period_interval_changes():
    """Apply the selected period and interval to refresh all stocks"""
    global current_period_combo_tag, current_interval_combo_tag

    try:
        if not current_period_combo_tag or not current_interval_combo_tag:
            print("❌ Dropdown tags not found")
            return

        period = dpg.get_value(current_period_combo_tag)
        interval = dpg.get_value(current_interval_combo_tag)

        # Validate and auto-correct the combination
        corrected_period, corrected_interval = validate_period_interval_combination(period, interval)

        # Update the UI if correction was made
        if corrected_interval != interval:
            dpg.set_value(current_interval_combo_tag, corrected_interval)
            interval = corrected_interval

        print(f"🔄 Applying period: {period}, interval: {interval}")

        # Get all active stock tags
        from components.stock.stock_data_manager import get_all_stock_tags
        stock_tags = get_all_stock_tags()

        if not stock_tags:
            print("📋 No stocks to refresh with new parameters")
            return

        # Refresh each stock with new period/interval
        for tag in stock_tags:
            try:
                print(f"🔄 Refreshing {tag.symbol} with {period}/{interval}")

                # Fetch new data with updated parameters
                fetch_stock_data(
                    tag.symbol,
                    current_stock_line_tag,
                    current_x_axis_tag,
                    current_y_axis_tag,
                    current_plot_tag,
                    period=period,
                    interval=interval
                )

                time.sleep(0.5)  # Small delay between requests

            except Exception as e:
                print(f"❌ Error refreshing {tag.symbol}: {e}")

        # Refresh the table to show updated data
        refresh_table_data()

        print(f"✅ Applied {period}/{interval} to {len(stock_tags)} stocks")

    except Exception as e:
        print(f"❌ Error applying period/interval changes: {e}")

# Keep the old function for backward compatibility
def create_graph_table_page(parent_tag):
    """Legacy function - redirects to new system"""
    return create_main_graph(parent_tag)

