# components/graph/analysis_graph.py

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd
import threading
import numpy as np
import yfinance as yf
import talib
from concurrent.futures import ThreadPoolExecutor, as_completed


from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock_search import create_stock_search

# Global variables to track current chart components
current_stock_line_tag = None
current_x_axis_tag = None
current_y_axis_tag = None
current_plot_tag = None
current_table_tag = None

# Thread lock for table operations
table_lock = threading.Lock()

def calculate_rsi_talib(data, timeperiod=14):
    """Calculate RSI using TA-Lib"""
    rsi = talib.RSI(data['Close'], timeperiod=timeperiod)
    return rsi

def fetch_and_plot_rsi(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Fetch stock data and plot RSI"""
    try:
        print(f"📊 Fetching RSI data for {symbol}")
        
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3mo", interval="1d")  # 3 months daily data
        
        if data.empty:
            print(f"❌ No data found for {symbol}")
            return
        
        # Calculate RSI using TA-Lib
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        latest_rsi = data['RSI'].iloc[-1]

        # Remove NaN values (first 14 values will be NaN)
        rsi_clean = data['RSI'].dropna()

        # Prepare data for DPG plot
        x_data = list(range(len(rsi_clean)))
        y_data = rsi_clean.tolist()

        print(f"📈 Latest RSI for {symbol}: {latest_rsi:.2f}")
        
        # Update the plot
        dpg.set_value(line_tag, [x_data, y_data])
        
        # Set appropriate axis limits for RSI (0-100)
        dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
        dpg.set_axis_limits(y_axis_tag, 0, 100)
        
        # Clear existing horizontal lines
        children = dpg.get_item_children(y_axis_tag, 1)
        if children:
            for child in children:
                child_label = dpg.get_item_label(child) if dpg.does_item_exist(child) else ""
                if "hline" in str(child) or "Overbought" in child_label or "Oversold" in child_label:
                    try:
                        dpg.delete_item(child)
                    except:
                        pass
        
        # Add horizontal reference lines for RSI levels
        try:
            # Overbought line at 70
            overbought_tag = f"hline_70_{int(time.time())}"
            dpg.add_hline_series([70] * len(x_data), parent=y_axis_tag, 
                               tag=overbought_tag, label="Overbought (70)")
            
            # Oversold line at 30
            oversold_tag = f"hline_30_{int(time.time())}"
            dpg.add_hline_series([30] * len(x_data), parent=y_axis_tag, 
                               tag=oversold_tag, label="Oversold (30)")
        except Exception as e:
            print(f"⚠️ Could not add reference lines: {e}")
        
        # Update axis labels
        dpg.configure_item(x_axis_tag, label="Days")
        dpg.configure_item(y_axis_tag, label="RSI Value")
        
        print(f"✅ RSI plot updated for {symbol}")

        if latest_rsi > 70:
            print(f"🔴 {symbol} is OVERBOUGHT (RSI: {latest_rsi:.2f})")
        elif latest_rsi < 30:
            print(f"🟢 {symbol} is OVERSOLD (RSI: {latest_rsi:.2f})")
        else:
            print(f"🟡 {symbol} is in NEUTRAL territory (RSI: {latest_rsi:.2f})")
        
    except Exception as e:
        print(f"❌ Error plotting RSI for {symbol}: {e}")
        import traceback
        traceback.print_exc()

def rsi_analysis_callback():
    """Callback for RSI analysis button"""
    print("📊 RSI Analysis clicked!")
    
    # For proof of concept, use a default symbol - can be made user input later
    symbol = "AAPL"
    
    # Use global chart tags
    global current_plot_tag, current_x_axis_tag, current_y_axis_tag, current_stock_line_tag
    
    if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
        # Update chart title/label
        if dpg.does_item_exist(current_plot_tag):
            try:
                dpg.configure_item(current_plot_tag, label=f"RSI Analysis - {symbol}")
            except:
                pass
        
        fetch_and_plot_rsi(symbol, current_stock_line_tag, current_x_axis_tag, 
                          current_y_axis_tag, current_plot_tag)
    else:
        print("❌ Chart components not available")

def reset_chart_callback():
    """Reset chart to normal price view"""
    print("🔄 Resetting chart to price view")
    
    global current_plot_tag, current_x_axis_tag, current_y_axis_tag
    
    # Reset chart title
    if dpg.does_item_exist(current_plot_tag):
        try:
            dpg.configure_item(current_plot_tag, label="Stock Price Chart")
        except:
            pass
    
    # Reset axis labels
    if dpg.does_item_exist(current_x_axis_tag):
        dpg.configure_item(current_x_axis_tag, label="Days")
    if dpg.does_item_exist(current_y_axis_tag):
        dpg.configure_item(current_y_axis_tag, label="Price ($)")
    
    # Generate fresh random data for demo
    refresh_data()

def create_main_rsi_graph(parent_tag, timestamp=None):
    """
    Creates a content page with a graph on top and technical analysis below.
    RSI analysis
    """
    # GLOBAL DECLARATION MUST BE FIRST IN FUNCTION
    global current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag, current_table_tag
    
    print(f"Creating analysis graph in parent: {parent_tag}")
    
    # Create unique identifier for this instance
    if timestamp is None:
        timestamp = str(int(time.time() * 1000))
    
    # Create a main container with proper height management
    main_container_tag = f"main_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, tag=main_container_tag, no_scrollbar=False):

        # GRAPH SECTION - Fixed height container
        dpg.add_text("Stock Analysis Chart", color=[200, 200, 255])
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
            with dpg.child_window(width=-1, height=400, tag=graph_container_tag, border=True):
                with dpg.plot(label="Stock Price Chart", height=-1, width=-1, tag=plot_tag):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag=x_axis_tag)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                    dpg.add_line_series(x_data, y_data, parent=y_axis_tag, tag=line_tag, label="Stock Data")
                    dpg.set_axis_limits(x_axis_tag, 0, 50)
                    dpg.set_axis_limits(y_axis_tag, 80, 120)

        # Technical Analysis Section
        dpg.add_spacer(height=15)
        dpg.add_text("Technical Analysis Tools", color=[255, 200, 100])
        dpg.add_separator()
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            # RSI Analysis button
            dpg.add_button(label="📈 RSI Analysis (AAPL)", callback=rsi_analysis_callback, 
                          width=180, height=35)
            dpg.add_spacer(width=15)
            
            # Reset Chart button
            dpg.add_button(label="🔄 Reset to Price Chart", callback=reset_chart_callback, 
                          width=180, height=35)
            dpg.add_spacer(width=15)
            
            # Stock search button
            dpg.add_button(label="🔍 Add Stock", callback=plus_button_callback, 
                          width=120, height=35)

        dpg.add_spacer(height=15)

        # Analysis Info Section
        with dpg.child_window(width=-1, height=150, border=True):
            dpg.add_text("Analysis Information", color=[200, 255, 200])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            dpg.add_text("RSI (Relative Strength Index) Information:", color=[180, 180, 255])
            dpg.add_text("• RSI > 70: Potentially Overbought (Consider Selling)", color=[255, 150, 150])
            dpg.add_text("• RSI < 30: Potentially Oversold (Consider Buying)", color=[150, 255, 150])
            dpg.add_text("• RSI 30-70: Neutral Territory", color=[255, 255, 150])
            dpg.add_spacer(height=5)
            dpg.add_text("Click 'RSI Analysis' to view RSI chart for AAPL", color=[200, 200, 200])

        dpg.add_spacer(height=20)
        
        # Navigation buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="⬅️ Back to Welcome", callback=go_to_welcome, width=150, height=35)
            dpg.add_spacer(width=15)
            dpg.add_button(label="📊 Portfolio View", callback=go_to_portfolio, width=150, height=35)

def plus_button_callback():
    """Open stock search dialog"""
    print("Plus button clicked!")
    create_stock_search(
        current_stock_line_tag,
        current_x_axis_tag,
        current_y_axis_tag,
        current_plot_tag
    )

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

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

def go_to_portfolio():
    """Go to portfolio/enhanced page"""
    print("Going to portfolio page")
    from containers.container_content import show_page
    show_page("enhanced")

# Legacy compatibility functions
def fav_button_callback():
    """Heart button callback"""
    print("Heart button clicked!")
    from components.stock.stock_data_manager import get_favorited_stocks
    favorites = get_favorited_stocks()
    print(f"Favorited stocks: {favorites}")

def create_graph_table_page(parent_tag):
    """Legacy function - redirects to new system"""
    return create_main_graph(parent_tag)