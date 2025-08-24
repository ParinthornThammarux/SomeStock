# components/indicator/indicator_Hammer.py

import dearpygui.dearpygui as dpg
import numpy as np
import time
import threading

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data

def create_hammer_chart_for_stock(parent_tag, symbol, container_height=540):
    """
    Create a candlestick chart for a stock and mark hammer candles
    """
    try:
        print(f"📊 Creating Hammer chart for {symbol}")

        # tags
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"hammer_chart_container_{symbol}_{timestamp}"
        plot_tag = f"hammer_plot_{symbol}_{timestamp}"
        x_axis_tag = f"hammer_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"hammer_y_axis_{symbol}_{timestamp}"
        candle_tag = f"candle_series_{symbol}_{timestamp}"
        marker_tag = f"hammer_marker_{symbol}_{timestamp}"

        # chart container
        with dpg.child_window(width=-1, height=container_height, parent=parent_tag, tag=chart_container_tag):
            with dpg.group(horizontal=True):
                dpg.add_text(f"Hammer Candles : {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"hammer_status_{symbol}_{timestamp}", color=[255, 255, 0])

            dpg.add_separator()
            dpg.add_spacer(height=5)

            # candlestick plot
            with dpg.plot(label="Hammer Candles", height=-1, width=-1, tag=plot_tag, crosshairs=True):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag=x_axis_tag, time=True)
                dpg.add_plot_axis(dpg.mvYAxis, label="Price", tag=y_axis_tag)

    
                # candlestick series placeholder
                dpg.add_candle_series([], [], [], [], [], parent=y_axis_tag, tag=candle_tag)
                # hammer markers
                dpg.add_scatter_series([], [], label="Hammer", parent=y_axis_tag, tag=marker_tag)

        # background thread: fetch + detect hammers
        thread = threading.Thread(
            target=_fetch_and_plot_hammer,
            args=(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, f"hammer_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()

        return chart_container_tag

    except Exception as e:
        print(f"❌ Error creating Hammer chart for {symbol}: {e}")
        return None

def _fetch_and_plot_hammer(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Fetch stock data and detect/plot hammer candles"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])

        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")

        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} hammer detection")
            _process_hammer_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if constants.DEBUG:
                print(f"🔄 Fetching fresh data for {symbol} hammer detection")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")

            fetch_stock_data(symbol, None, None, None, None, period="1y", interval="1d")
            _wait_for_cache_and_process_hammer(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)

    except Exception as e:
        print(f"❌ Error in hammer data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
def _wait_for_cache_and_process_hammer(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process hammer detection"""
    try:
        start_time = time.time()

        while time.time() - start_time < max_wait:
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")

            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                if constants.DEBUG:
                    print(f"✅ Cache updated for {symbol}, processing hammer detection")
                _process_hammer_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return

            time.sleep(0.5)

        if constants.DEBUG:
            print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_hammer_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])

    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])       

def _process_hammer_data(price_df, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Process the cached price data to detect and display hammer candles with zoom/pan enabled"""
    try:
        df = price_df.copy()
        if df is None or df.empty:
            dpg.set_value(status_tag, "No data")
            return

        # hammer detection logic
        body = abs(df["close"] - df["open"])
        lower_shadow = np.where(df["close"] > df["open"], df["open"], df["close"]) - df["low"]
        upper_shadow = df["high"] - np.where(df["close"] > df["open"], df["close"], df["open"])

        hammer_mask = (lower_shadow >= 2 * body) & (upper_shadow <= 0.1 * body)
        hammer_dates = df.index[hammer_mask]
        hammer_prices = df["close"][hammer_mask]

        print(f"🔨 {symbol} - Detected Hammer on dates: {[d.strftime('%Y-%m-%d') for d in hammer_dates]}")

        # build candlestick arrays
        x_data = [date.timestamp() for date in df.index]
        dpg.set_value(candle_tag, [x_data, df["open"].tolist(), df["close"].tolist(), df["low"].tolist(), df["high"].tolist()])
        
        # hammer markers (scatter on closing price)
        hx = [d.timestamp() for d in hammer_dates]
        hy = hammer_prices.tolist()
        dpg.set_value(marker_tag, [hx, hy])

        # Horizontal padding (time axis)
        x_min = min(x_data)
        x_max = max(x_data)
        x_padding = (x_max - x_min) * 0.02  # 2% padding
        dpg.set_axis_limits(x_axis_tag, x_min - x_padding, x_max + x_padding)

        # Vertical padding (price axis)
        y_min = min(df["low"].min(), min(hy) if hy else df["low"].min())
        y_max = max(df["high"].max(), max(hy) if hy else df["high"].max())
        y_range = y_max - y_min
        dpg.set_axis_limits(y_axis_tag, y_min - y_range * 0.05, y_max + y_range * 0.05)

    
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Detected {len(hx)} Hammers on dates: {[d.strftime('%Y-%m-%d') for d in hammer_dates]}")
            dpg.configure_item(status_tag, color=[0, 255, 0] if len(hx) > 0 else [255, 255, 255])

    except Exception as e:
        print(f"❌ Error hammer detection for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Hammer detection error")
            dpg.configure_item(status_tag, color=[255, 100, 100])

                   