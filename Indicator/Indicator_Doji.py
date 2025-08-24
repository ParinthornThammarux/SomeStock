# components/indicator/indicator_Doji.py

import dearpygui.dearpygui as dpg
import numpy as np
import time
import threading

from utils import constants
from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data

def create_doji_chart_for_stock(parent_tag, symbol, container_height=540):
    """
    Create a candlestick chart for a stock and mark doji candles
    """
    try:
        print(f"📊 Creating Doji chart for {symbol}")

        # tags
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"doji_chart_container_{symbol}_{timestamp}"
        plot_tag = f"doji_plot_{symbol}_{timestamp}"
        x_axis_tag = f"doji_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"doji_y_axis_{symbol}_{timestamp}"
        candle_tag = f"candle_series_{symbol}_{timestamp}"
        marker_tag = f"doji_marker_{symbol}_{timestamp}"

        # chart container
        with dpg.child_window(width=-1, height=container_height, parent=parent_tag, tag=chart_container_tag):
            with dpg.group(horizontal=True):
                dpg.add_text(f"Doji Candles : {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"doji_status_{symbol}_{timestamp}", color=[255, 255, 0])

            dpg.add_separator()
            dpg.add_spacer(height=5)

            # candlestick plot
            with dpg.plot(label="Doji Candles", height=-1, width=-1, tag=plot_tag, crosshairs=True):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag=x_axis_tag, time=True)
                dpg.add_plot_axis(dpg.mvYAxis, label="Price", tag=y_axis_tag)

    
                # candlestick series placeholder
                dpg.add_candle_series([], [], [], [], [], parent=y_axis_tag, tag=candle_tag)
                # doji markers
                dpg.add_scatter_series([], [], label="Doji", parent=y_axis_tag, tag=marker_tag)

        # background thread: fetch + detect dojis
        thread = threading.Thread(
            target=_fetch_and_plot_doji,
            args=(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, f"doji_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()

        return chart_container_tag

    except Exception as e:
        print(f"❌ Error creating Doji chart for {symbol}: {e}")
        return None

def _fetch_and_plot_doji(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Fetch stock data and detect/plot doji candles"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])

        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")

        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} doji detection")
            _process_doji_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if constants.DEBUG:
                print(f"🔄 Fetching fresh data for {symbol} doji detection")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")

            fetch_stock_data(symbol, None, None, None, None, period="1y", interval="1d")
            _wait_for_cache_and_process_doji(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)

    except Exception as e:
        print(f"❌ Error in doji data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])
            
def _wait_for_cache_and_process_doji(symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process doji detection"""
    try:
        start_time = time.time()

        while time.time() - start_time < max_wait:
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")

            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                if constants.DEBUG:
                    print(f"✅ Cache updated for {symbol}, processing doji detection")
                _process_doji_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return

            time.sleep(0.5)

        if constants.DEBUG:
            print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_doji_data(stock_data.price_history, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])

    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])       

def _process_doji_data(price_df, symbol, candle_tag, marker_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Process cached price data to detect and display Doji candles (simple version)"""
    try:
        df = price_df.copy()
        if df is None or df.empty:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data")
            return

        # Doji detection (body < 10% of range)
        body = abs(df["close"] - df["open"])
        range_ = df["high"] - df["low"]
        doji_mask = (body / range_) < 0.1
        doji_dates = df.index[doji_mask]
        doji_prices = df["close"][doji_mask]

        print(f"🕯️ {symbol} - Detected Doji on dates: {[d.strftime('%Y-%m-%d') for d in doji_dates]}")

        x_data = [date.timestamp() for date in df.index]
        dpg.set_value(candle_tag, [x_data, df["open"].tolist(), df["close"].tolist(), df["low"].tolist(), df["high"].tolist()])

        # Doji Markers
        dx = [d.timestamp() for d in doji_dates]
        dy = doji_prices.tolist()
        dpg.set_value(marker_tag, [dx, dy])

        if x_data:
            x_min, x_max = min(x_data), max(x_data)
            x_pad = (x_max - x_min) * 0.02
            dpg.set_axis_limits(x_axis_tag, x_min - x_pad, x_max + x_pad)

            y_min = min(df["low"].min(), min(dy) if dy else df["low"].min())
            y_max = max(df["high"].max(), max(dy) if dy else df["high"].max())
            y_range = y_max - y_min
            dpg.set_axis_limits(y_axis_tag, y_min - y_range*0.05, y_max + y_range*0.05)
            
        # Status
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Detected {len(dx)} Doji candles on dates: {[d.strftime('%Y-%m-%d') for d in doji_dates]}")
            dpg.configure_item(status_tag, color=[0, 255, 255] if len(dx) > 0 else [255, 255, 255])
    except Exception as e:
        print(f"❌ Error Doji detection for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Doji detection error")
            dpg.configure_item(status_tag, color=[255, 100, 100])
