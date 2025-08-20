# components/graph/graph_rsi.py

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
import time
import threading
import talib

from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data, find_tag_by_symbol

def create_rsi_chart_for_stock(parent_tag, symbol, container_height=280):
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
        
        # Create chart container
        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            # Chart header with stock info
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
                tag=plot_tag
            ):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Time Period", tag=x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label="RSI Value", tag=y_axis_tag)
                
                # Initialize empty RSI line series
                dpg.add_line_series([], [], parent=y_axis_tag, tag=line_tag, label=f"RSI {symbol}")
                
                # Set RSI-appropriate axis limits
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
        # Update status
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Try to get cached data first
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} RSI calculation")
            _process_rsi_data(stock_data.price_history, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            print(f"🔄 Fetching fresh data for {symbol} RSI calculation using global fetch system")
            
            # Update status
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            fetch_stock_data(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag)
            
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
                
                print(f"✅ Cache updated for {symbol}, processing RSI")
                _process_rsi_data(stock_data.price_history, symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout - try with whatever data we have
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
            dpg.set_value(status_tag, "Calculating RSI with TA-Lib...")
        
        # Get close prices from the DataFrame
        if 'close' not in price_df.columns:
            print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Invalid price data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        close_prices = price_df['close'].dropna()
        
        if len(close_prices) < 15:  # Need at least 15 points for 14-period RSI
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
        
        # Prepare plot data
        x_data = list(range(len(rsi_data)))
        y_data = rsi_data.tolist()
        
        # Get latest RSI value for display
        latest_rsi = rsi_data[-1] if len(rsi_data) > 0 else 0
        
        # Update the RSI plot
        if dpg.does_item_exist(line_tag):
            dpg.set_value(line_tag, [x_data, y_data])
        
        # Update axis limits for RSI (0-100 range)
        if dpg.does_item_exist(x_axis_tag):
            dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
        if dpg.does_item_exist(y_axis_tag):
            dpg.set_axis_limits(y_axis_tag, 0, 100)
        
        # Add reference lines for overbought/oversold levels
        _add_rsi_reference_lines(y_axis_tag, len(x_data))
        
        # Update status with current RSI value and interpretation
        rsi_status, rsi_color = _get_rsi_interpretation(latest_rsi)
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"RSI: {latest_rsi:.1f} ({rsi_status}) [TA-Lib]")
            dpg.configure_item(status_tag, color=rsi_color)
        
        print(f"✅ RSI chart updated for {symbol} using TA-Lib - Latest RSI: {latest_rsi:.2f} ({rsi_status})")
        
    except Exception as e:
        print(f"❌ Error processing RSI data for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Processing error")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
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
        # Convert to numpy array if it's a pandas Series
        if isinstance(prices, pd.Series):
            prices_array = prices.values
        else:
            prices_array = np.array(prices)
        
        if len(prices_array) < period + 1:
            print(f"⚠️ Insufficient data for RSI calculation (need {period + 1}, got {len(prices_array)})")
            return None
        
        # Calculate RSI using TA-Lib
        rsi_values = talib.RSI(prices_array, timeperiod=period)
        
        # Remove NaN values (first 'period' values will be NaN)
        valid_rsi = rsi_values[~np.isnan(rsi_values)]
        
        if len(valid_rsi) == 0:
            print(f"❌ No valid RSI values calculated for {len(prices_array)} price points")
            return None
        
        print(f"✅ RSI calculated using TA-Lib: {len(valid_rsi)} values, range: {valid_rsi.min():.1f}-{valid_rsi.max():.1f}")
        return valid_rsi
        
    except ImportError:
        print("❌ TA-Lib not available, falling back to manual calculation")
        return _calculate_rsi_manual_fallback(prices, period)
    except Exception as e:
        print(f"❌ Error calculating RSI with TA-Lib: {e}")
        return _calculate_rsi_manual_fallback(prices, period)

def _calculate_rsi_manual_fallback(prices, period=14):
    """
    Fallback manual RSI calculation when TA-Lib is not available
    """
    try:
        print("🔄 Using manual RSI calculation as fallback")
        
        if isinstance(prices, pd.Series):
            prices = prices.values
        else:
            prices = np.array(prices)
        
        if len(prices) < period + 1:
            print(f"⚠️ Insufficient data for RSI calculation (need {period + 1}, got {len(prices)})")
            return None
        
        # Calculate price differences
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate initial averages
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        # Initialize RSI array
        rsi = np.zeros(len(prices))
        rsi[:period] = np.nan  # First 'period' values are NaN
        
        # Calculate RSI for each point after the initial period
        for i in range(period, len(prices)):
            # Smoothed moving average (Wilder's smoothing)
            avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
            
            # Calculate RS and RSI
            if avg_loss == 0:
                rsi[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))
        
        # Return only valid RSI values (remove NaN)
        valid_rsi = rsi[period:]
        
        print(f"✅ Manual RSI calculated: {len(valid_rsi)} values, range: {valid_rsi.min():.1f}-{valid_rsi.max():.1f}")
        return valid_rsi
        
    except Exception as e:
        print(f"❌ Error in manual RSI calculation: {e}")
        return None
    
