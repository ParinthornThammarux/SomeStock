# components/graph_dpg.py

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd

from utils import constants
from utils.stockdex_layer import fetch_data_from_stockdx
from components.stock_search import create_stock_search
# Global variables to track current chart components - MOVED TO TOP
current_stock_line_tag = None
current_x_axis_tag = None
current_y_axis_tag = None
current_plot_tag = None

def create_main_graph(parent_tag, timestamp=None):
    """
    Creates a content page with a graph on top and a table below with demo data.
    Simplified approach to avoid tag conflicts.
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
    
        # Small buttons below the graph this will also hold the tags for each stock
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

        # DEBUG BUTTONS - Add these for troubleshooting
        dpg.add_spacer(height=10)
        
        # TABLE SECTION
        dpg.add_text("Stock Portfolio Data", color=[200, 255, 200])
        dpg.add_spacer(height=5)
        
        # Create table with unique tag - FIXED HEIGHT
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
                # NEW TABLE COLUMNS - Updated to match stockdx data
                dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Company", width_fixed=True, init_width_or_weight=200)
                dpg.add_table_column(label="Price", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Change", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Volume", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Revenue", width_fixed=True, init_width_or_weight=120)  # From income statement
                dpg.add_table_column(label="Net Income", width_fixed=True, init_width_or_weight=120)  # From income statement
                dpg.add_table_column(label="Cash Flow", width_fixed=True, init_width_or_weight=120)  # From cash flow
                
        # Action buttons
        dpg.add_spacer(height=15)
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Random Data", callback=refresh_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="TSLA Data", callback=refresh_data_from_stockdx_button, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Export CSV", callback=export_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

def plus_button_callback():
    print("Plus button clicked!")
    create_stock_search(
        current_stock_line_tag,
        current_x_axis_tag,
        current_y_axis_tag,
        current_plot_tag
    )

def fav_button_callback():
    print("Heart button clicked!")
    # Add your heart button functionality here

def refresh_data():
    """Refresh the graph data"""
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

def refresh_data_from_stockdx_button(user_data):
    """Button callback wrapper for stockdx data"""
    fetch_data_from_stockdx("CPALL.BK")



def simple_debug_plot(df, symbol):
    """Super simple matplotlib plot - just for debugging"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import tkinter as tk
        from PIL import Image, ImageTk
        import io
        import threading
        
        def create_plot():
            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.plot(df['close'])
            plt.title(f'{symbol} - Close Prices (Debug)')
            plt.ylabel('Price')
            plt.xlabel('Data Points')
            plt.grid(True)
            
            # Save to memory instead of showing
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()  # Close the figure to free memory
            
            # Display in tkinter window
            root = tk.Tk()
            root.title(f"{symbol} Debug Plot")
            
            # Load image
            image = Image.open(buffer)
            photo = ImageTk.PhotoImage(image)
            
            # Display image
            label = tk.Label(root, image=photo)
            label.pack()
            
            # Close button
            close_btn = tk.Button(root, text="Close", command=root.destroy, 
                                font=('Arial', 10), padx=20, pady=5)
            close_btn.pack(pady=10)
            
            # Keep reference to prevent garbage collection
            label.image = photo
            
            root.mainloop()
        
        # Run in thread
        thread = threading.Thread(target=create_plot, daemon=True)
        thread.start()
        print(f"✅ Simple debug plot opened for {symbol}")
        
    except Exception as e:
        print(f"❌ Error creating debug plot: {e}")
        # Fallback: just print some basic info
        print(f"Plot fallback - Close prices range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
        print(f"Latest price: ${df['close'].iloc[-1]:.2f}")

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

def add_stock_to_portfolio_table(symbol):
    """Add a new stock row to the portfolio table using Yahoo API data"""
    global current_table_tag
    
    try:
        if not current_table_tag or not dpg.does_item_exist(current_table_tag):
            print("❌ Portfolio table not found")
            return
        
        # Get company name from the stock tag
        from components.stock_tag import find_tag_by_name
        stock_tag = find_tag_by_name(symbol)
        company_name = stock_tag.get_company_name() if stock_tag else f"{symbol} Corp."
        
        from stockdex import Ticker
        from datetime import datetime
        import pandas as pd
        ticker = Ticker(ticker=symbol)
        
        print(f"📊 Fetching Yahoo API data for {symbol} ({company_name})...")
        
        # Get current price data (includes volume) - FIXED: Use longer range for better data
        price_data = ticker.yahoo_api_price(range='5d', dataGranularity='1d')
        
        if price_data is None or price_data.empty:
            print(f"❌ No price data available for {symbol}")
            return
            
        # FIXED: Better volume extraction with debug info
        print(f"📊 Price data columns: {price_data.columns.tolist()}")
        print(f"📊 Price data shape: {price_data.shape}")
        
        # Extract price and volume data
        current_price = price_data['close'].iloc[-1]
        
        # FIXED: Better volume handling
        volume = 0
        if 'volume' in price_data.columns:
            volume_series = price_data['volume']
            # Get the most recent non-null volume
            non_null_volumes = volume_series.dropna()
            if not non_null_volumes.empty:
                volume = non_null_volumes.iloc[-1]
                print(f"📊 Volume found: {volume:,}")
            else:
                print("⚠️ No valid volume data found")
        else:
            print("⚠️ Volume column not found in price data")
        
        # Calculate change
        if len(price_data) > 1:
            previous_price = price_data['close'].iloc[-2]
            change = current_price - previous_price
        else:
            change = 0
        
        # Initialize financial metrics
        revenue = "N/A"
        net_income = "N/A"
        cash_flow_value = "N/A"
        
        # Get fundamental data using Yahoo API
        try:
            print(f"📋 Fetching Yahoo API fundamental data for {symbol}...")
            
            # Get quarterly financial data
            income_statement = ticker.yahoo_api_income_statement(frequency='quarterly', format='raw')
            cash_flow = ticker.yahoo_api_cash_flow(frequency='quarterly', format='raw')
            
            # Extract Revenue (Total Revenue)
            if income_statement is not None and not income_statement.empty:
                if 'quarterlyTotalRevenue' in income_statement.columns:
                    print("✅ Found quarterlyTotalRevenue column")
                    latest_quarter_idx = income_statement.index[-1]
                    print(f"📊 Latest quarter index: {latest_quarter_idx}")
                    rev_value = income_statement.loc[latest_quarter_idx, 'quarterlyTotalRevenue']
                    print(f"📊 Raw revenue value: {rev_value} (type: {type(rev_value)})")
                    
                    if pd.notna(rev_value) and rev_value != 0:
                        print("✅ Revenue value is valid (not NaN and not zero)")
                        rev_value = float(rev_value)
                        revenue = f"${rev_value/1_000_000:.1f}M" if rev_value >= 1_000_000 else f"${rev_value/1_000:.1f}K"
                        print(f"📊 Formatted revenue: {revenue}")
                    else:
                        print(f"❌ Revenue value is invalid: NaN={pd.isna(rev_value)}, Zero={rev_value == 0}")
            else:
                print("❌ Income statement is None or empty")
            
            # Extract Net Income
            if income_statement is not None and not income_statement.empty:
                net_income_col = None
                for col in ['quarterlyNetIncome', 'quarterlyNetIncomeCommonStockholders']:
                    if col in income_statement.columns:
                        net_income_col = col
                        break
                
                if net_income_col:
                    latest_quarter_idx = income_statement.index[-1]
                    ni_value = income_statement.loc[latest_quarter_idx, net_income_col]
                    if pd.notna(ni_value) and ni_value != 0:
                        ni_value = float(ni_value)
                        net_income = f"${ni_value/1_000_000:.1f}M" if abs(ni_value) >= 1_000_000 else f"${ni_value/1_000:.1f}K"
            
            # Extract Operating Cash Flow
            if cash_flow is not None and not cash_flow.empty:
                cf_col = None
                for col in ['quarterlyOperatingCashFlow', 'quarterlyFreeCashFlow']:
                    if col in cash_flow.columns:
                        cf_col = col
                        break
                
                if cf_col:
                    latest_quarter_idx = cash_flow.index[-1]
                    cf_value = cash_flow.loc[latest_quarter_idx, cf_col]
                    if pd.notna(cf_value) and cf_value != 0:
                        cf_value = float(cf_value)
                        cash_flow_value = f"${cf_value/1_000_000:.1f}M" if abs(cf_value) >= 1_000_000 else f"${cf_value/1_000:.1f}K"
            
            print(f"✅ Retrieved Yahoo API data for {symbol}")            
        except Exception as e:
            print(f"⚠️ Could not fetch Yahoo API fundamental data for {symbol}: {e}")
            import traceback
            traceback.print_exc()
        
        # FIXED: Better volume formatting with proper type checking
        volume_str = "N/A"
        if volume is not None and pd.notna(volume):
            try:
                volume_num = float(volume)
                if volume_num > 0:
                    if volume_num >= 1_000_000_000:
                        volume_str = f"{volume_num/1_000_000_000:.1f}B"
                    elif volume_num >= 1_000_000:
                        volume_str = f"{volume_num/1_000_000:.1f}M"
                    elif volume_num >= 1_000:
                        volume_str = f"{volume_num/1_000:.1f}K"
                    else:
                        volume_str = f"{int(volume_num):,}"
                    print(f"📊 Formatted volume: {volume_str}")
                else:
                    print("⚠️ Volume is zero or negative")
            except (ValueError, TypeError) as e:
                print(f"⚠️ Could not format volume: {e}")
        else:
            print("⚠️ Volume is None or NaN")
        
        # Add new row to the table
        with dpg.table_row(parent=current_table_tag):
            dpg.add_text(symbol)
            dpg.add_text(company_name[:20] + "..." if len(company_name) > 20 else company_name)
            dpg.add_text(f"${current_price:.2f}")
            
            # Color-coded change
            change_color = [0, 255, 0] if change >= 0 else [255, 0, 0]
            change_text = f"+${change:.2f}" if change >= 0 else f"${change:.2f}"
            dpg.add_text(change_text, color=change_color)
            
            dpg.add_text(volume_str)
            dpg.add_text(revenue)
            
            # Color-code net income
            ni_color = [255, 255, 255]  # Default white
            if net_income != "N/A" and not net_income.startswith("-"):
                ni_color = [0, 255, 0]  # Green for positive
            elif net_income != "N/A":
                ni_color = [255, 0, 0]  # Red for negative
            
            dpg.add_text(net_income, color=ni_color)
            dpg.add_text(cash_flow_value)
        
        print(f"✅ Added {symbol} ({company_name}) with Yahoo API financial data")
        
    except Exception as e:
        print(f"❌ Failed to add {symbol} to table: {e}")
        import traceback
        traceback.print_exc()