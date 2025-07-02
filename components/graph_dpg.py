# components/graph_dpg.py

import dearpygui.dearpygui as dpg
import math
import random
import time

from utils import constants
# Global variable to track current stock line tag
current_stock_line_tag = None

def create_main_graph(parent_tag, timestamp=None):
    """
    Creates a content page with a graph on top and a table below with demo data.
    Simplified approach to avoid tag conflicts.
    """
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
        
        # Generate demo data for the graph
        x_data = list(range(50))
        y_data = []
        base_price = 100
        for i in range(50):
            change = random.uniform(-2, 2)
            base_price += change
            y_data.append(max(80, min(120, base_price)))
        
        # Create the plot with unique tags - FIXED HEIGHT APPROACH
        plot_tag = f"plot_{timestamp}"
        x_axis_tag = f"x_axis_{timestamp}"
        y_axis_tag = f"y_axis_{timestamp}"
        line_tag = f"stock_line_{timestamp}"
        graph_container_tag = f"graph_container_{timestamp}"
        
        # Use a group to contain the plot with specific dimensions
        with dpg.group():
            with dpg.child_window(width=-1, height=280, tag=graph_container_tag, border=True):
                with dpg.plot(label="", height=-1, width=-1, tag=plot_tag, no_title=True):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag=x_axis_tag)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                    dpg.add_line_series(x_data, y_data, label="AAPL Stock Price", parent=y_axis_tag, tag=line_tag)
                    dpg.set_axis_limits(x_axis_tag, 0, 50)
                    dpg.set_axis_limits(y_axis_tag, 80, 120)
    
        # Store the line tag globally for refresh function
        global current_stock_line_tag
        current_stock_line_tag = line_tag
        
        # Small buttons below the graph this will also hold the tags for each stock
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            
            # Create themes with unique tags
            green_theme_tag = f"green_button_theme_{timestamp}"
            red_theme_tag = f"red_button_theme_{timestamp}"
            
            # Only create themes if they don't exist
            if not dpg.does_item_exist(green_theme_tag):
                with dpg.theme(tag=green_theme_tag):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 128, 0, 255])        # Normal state - green
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 180, 0, 255]) # Hover state - lighter green
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 100, 0, 255])  # Clicked state - darker green
            
            if not dpg.does_item_exist(red_theme_tag):
                with dpg.theme(tag=red_theme_tag):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, [128, 0, 0, 255])        # Normal state - red
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [180, 0, 0, 255]) # Hover state - lighter red
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 0, 0, 255])  # Clicked state - darker red

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

        
        dpg.add_spacer(height=20)
        
        # TABLE SECTION
        dpg.add_text("Stock Portfolio Data", color=[200, 255, 200])
        dpg.add_spacer(height=5)
        
        # Create table with unique tag - FIXED HEIGHT
        table_tag = f"portfolio_table_{timestamp}"
        table_container_tag = f"table_container_{timestamp}"
        
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
                dpg.add_table_column(label="Market Cap", width_fixed=True, init_width_or_weight=120)
                
                # Demo stock data
                demo_stocks = [
                    ("AAPL", "Apple Inc.", 175.43, 2.15, "64.2M", "2.75T"),
                    ("GOOGL", "Alphabet Inc.", 2431.50, -15.23, "1.2M", "1.63T"),
                    ("MSFT", "Microsoft Corp.", 338.25, 5.67, "23.1M", "2.52T"),
                    ("AMZN", "Amazon.com Inc.", 3102.97, -45.12, "3.8M", "1.57T"),
                    ("TSLA", "Tesla Inc.", 248.50, 12.34, "89.5M", "789B"),
                    ("META", "Meta Platforms", 297.55, -8.91, "18.7M", "754B"),
                    ("NVDA", "NVIDIA Corp.", 421.13, 18.76, "45.2M", "1.04T"),
                    ("NFLX", "Netflix Inc.", 384.29, -2.45, "8.9M", "171B"),
                    ("CRM", "Salesforce Inc.", 198.76, 4.23, "5.6M", "196B"),
                    ("PYPL", "PayPal Holdings", 62.85, -1.78, "12.3M", "70.8B")
                ]
                
                # Add table rows
                for symbol, company, price, change, volume, market_cap in demo_stocks:
                    with dpg.table_row():
                        dpg.add_text(symbol)
                        dpg.add_text(company)
                        dpg.add_text(f"${price:.2f}")
                        
                        # Color-coded change
                        change_color = [0, 255, 0] if change >= 0 else [255, 0, 0]
                        change_text = f"+${change:.2f}" if change >= 0 else f"${change:.2f}"
                        dpg.add_text(change_text, color=change_color)
                        
                        dpg.add_text(volume)
                        dpg.add_text(market_cap)
        
        # Action buttons
        dpg.add_spacer(height=15)
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh Data", callback=refresh_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="TSLA Data", callback=refresh_data_from_stockdx_button, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Export CSV", callback=export_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

def plus_button_callback():
    """Callback for the plus button"""
    print("Plus button clicked!")
    # Add your plus button functionality here

def fav_button_callback():
    """Callback for the heart button"""
    print("Heart button clicked!")
    # Add your heart button functionality here

def refresh_data():
    """Refresh the graph data"""
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
    global current_stock_line_tag
    if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
        dpg.set_value(current_stock_line_tag, [x_data, y_data])
        print("Graph data refreshed!")
    else:
        print("Graph not found for refresh")

def refresh_data_from_stockdx_button(user_data):
    """Button callback wrapper for stockdx data"""
    refresh_data_from_stockdx("TSLA")
    
# In your graph_dpg.py, modify the refresh function:
def refresh_data_from_stockdx(symbol="TSLA"):
    """Refresh graph with real stockdx data - improved version"""
    try:
        print(f"Fetching real data for {symbol}...")
        from stockdex import Ticker
        
        ticker = Ticker(ticker=symbol)
        df = ticker.yahoo_api_price(range='1d', dataGranularity='5m')
        
        if df is not None and not df.empty:
            # Convert to DPG format
            x_data = list(range(len(df)))
            y_data = df['close'].tolist()
            
            # Update existing line series
            global current_stock_line_tag
            if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
                dpg.set_value(current_stock_line_tag, [x_data, y_data])
                
                # Update axis limits to fit new data
                if len(y_data) > 0:
                    min_price = min(y_data) * 0.98  # Add some padding
                    max_price = max(y_data) * 1.02
                    
                    # Find the axis tags (you might need to store these globally too)
                    # For now, let's try to find them dynamically
                    for item in dpg.get_all_items():
                        if dpg.get_item_type(item) == "mvAppItemType::mvPlotAxis":
                            if "y_axis" in str(item):
                                dpg.set_axis_limits(item, min_price, max_price)
                            elif "x_axis" in str(item):
                                dpg.set_axis_limits(item, 0, len(x_data))
                
                print(f"✅ Updated chart with real {symbol} data! ({len(df)} points)")
                print(f"   Current price: ${y_data[-1]:.2f}")
            else:
                print("❌ Chart line series not found")
        else:
            print(f"⚠️ No data returned for {symbol}")
            
    except ImportError:
        print("❌ stockdx library not available")
    except Exception as e:
        print(f"❌ Error updating with real data: {e}")

def export_data():
    """Simulate data export"""
    print("Exporting portfolio data to CSV...")
    # In a real application, you would export the table data to a CSV file

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

# Keep the old function for backward compatibility
def create_graph_table_page(parent_tag):
    """Legacy function - redirects to new system"""
    return create_main_graph(parent_tag)