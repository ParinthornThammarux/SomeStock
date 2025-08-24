# components/indicator/Indicator_EMA.py

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
import time
import threading
import talib

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data

plot_tag_to_text_tag = {}

def create_ema_chart_for_stock(parent_tag, symbol, container_height=540):
    """
    Create a EMA crossover chart for a specific stock within a container
    """
    
    try:
        print(f"📊 Creating EMA chart for {symbol}")
        
        # Generate unique tags for this stock's EMA chart
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"ema_chart_container_{symbol}_{timestamp}"
        plot_tag = f"ema_plot_{symbol}_{timestamp}"
        x_axis_tag = f"ema_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"ema_y_axis_{symbol}_{timestamp}"
        price_line_tag = f"ema_price_line_{symbol}_{timestamp}"
        ema12_line_tag = f"ema12_line_{symbol}_{timestamp}"
        ema26_line_tag = f"ema26_line_{symbol}_{timestamp}"
        mouse_text_tag = f"{symbol}_mouse_ema_{timestamp}"
        
        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(f"EMA Crossover: {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"ema_status_{symbol}_{timestamp}", color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text("Mouse Position:", tag=mouse_text_tag)
            
            dpg.set_frame_callback(0, callback=check_hover)

            # Create the EMA plot with price and EMAs
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
                dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)

                # Add line series
                dpg.add_line_series([], [], parent=y_axis_tag, tag=price_line_tag, label=f"Price {symbol}")
                dpg.add_line_series([], [], parent=y_axis_tag, tag=ema12_line_tag, label="EMA 12")
                dpg.add_line_series([], [], parent=y_axis_tag, tag=ema26_line_tag, label="EMA 26")

                dpg.set_axis_limits(x_axis_tag, 0, 100)
                dpg.set_axis_limits(y_axis_tag, 0, 200)
                
        with dpg.handler_registry():
            dpg.add_mouse_move_handler(
                callback=update_mouse_pos_text, 
                user_data={"plot_tag": plot_tag, "text_tag": mouse_text_tag}
            )
        plot_tag_to_text_tag[plot_tag] = mouse_text_tag
        
        # Start EMA calculation using global fetch system
        thread = threading.Thread(
            target=_fetch_and_plot_ema, 
            args=(symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, f"ema_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating EMA chart for {symbol}: {e}")
        return None


def check_hover():
    """Check hover state for ALL existing EMA plots"""
    global plot_tag_to_text_tag
    
    plot_tags_copy = list(plot_tag_to_text_tag.keys())
    
    for plot_tag in plot_tags_copy:
        text_tag = plot_tag_to_text_tag[plot_tag]
        
        try:
            if not dpg.does_item_exist(plot_tag) or not dpg.does_item_exist(text_tag):
                del plot_tag_to_text_tag[plot_tag]
                continue
                
            if not dpg.is_item_hovered(plot_tag):
                dpg.set_value(text_tag, "Mouse Position:")
                
        except Exception as e:
            if plot_tag in plot_tag_to_text_tag:
                del plot_tag_to_text_tag[plot_tag]
            if constants.DEBUG:
                print(f"⚠️ Cleaned up dead plot reference: {plot_tag}")

def update_mouse_pos_text(sender, app_data, user_data):
    """Updates the mouse position text for the specific plot"""
    plot_tag = user_data["plot_tag"]
    text_tag = user_data["text_tag"]
    
    try:
        if not dpg.does_item_exist(plot_tag) or not dpg.does_item_exist(text_tag):
            return
            
        if dpg.is_item_hovered(plot_tag):
            mouse_pos = dpg.get_plot_mouse_pos()
            if mouse_pos and len(mouse_pos) >= 2:
                mouse_x, mouse_y = mouse_pos[0], mouse_pos[1]
                
                try:
                    if mouse_x > 1000000000:
                        import datetime
                        date_obj = datetime.datetime.fromtimestamp(mouse_x)
                        date_str = date_obj.strftime("%Y-%m-%d")
                        dpg.set_value(text_tag, f"Mouse Position: ({date_str}, ${mouse_y:.2f})")
                    else:
                        dpg.set_value(text_tag, f"Mouse Position: (Day {int(mouse_x)}, ${mouse_y:.2f})")
                except (ValueError, OSError, OverflowError):
                    dpg.set_value(text_tag, f"Mouse Position: ({mouse_x:.0f}, ${mouse_y:.2f})")
            else:
                dpg.set_value(text_tag, "Mouse Position: No position")
        else:
            dpg.set_value(text_tag, "Mouse Position:")
            
    except Exception as e:
        if constants.DEBUG:
            print(f"⚠️ Mouse handler error: {e}")
              
def _fetch_and_plot_ema(symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Use the stock fetch layer to get stock data and calculate EMA crossover"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Try to get cached data first
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} EMA calculation")
            _process_ema_data(stock_data.price_history, symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if constants.DEBUG:
                print(f"🔄 Fetching fresh data for {symbol} EMA calculation using global fetch system")

            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            fetch_stock_data(symbol, None, None, None, None, period="1y", interval="1d")
            
            # Wait for data to be fetched and cached, then process for EMA
            _wait_for_cache_and_process_ema(symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        
    except Exception as e:
        print(f"❌ Error in EMA data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _wait_for_cache_and_process_ema(symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process EMA"""
    try:
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
            
            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                if constants.DEBUG:
                    print(f"✅ Cache updated for {symbol}, processing EMA")
                _process_ema_data(stock_data.price_history, symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return
            
            time.sleep(0.5)
        
        # Timeout
        if constants.DEBUG:
            print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_ema_data(stock_data.price_history, symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
def _process_ema_data(price_df, symbol, price_line_tag, ema12_line_tag, ema26_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Process the cached price data to calculate and display EMA crossover using TA-Lib"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Calculating EMA crossover...")
       
        # Validate data
        if 'close' not in price_df.columns:
            if constants.DEBUG:
                print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "Invalid price data")
               dpg.configure_item(status_tag, color=[255, 100, 100])
            return
       
        close_prices = price_df['close'].dropna()
       
        if len(close_prices) < 30:  # Need more data for EMA crossover
            if constants.DEBUG:
                print(f"❌ Insufficient price data for {symbol}: {len(close_prices)} points")
            if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "Insufficient data")
               dpg.configure_item(status_tag, color=[255, 100, 100])
            return
              
        # Calculate EMAs using TA-Lib
        ema12_data = talib.EMA(close_prices.values, timeperiod=12)
        ema26_data = talib.EMA(close_prices.values, timeperiod=26)
        
        # Remove NaN values
        valid_indices = ~(np.isnan(ema12_data) | np.isnan(ema26_data))
        ema12_clean = ema12_data[valid_indices]
        ema26_clean = ema26_data[valid_indices]
        price_clean = close_prices.values[valid_indices]
        
        if len(ema12_clean) == 0:
           if dpg.does_item_exist(status_tag):
               dpg.set_value(status_tag, "EMA calculation failed")
               dpg.configure_item(status_tag, color=[255, 100, 100])
           return

        try:
           # Get dates from DataFrame index
           full_dates = price_df.index if hasattr(price_df.index, '__iter__') else range(len(price_df))
           
           # Align dates with EMA data
           if len(full_dates) > len(ema12_clean):
               ema_dates = full_dates[-len(ema12_clean):]
           else:
               ema_dates = full_dates
           
           # Convert dates to timestamps for DPG plotting
           x_data = []
           for date in ema_dates:
               try:
                   if hasattr(date, 'timestamp'):
                       x_data.append(date.timestamp())
                   elif hasattr(date, 'strftime'):
                       x_data.append(date.timestamp())
                   else:
                       x_data.append(len(x_data))
               except:
                   x_data.append(len(x_data))
           
           # If conversion failed, use sequential
           if not x_data:
                x_data = list(range(len(ema12_clean)))
                if constants.DEBUG:
                    print(f"⚠️ Using sequential x-axis for {symbol}")
           else:
                if constants.DEBUG:
                    print(f"✅ Using timestamp x-axis for {symbol}")
               
        except Exception as e:
            if constants.DEBUG:
                print(f"⚠️ Date processing failed for {symbol}: {e}, using sequential")
            x_data = list(range(len(ema12_clean)))

        # Convert data to lists for DPG
        price_data = price_clean.tolist()
        ema12_data_list = ema12_clean.tolist()
        ema26_data_list = ema26_clean.tolist()

        # Update plot lines
        if dpg.does_item_exist(price_line_tag):
           dpg.set_value(price_line_tag, [x_data, price_data])
        if dpg.does_item_exist(ema12_line_tag):
           dpg.set_value(ema12_line_tag, [x_data, ema12_data_list])
        if dpg.does_item_exist(ema26_line_tag):
           dpg.set_value(ema26_line_tag, [x_data, ema26_data_list])
        
        _add_crossover_markers(plot_tag, y_axis_tag, x_data, price_data, ema12_clean, ema26_clean, str(int(time.time() * 1000)))

           
        print(f"📊 Updated EMA plot for {symbol} with {len(x_data)} points")
       
        # Update axis limits
        if dpg.does_item_exist(x_axis_tag):
           if len(x_data) > 0:
               if isinstance(x_data[0], (int, float)) and x_data[0] > 1000000000:
                    dpg.set_axis_limits(x_axis_tag, min(x_data), max(x_data))
                    dpg.configure_item(x_axis_tag, time=True)
                    if constants.DEBUG:
                        print(f"📅 Set timestamp x-axis limits for {symbol}")
               else:
                    dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
                    if constants.DEBUG:
                        print(f"🔢 Set sequential x-axis limits for {symbol}")
       
        if dpg.does_item_exist(y_axis_tag):
            all_values = price_data + ema12_data_list + ema26_data_list
            min_val = min(all_values) * 0.98
            max_val = max(all_values) * 1.02
            dpg.set_axis_limits(y_axis_tag, min_val, max_val)

        # Detect crossovers
        crossovers = _detect_ema_crossovers(ema12_clean, ema26_clean)
        if crossovers:
            print(f"📈 {symbol} - EMA Cross detected:")
            for crossover in crossovers[-5:]:  # Show last 5 crossovers
                cross_type = "Bullish" if crossover['type'] == 'bullish' else "Bearish"
                print(f"  - Point {crossover['index']}: {cross_type}")
        else:
            print(f"📉 {symbol} - No EMA Cross detected in data.")
            
        # Update status with crossover information
        latest_ema12 = ema12_clean[-1]
        latest_ema26 = ema26_clean[-1]
        latest_price = price_clean[-1]
        
        if latest_ema12 > latest_ema26:
            signal = "Bullish"
            signal_color = [100, 255, 100]
        else:
            signal = "Bearish" 
            signal_color = [255, 100, 100]
            
        recent_crossovers = len([c for c in crossovers if c['index'] >= len(ema12_clean) - 50])  # Last 50 points
        dpg.set_value(status_tag, f"EMA 12: ${latest_ema12:.2f} | EMA 26: ${latest_ema26:.2f} | Signal: {signal} | Recent Crosses: {recent_crossovers}")
        dpg.configure_item(status_tag, color=signal_color)
       
        print(f"✅ EMA chart updated for {symbol} - Latest EMA12: ${latest_ema12:.2f}, EMA26: ${latest_ema26:.2f} ({signal})")
        print(f"📊 Detected {len(crossovers)} crossovers in the data period")
       
    except Exception as e:
        print(f"❌ Error processing EMA data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        if dpg.does_item_exist(status_tag):
           dpg.set_value(status_tag, f"Processing error: {str(e)[:20]}")
           dpg.configure_item(status_tag, color=[255, 100, 100])

def _detect_ema_crossovers(ema12, ema26):
    """Detect EMA crossover points using signal diff method"""
    try:
        # Create signal array: 1 when EMA12 > EMA26, 0 otherwise
        signal = np.where(ema12 > ema26, 1, 0)
        
        # Calculate signal differences to detect crossovers
        cross = np.diff(signal)
        
        crossovers = []
        
        # Find crossover indices (note: diff() result is 1 element shorter)
        for i in range(len(cross)):
            if cross[i] == 1:  # Signal changed from 0 to 1 (Bullish)
                crossovers.append({'index': i + 1, 'type': 'bullish'})  # +1 because diff shifts index
            elif cross[i] == -1:  # Signal changed from 1 to 0 (Bearish)
                crossovers.append({'index': i + 1, 'type': 'bearish'})
        
        return crossovers
        
    except Exception as e:
        print(f"❌ Error detecting crossovers: {e}")
        return []
    
# Utility functions for external access
def get_ema_crossover_for_symbol(symbol, period_fast=12, period_slow=26):
    """
    Get current EMA crossover signal for a symbol using TA-Lib
    
    Returns:
        tuple: (ema12, ema26, signal, crossovers_count)
    """
    try:
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            close_prices = stock_data.price_history['close'].dropna()
            if len(close_prices) >= max(period_fast, period_slow) + 1:
                ema12 = talib.EMA(close_prices.values, timeperiod=period_fast)
                ema26 = talib.EMA(close_prices.values, timeperiod=period_slow)
                
                # Get latest values
                latest_ema12 = ema12[-1]
                latest_ema26 = ema26[-1]
                
                signal = "Bullish" if latest_ema12 > latest_ema26 else "Bearish"
                
                # Count recent crossovers
                crossovers = _detect_ema_crossovers(ema12[~np.isnan(ema12)], ema26[~np.isnan(ema26)])
                
                return latest_ema12, latest_ema26, signal, len(crossovers)
        
        return None, None, "No Data", 0
        
    except Exception as e:
        print(f"❌ Error getting EMA crossover for {symbol}: {e}")
        return None, None, "Error", 0

def cleanup_ema_plot_tracking(symbol):
    """Clean up EMA plot tracking when a stock is removed"""
    global plot_tag_to_text_tag
    
    try:
        keys_to_remove = []
        for plot_tag in plot_tag_to_text_tag.keys():
            if symbol in plot_tag:
                keys_to_remove.append(plot_tag)
        
        for key in keys_to_remove:
            del plot_tag_to_text_tag[key]
            print(f"🧹 Cleaned up EMA plot tracking for {symbol}")
            
    except Exception as e:
        print(f"⚠️ Error cleaning up EMA tracking: {e}")
        
def _add_crossover_markers(plot_tag, y_axis_tag, x_data, price_data, ema12_data, ema26_data, timestamp):
    """Add plot annotations for bullish and bearish crossovers"""
    try:
        if not dpg.does_item_exist(plot_tag):
            return
        
        crossovers = _detect_ema_crossovers(ema12_data, ema26_data)
        
        if not crossovers:
            return
        
        # Add crossover annotations
        for crossover in crossovers:
            idx = crossover['index']
            if idx < len(x_data) and idx < len(price_data):
                x_pos = x_data[idx]
                y_pos = price_data[idx]
                
                if crossover['type'] == 'bullish':
                    # Green upward triangle annotation
                    annotation_tag = f"bullish_annotation_{timestamp}_{idx}"
                    dpg.add_plot_annotation(
                        label="^",  # Unicode upward triangle
                        default_value=(x_pos, y_pos),
                        offset=(0, -20),  # Offset above the point
                        color=[0, 255, 0, 255],  # Green
                        parent=plot_tag,
                        tag=annotation_tag
                    )
                    
                elif crossover['type'] == 'bearish':
                    # Red downward triangle annotation
                    annotation_tag = f"bearish_annotation_{timestamp}_{idx}"
                    dpg.add_plot_annotation(
                        label="v",  # Unicode downward triangle
                        default_value=(x_pos, y_pos),
                        offset=(0, 20),  # Offset below the point
                        color=[255, 0, 0, 255],  # Red
                        parent=plot_tag,
                        tag=annotation_tag
                    )
        
        # bullish_count = len([c for c in crossovers if c['type'] == 'bullish'])
        # bearish_count = len([c for c in crossovers if c['type'] == 'bearish'])
        
    except Exception as e:
        if constants.DEBUG:
            print(f"⚠️ Could not add crossover annotations: {e}")