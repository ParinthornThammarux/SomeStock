# components/graph/graph_rsi.py

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
import time
import threading
import talib

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data, find_tag_by_symbol

def create_rsi_chart_for_stock(parent_tag, symbol, container_height=540):
    """
    Create a RSI chart for a specific stock within a container
    """
    try:
        print(f"📊 Creating RSI chart for {symbol}")
        
        # Generate unique tags for this stock's RSI chart
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"rsi_chart_container_{symbol}_{timestamp}"
        plot_tag = f"rsi_plot_{symbol}_{timestamp}"
        x_axis_tag = f"rsi_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"rsi_y_axis_{symbol}_{timestamp}"
        line_tag = f"rsi_line_{symbol}_{timestamp}"
        
        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(f"RSI Analysis: {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"rsi_status_{symbol}_{timestamp}", color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Create the RSI plot (separate from price plot)
            with dpg.plot(
                label="", 
                height=-1, 
                width=-1, 
                tag=plot_tag,
                equal_aspects=False,
                crosshairs=True,
                no_mouse_pos=True
            ):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Time Period", tag=x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label="RSI Value", tag=y_axis_tag, tick_format="%.2f")

                dpg.add_line_series([], [], parent=y_axis_tag, tag=line_tag, label=f"RSI {symbol}")
                dpg.set_axis_limits(x_axis_tag, 0, 100)
                dpg.set_axis_limits(y_axis_tag, 0, 100)
        
        # Start RSI calculation using global fetch system
        thread = threading.Thread(
            target=_fetch_and_plot_rsi_async, 
            args=(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, f"rsi_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating RSI chart for {symbol}: {e}")
        return None
    
def _fetch_and_plot_rsi_async(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Use the stock fetch layer to get stock data and calculate RSI"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Try to get cached data first
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} RSI calculation")
            _process_rsi_data(stock_data.price_history, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if constants.DEBUG:
                print(f"🔄 Fetching fresh data for {symbol} RSI calculation using global fetch system")

            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            fetch_stock_data(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag,period="1y", interval="1d")
            
            # Wait for data to be fetched and cached, then process for RSI
            _wait_for_cache_and_process_rsi(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        
    except Exception as e:
        print(f"❌ Error in RSI data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _wait_for_cache_and_process_rsi(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process RSI"""
    try:
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check if cache has been updated with fresh data
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
            
            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                if constants.DEBUG:
                    print(f"✅ Cache updated for {symbol}, processing RSI")
                _process_rsi_data(stock_data.price_history, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout
        if constants.DEBUG:
            print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_rsi_data(stock_data.price_history, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
def _process_rsi_data(price_df, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    
    """Process the cached price data to calculate and display RSI using TA-Lib"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Validating data for RSI...")
       
        # Validate data
        if not _validate_rsi_data(price_df, symbol):
           if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "Data validation failed")
               dpg.configure_item(status_tag, color=[255, 100, 100])
           return
       
        if dpg.does_item_exist(status_tag):
           dpg.set_value(status_tag, "Calculating RSI with TA-Lib...")
       
        # Get close prices from DF
        if 'close' not in price_df.columns:
            if constants.DEBUG:
                print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "Invalid price data")
               dpg.configure_item(status_tag, color=[255, 100, 100])
            return
       
        close_prices = price_df['close'].dropna()
       
        if len(close_prices) < 15:
            if constants.DEBUG:
                print(f"❌ Insufficient price data for {symbol}: {len(close_prices)} points")
            if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "Insufficient data")
               dpg.configure_item(status_tag, color=[255, 100, 100])
            return
              
        # Calculate RSI using TA-Lib
        rsi_data = _calculate_rsi_talib(close_prices, period=14)
       
        if rsi_data is None or len(rsi_data) == 0:
           if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "RSI calculation failed")
               dpg.configure_item(status_tag, color=[255, 100, 100])
           return

        try:
           # Get dates from DataFrame index
           full_dates = price_df.index if hasattr(price_df.index, '__iter__') else range(len(price_df))
           
           # Align dates with RSI data (RSI has fewer points due to initial NaN values)
           if len(full_dates) > len(rsi_data):
               # Skip the first dates that correspond to NaN RSI values  
               rsi_dates = full_dates[-len(rsi_data):]
           else:
               rsi_dates = full_dates
           
           # Convert dates to timestamps for DPG plotting
           x_data = []
           for date in rsi_dates:
               try:
                   if hasattr(date, 'timestamp'):
                       # Pandas Timestamp
                       x_data.append(date.timestamp())
                   elif hasattr(date, 'strftime'):
                       # datetime object
                       x_data.append(date.timestamp())
                   else:
                       # Fallback to sequential
                       x_data.append(len(x_data))
               except:
                   x_data.append(len(x_data))
           
           # If conversion failed, use sequential
           if not x_data:
                x_data = list(range(len(rsi_data)))
                if constants.DEBUG:
                    print(f"⚠️ Using sequential x-axis for {symbol} (date conversion failed)")
           else:
                if constants.DEBUG:
                    print(f"✅ Using timestamp x-axis for {symbol}")
               
        except Exception as e:
            if constants.DEBUG:
                print(f"⚠️ Date processing failed for {symbol}: {e}, using sequential")
            x_data = list(range(len(rsi_data)))
       
        y_data = rsi_data.tolist()
        print(f"🔍 RSI data types - numpy: {type(rsi_data[0])}, list: {type(y_data[0])}, values: {y_data[-5:]}")

        latest_rsi = rsi_data[-1] if len(rsi_data) > 0 else 0

        if dpg.does_item_exist(line_tag):
           dpg.set_value(line_tag, [x_data, y_data])
           print(f"📊 Updated RSI plot for {symbol} with {len(x_data)} points")
       
        # Update axis limits
        if dpg.does_item_exist(x_axis_tag):
           if len(x_data) > 0:
               # Check if we're using timestamps
               if isinstance(x_data[0], (int, float)) and x_data[0] > 1000000000:  # Timestamp check
                    dpg.set_axis_limits(x_axis_tag, min(x_data), max(x_data))
                    # Configure x-axis to show dates
                    dpg.configure_item(x_axis_tag, time=True)
                    if constants.DEBUG:
                        print(f"📅 Set timestamp x-axis limits for {symbol}")
               else:
                    dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
                    if constants.DEBUG:
                        print(f"🔢 Set sequential x-axis limits for {symbol}")
       
        if dpg.does_item_exist(y_axis_tag):
            dpg.set_axis_limits(y_axis_tag, 0, 100)
       
       # Add reference lines
        _add_rsi_reference_lines(y_axis_tag, x_data)
       
        # Update status with current RSI value and interpretation
        rsi_status, rsi_color = _get_rsi_interpretation(latest_rsi)
        dpg.set_value(status_tag, f"RSI: {latest_rsi:.1f} ({rsi_status}) [TA-Lib]")
        dpg.configure_item(status_tag, color=rsi_color)
       
        print(f"✅ RSI chart updated for {symbol} using TA-Lib - Latest RSI: {latest_rsi:.2f} ({rsi_status})")
        print(f"📊 Data summary: {len(close_prices)} price points → {len(rsi_data)} RSI values")
       
    except Exception as e:
        print(f"❌ Error processing RSI data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        if dpg.does_item_exist(status_tag):
           dpg.set_value(status_tag, f"Processing error: {str(e)[:20]}")
           dpg.configure_item(status_tag, color=[255, 100, 100])

def _validate_rsi_data(price_df, symbol):
    """Validate that we have appropriate data for RSI calculation"""
    if 'close' not in price_df.columns:
        print(f"❌ No 'close' column for {symbol}")
        return False
   
    close_prices = price_df['close'].dropna()
    data_points = len(close_prices)
   
    # Check data frequency and set appropriate minimums
    if len(price_df) > 200:
            if constants.DEBUG:
                print(f"📊 Using high-frequency data ({data_points} points) for {symbol}")
        # For intraday data, we need more points for stable RSI
    if data_points < 50:
           if constants.DEBUG:
                print(f"⚠️ Insufficient intraday data for reliable RSI: {data_points} points (need 50+)")
           return False
    else:
        if constants.DEBUG:
                print(f"📊 Using daily data ({data_points} points) for {symbol}")
        # For daily data, standard requirement
        if data_points < 15:
           if constants.DEBUG:
                print(f"❌ Insufficient daily data for RSI: {data_points} points (need 15+)")
           return False
   
    # Check for valid price data
    if close_prices.max() <= 0 or close_prices.min() < 0:
       if constants.DEBUG:
                print(f"❌ Invalid price data for {symbol}: prices not positive")
       return False
   
    return True
        
def _calculate_rsi_talib(prices, period=14):
    """
    Calculate RSI using TA-Lib library
    
    Args:
        prices: Pandas Series or numpy array of closing prices
        period: RSI period (default 14)
    
    Returns:
        Numpy array of RSI values
    """
    try:
        if isinstance(prices, pd.Series):
            prices_array = prices.values
        else:
            prices_array = np.array(prices)
        
        if len(prices_array) < period + 1:
            if constants.DEBUG:
                print(f"⚠️ Insufficient data for RSI calculation (need {period + 1}, got {len(prices_array)})")
            return None
        
        # Calculate RSI using TA-Lib
        rsi_values = talib.RSI(prices_array, timeperiod=period)
        
        # Remove NaN values (first 'period' values will be NaN)
        valid_rsi = rsi_values[~np.isnan(rsi_values)]
        
        if len(valid_rsi) == 0:
            if constants.DEBUG:
                print(f"❌ No valid RSI values calculated for {len(prices_array)} price points")
            return None
        
        if constants.DEBUG:
                print(f"✅ RSI calculated using TA-Lib: {len(valid_rsi)} values, range: {valid_rsi.min():.1f}-{valid_rsi.max():.1f}")
        return valid_rsi
        
    except ImportError:
        print("❌ TA-Lib not available- check installation")
        return None
    except Exception as e:
        print(f"❌ Error calculating RSI with TA-Lib: {e}")
        return None

def _add_rsi_reference_lines(y_axis_tag, x_data):
    """Add overbought/oversold reference lines to RSI chart"""
    try:
        if not dpg.does_item_exist(y_axis_tag):
            return
        
        if not x_data or len(x_data) == 0:
            if constants.DEBUG:
                print(f"⚠️ No x_data provided for reference lines")
            return
        
        timestamp = str(int(time.time() * 1000))
        
        data_length = len(x_data)
        
        overbought_tag = f"rsi_overbought_{timestamp}"
        y_overbought = [70] * data_length
        
        dpg.add_line_series(
            x_data, y_overbought,
            parent=y_axis_tag,
            tag=overbought_tag,
            label="Overbought (70)"
        )
        
        oversold_tag = f"rsi_oversold_{timestamp}"
        y_oversold = [30] * data_length
        
        dpg.add_line_series(
            x_data, y_oversold,
            parent=y_axis_tag,
            tag=oversold_tag,
            label="Oversold (30)"
        )

        midline_tag = f"rsi_midline_{timestamp}"
        y_midline = [50] * data_length
        
        dpg.add_line_series(
            x_data, y_midline,
            parent=y_axis_tag,
            tag=midline_tag,
            label="Midline (50)"
        )
                
    except Exception as e:
        if constants.DEBUG:
                print(f"Could not add RSI reference lines: {e}")
        
def _get_rsi_interpretation(rsi_value):
    """Get RSI interpretation and corresponding color"""
    if rsi_value > 70:
        return "Overbought", [255, 100, 100]  # Red
    elif rsi_value < 30:
        return "Oversold", [100, 255, 100]    # Green
    else:
        return "Neutral", [255, 200, 100]     # Orange
    
# Utility functions for external access
def get_rsi_for_symbol(symbol, period=14):
    """
    Get current RSI value for a symbol using TA-Lib
    
    Returns:
        tuple: (rsi_value, interpretation, color)
    """
    try:
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            rsi_values = _calculate_rsi_talib(stock_data.price_history['close'], period)
            if rsi_values is not None and len(rsi_values) > 0:
                latest_rsi = rsi_values[-1]
                interpretation, color = _get_rsi_interpretation(latest_rsi)
                return latest_rsi, interpretation, color
        
        return None, "No Data", [100, 100, 100]
        
    except Exception as e:
        print(f"❌ Error getting RSI for {symbol}: {e}")
        return None, "Error", [255, 100, 100]