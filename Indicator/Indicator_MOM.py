# components/indicator/indicator_MOM.py

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

def create_mom_chart_for_stock(parent_tag, symbol, container_height=540):
    """
    Create a Momentum chart for a specific stock within a container
    """
    
    try:
        print(f"📊 Creating MOM chart for {symbol}")
        
        # Generate unique tags for this stock's MOM chart
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"mom_chart_container_{symbol}_{timestamp}"
        plot_tag = f"mom_plot_{symbol}_{timestamp}"
        x_axis_tag = f"mom_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"mom_y_axis_{symbol}_{timestamp}"
        momentum_line_tag = f"mom_price_line_{symbol}_{timestamp}"
        mouse_text_tag = f"{symbol}_mouse_mom_{timestamp}"

        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(f"Momentum : {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"mom_status_{symbol}_{timestamp}", color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text("Mouse Position:", tag=mouse_text_tag)
            
            dpg.set_frame_callback(0, callback=check_hover)

            # Create the MOM plot
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
                dpg.add_plot_axis(dpg.mvYAxis, label="Momentum", tag=y_axis_tag)

                # Add line series
                dpg.add_line_series([], [], parent=y_axis_tag, tag=momentum_line_tag, label=f"Momentum {symbol}")

                dpg.set_axis_limits(x_axis_tag, 0, 100)
                dpg.set_axis_limits(y_axis_tag, 0, 200)
                
        with dpg.handler_registry():
            dpg.add_mouse_move_handler(
                callback=update_mouse_pos_text, 
                user_data={"plot_tag": plot_tag, "text_tag": mouse_text_tag}
            )
        plot_tag_to_text_tag[plot_tag] = mouse_text_tag
        
        # Start MOM calculation using global fetch system
        thread = threading.Thread(
            target=_fetch_and_plot_mom, 
            args=(symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, f"mom_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating MOM chart for {symbol}: {e}")
        return None


def check_hover():
    """Check hover state for ALL existing MOM plots"""
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
                        dpg.set_value(text_tag, f"Mouse Position: ({date_str}, {mouse_y:.2f})")
                    else:
                        dpg.set_value(text_tag, f"Mouse Position: (Day {int(mouse_x)}, {mouse_y:.2f})")
                except (ValueError, OSError, OverflowError):
                    dpg.set_value(text_tag, f"Mouse Position: ({mouse_x:.0f}, {mouse_y:.2f})")
            else:
                dpg.set_value(text_tag, "Mouse Position: No position")
        else:
            dpg.set_value(text_tag, "Mouse Position:")
            
    except Exception as e:
        if constants.DEBUG:
            print(f"⚠️ Mouse handler error: {e}")
              
def _fetch_and_plot_mom(symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Use the stock fetch layer to get stock data and calculate Momentum"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Try to get cached data first
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} Momentum calculation")
            _process_mom_data(stock_data.price_history, symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if constants.DEBUG:
                print(f"🔄 Fetching fresh data for {symbol} Momentum calculation using global fetch system")

            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            fetch_stock_data(symbol, None, None, None, None, period="1y", interval="1d")
            
            # Wait for data to be fetched and cached, then process for Momentum
            _wait_for_cache_and_process_momentum(symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        
    except Exception as e:
        print(f"❌ Error in Momentum data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _wait_for_cache_and_process_momentum(symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process Momentum"""
    try:
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
            
            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                if constants.DEBUG:
                    print(f"✅ Cache updated for {symbol}, processing Momentum")
                _process_mom_data(stock_data.price_history, symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return
            
            time.sleep(0.5)
        
        # Timeout
        if constants.DEBUG:
            print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_mom_data(stock_data.price_history, symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _process_mom_data(price_df, symbol, momentum_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Process the cached price data to calculate and display MOM using TA-Lib"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Calculating MOM...")

        if 'close' not in price_df.columns:
            if constants.DEBUG:
                print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Invalid price data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return

        close_prices = price_df['close'].dropna()
        if len(close_prices) < 11:  # MOM(timeperiod=10) needs at least 11 data points
            if constants.DEBUG:
                print(f"❌ Insufficient price data for {symbol}: {len(close_prices)} points")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Insufficient data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return

        # Calculate Momentum using TA-Lib
        momentum = talib.MOM(close_prices, timeperiod=10)
        momentum = momentum.dropna()
        
        if momentum is None or len(momentum) == 0:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "MOM calculation failed")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return

        print(f"Momentum values for {symbol}: \n{momentum.tail()}") 

        try:
            full_dates = price_df.index
            if len(full_dates) > len(momentum):
                mom_dates = full_dates[-len(momentum):]
            else:
                mom_dates = full_dates

            x_data = [date.timestamp() for date in mom_dates]
            y_data = momentum.tolist()
            
        except Exception as e:
            if constants.DEBUG:
                print(f"⚠️ Date processing failed for {symbol}: {e}, using sequential")
            x_data = list(range(len(momentum)))
            y_data = momentum.tolist()

        if dpg.does_item_exist(momentum_line_tag):
            dpg.set_value(momentum_line_tag, [x_data, y_data])
            print(f"📊 Updated MOM plot for {symbol} with {len(x_data)} points")

        if dpg.does_item_exist(x_axis_tag) and len(x_data) > 0:
            if isinstance(x_data[0], (int, float)) and x_data[0] > 1000000000:
                dpg.set_axis_limits(x_axis_tag, min(x_data), max(x_data))
                dpg.configure_item(x_axis_tag, time=True)
            else:
                dpg.set_axis_limits(x_axis_tag, 0, len(x_data))

        if dpg.does_item_exist(y_axis_tag) and y_data:
            min_val = min(y_data)
            max_val = max(y_data)
            if min_val == max_val:
                min_val -= 1
                max_val += 1
            # Add some padding to the limits
            dpg.set_axis_limits(y_axis_tag, min_val * 0.98, max_val * 1.02)

        if dpg.does_item_exist(status_tag):
            latest_mom = momentum.iloc[-1]
            status_text = f"MOM: {latest_mom:.2f} [TA-Lib]"
            dpg.set_value(status_tag, status_text)
            if latest_mom > 0:
                # Green
                dpg.configure_item(status_tag, color=[0, 255, 0])
            elif latest_mom < 0:
                # Red
                dpg.configure_item(status_tag, color=[255, 0, 0])
            else:
                dpg.configure_item(status_tag, color=[255, 255, 255])

    except Exception as e:
        print(f"❌ Error processing MOM data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Processing error: {str(e)[:20]}")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
def cleanup_mom_plot_tracking(symbol):
    """Clean up MOM plot tracking when a stock is removed"""
    global plot_tag_to_text_tag
    
    try:
        keys_to_remove = []
        for plot_tag in plot_tag_to_text_tag.keys():
            if symbol in plot_tag:
                keys_to_remove.append(plot_tag)
        
        for key in keys_to_remove:
            del plot_tag_to_text_tag[key]
            print(f"🧹 Cleaned up MOM plot tracking for {symbol}")
            
    except Exception as e:
        print(f"⚠️ Error cleaning up MOM tracking: {e}")