def _add_rsi_reference_lines(y_axis_tag, data_length):
    """Add overbought/oversold reference lines to RSI chart"""
    try:
        if not dpg.does_item_exist(y_axis_tag):
            return
        
        # Create timestamp for unique tags
        timestamp = str(int(time.time() * 1000))
        
        # Overbought line at 70
        overbought_tag = f"rsi_overbought_{timestamp}"
        x_values = list(range(data_length))
        y_values = [70] * data_length
        
        dpg.add_line_series(
            x_values, y_values,
            parent=y_axis_tag,
            tag=overbought_tag,
            label="Overbought (70)"
        )
        
        # Oversold line at 30
        oversold_tag = f"rsi_oversold_{timestamp}"
        y_values = [30] * data_length
        
        dpg.add_line_series(
            x_values, y_values,
            parent=y_axis_tag,
            tag=oversold_tag,
            label="Oversold (30)"
        )
        
        # Midline at 50
        midline_tag = f"rsi_midline_{timestamp}"
        y_values = [50] * data_length
        
        dpg.add_line_series(
            x_values, y_values,
            parent=y_axis_tag,
            tag=midline_tag,
            label="Midline (50)"
        )
        
    except Exception as e:
        print(f"⚠️ Could not add RSI reference lines: {e}")

def _get_rsi_interpretation(rsi_value):
    """Get RSI interpretation and corresponding color"""
    if rsi_value > 70:
        return "Overbought", [255, 100, 100]  # Red
    elif rsi_value < 30:
        return "Oversold", [100, 255, 100]    # Green
    elif rsi_value > 50:
        return "Bullish", [255, 255, 100]     # Yellow
    else:
        return "Bearish", [255, 200, 100]     # Orange

def create_rsi_analysis_summary(parent_tag, symbols):
    """
    Create a summary table of RSI values for multiple stocks
    
    Args:
        parent_tag: Parent container for the summary
        symbols: List of stock symbols to analyze
    """
    try:
        timestamp = str(int(time.time() * 1000))
        summary_tag = f"rsi_summary_{timestamp}"
        
        with dpg.child_window(
            width=-1, 
            height=200, 
            border=True, 
            parent=parent_tag,
            tag=summary_tag
        ):
            dpg.add_text("RSI Summary", color=[255, 255, 255])
            dpg.add_separator()
            
            # Create summary table
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, 
                          borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="RSI", width_fixed=True, init_width_or_weight=60)
                dpg.add_table_column(label="Signal", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Status", width_fixed=True, init_width_or_weight=120)
                
                for symbol in symbols:
                    with dpg.table_row():
                        dpg.add_text(symbol)
                        dpg.add_text("Calculating...", tag=f"rsi_value_{symbol}_{timestamp}")
                        dpg.add_text("...", tag=f"rsi_signal_{symbol}_{timestamp}")
                        dpg.add_text("Loading", tag=f"rsi_status_summary_{symbol}_{timestamp}")
        
        return summary_tag
        
    except Exception as e:
        print(f"❌ Error creating RSI summary: {e}")
        return None

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