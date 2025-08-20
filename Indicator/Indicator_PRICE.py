# components/graph/Indicator_Price.py - Simple Price Prediction

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
import time
import threading

from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data, find_tag_by_symbol
from Indicator.linear_regression_model import get_linear_regression_prediction, clear_model_cache

def create_price_chart_for_stock(parent_tag, symbol, container_height=350):
    """
    Create a simple price chart with PyTorch prediction for a specific stock
    Shows actual price history + single predicted next price point
    """
    try:
        print(f"📊 Creating simple price prediction chart for {symbol}")
        
        # Generate unique tags for this stock's price chart
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"price_chart_container_{symbol}_{timestamp}"
        plot_tag = f"price_plot_{symbol}_{timestamp}"
        x_axis_tag = f"price_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"price_y_axis_{symbol}_{timestamp}"
        
        # Only two line series: actual price and prediction
        actual_price_tag = f"actual_price_line_{symbol}_{timestamp}"
        prediction_tag = f"prediction_point_{symbol}_{timestamp}"
        
        # Create chart container
        with dpg.child_window(
            width=-1, 
            height=container_height, 
            border=True, 
            parent=parent_tag,
            tag=chart_container_tag
        ):
            # Simple header
            with dpg.group(horizontal=True):
                dpg.add_text(f"Price Prediction: {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"prediction_status_{symbol}_{timestamp}", color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Create the simple prediction plot
            with dpg.plot(
                label="", 
                height=-1, 
                width=-1, 
                tag=plot_tag
            ):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag=x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                
                # Initialize line series
                dpg.add_line_series([], [], parent=y_axis_tag, tag=actual_price_tag, label="Actual Price")
                dpg.add_scatter_series([], [], parent=y_axis_tag, tag=prediction_tag, label="Predicted Price")
                
                # Set initial axis limits
                dpg.set_axis_limits(x_axis_tag, 0, 100)
                dpg.set_axis_limits(y_axis_tag, 0, 200)
        
        # Start simple prediction analysis
        thread = threading.Thread(
            target=_fetch_and_predict_simple, 
            args=(symbol, {
                'actual_price': actual_price_tag,
                'prediction': prediction_tag,
                'x_axis': x_axis_tag,
                'y_axis': y_axis_tag,
                'plot': plot_tag,
                'status': f"prediction_status_{symbol}_{timestamp}"
            })
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating prediction chart for {symbol}: {e}")
        return None

def _fetch_and_predict_simple(symbol, chart_tags):
    """Simple fetch and predict - equivalent to predict_next_price function"""
    try:
        status_tag = chart_tags['status']
        
        # Update status
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Getting price data...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Get cached data
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} prediction")
            _process_simple_prediction(stock_data.price_history, symbol, chart_tags)
        else:
            print(f"🔄 Fetching data for {symbol} prediction")
            
            # Update status
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            # Fetch with longer period for better prediction (3 months of daily data)
            fetch_stock_data(symbol, None, None, None, None, period="1y", interval="1d")
            
            # Wait for data and process
            _wait_for_cache_and_predict_simple(symbol, chart_tags)
        
    except Exception as e:
        print(f"❌ Error in simple prediction for {symbol}: {e}")
        if dpg.does_item_exist(chart_tags['status']):
            dpg.set_value(chart_tags['status'], f"Error: {str(e)[:30]}...")
            dpg.configure_item(chart_tags['status'], color=[255, 100, 100])

def _wait_for_cache_and_predict_simple(symbol, chart_tags, max_wait=30):
    """Wait for the global fetch system to update cache, then process prediction"""
    try:
        start_time = time.time()
        status_tag = chart_tags['status']
        
        while time.time() - start_time < max_wait:
            # Check if cache has been updated with fresh data
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
            
            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                
                print(f"✅ Cache updated for {symbol}, processing prediction")
                _process_simple_prediction(stock_data.price_history, symbol, chart_tags)
                return
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout - try with whatever data we have
        print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_simple_prediction(stock_data.price_history, symbol, chart_tags)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(chart_tags['status']):
            dpg.set_value(chart_tags['status'], "Cache error")
            dpg.configure_item(chart_tags['status'], color=[255, 100, 100])

def _process_simple_prediction(price_df, symbol, chart_tags):
    """Process simple prediction - equivalent to predict_next_price function"""
    try:
        status_tag = chart_tags['status']
        
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Making prediction...")
        
        # Get close prices
        if 'close' not in price_df.columns:
            print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Invalid price data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        close_prices = price_df['close'].dropna().values
        
        if len(close_prices) < 20:  # Need reasonable amount of data
            print(f"❌ Insufficient price data for {symbol}: {len(close_prices)} points")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Insufficient data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        # Get prediction using the cached model system (equivalent to predict_next_price)
        predicted_price = predict_next_price(symbol, close_prices)
        
        if predicted_price is None:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Prediction failed")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        # Prepare chart data
        x_data = list(range(len(close_prices)))
        y_data = close_prices.tolist()
        
        # Prediction point (red dot at next time step)
        pred_x = [len(close_prices)]  # Next day
        pred_y = [predicted_price]
        
        # Update actual price line
        if dpg.does_item_exist(chart_tags['actual_price']):
            dpg.set_value(chart_tags['actual_price'], [x_data, y_data])
        
        # Update prediction point (red dot)
        if dpg.does_item_exist(chart_tags['prediction']):
            dpg.set_value(chart_tags['prediction'], [pred_x, pred_y])
        
        # Update axis limits
        all_prices = y_data + pred_y
        min_price = min(all_prices) * 0.995
        max_price = max(all_prices) * 1.005
        
        if dpg.does_item_exist(chart_tags['x_axis']):
            dpg.set_axis_limits(chart_tags['x_axis'], 0, len(close_prices) + 2)
        if dpg.does_item_exist(chart_tags['y_axis']):
            dpg.set_axis_limits(chart_tags['y_axis'], min_price, max_price)
        
        # Update status with prediction results
        current_price = close_prices[-1]
        change = predicted_price - current_price
        change_pct = (change / current_price) * 100
        
        try:
            # Calculate additional metrics
            data_points = len(close_prices)
            volatility = np.std(close_prices[-10:]) if len(close_prices) >= 10 else 0
            vol_pct = (volatility / current_price) * 100
            
            # Recent performance
            day_5_change = ((close_prices[-1] - close_prices[-5]) / close_prices[-5] * 100) if len(close_prices) >= 5 else 0
            
            # Model confidence (based on prediction magnitude)
            confidence = "High" if abs(change_pct) < 0.5 else "Medium" if abs(change_pct) < 2 else "Low"
            
            # Comprehensive status
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, 
                    f"Predicted: ${predicted_price:.2f} ({change_pct:+.1f}%) | "
                    f"Current: ${current_price:.2f} | 5D: {day_5_change:+.1f}% | "
                    f"Vol: {vol_pct:.1f}% | Confidence: {confidence} | Data: {data_points}pts"
                )
            if change > 0:
                dpg.configure_item(status_tag, color=[100, 255, 100])
            else :
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
        except Exception as e:
            # Fallback to simple version
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, f"Predicted: ${predicted_price:.2f} ({change_pct:+.1f}%)")
            if change > 0:
                dpg.configure_item(status_tag, color=[100, 255, 100])
            else :
                dpg.configure_item(status_tag, color=[255, 100, 100])
        
        print(f"📈 {symbol} - Predicted next close price: ${predicted_price:.2f}")
        print(f"    Current: ${current_price:.2f}, Change: {change:+.2f} ({change_pct:+.1f}%)")
        
    except Exception as e:
        print(f"❌ Error processing simple prediction for {symbol}: {e}")
        if dpg.does_item_exist(chart_tags['status']):
            dpg.set_value(chart_tags['status'], "Processing error")
            dpg.configure_item(chart_tags['status'], color=[255, 100, 100])

def predict_next_price(symbol, window_size=10, verbose=True):
    """
    Predict next price for a symbol using cached PyTorch model
    
    Args:
        symbol: Stock symbol to predict
        window_size: Window size for model (default 10) 
        verbose: Whether to print detailed output
    
    Returns:
        float: Predicted next price, or None if failed
    """
    try:
        # Get cached data
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if not (stock_data and stock_data.price_history is not None):
            if verbose:
                print(f"❌ No data available for {symbol}")
            return None
        
        close_prices = stock_data.price_history['close'].dropna().values
        
        if len(close_prices) < MINIMUM_DATA_POINTS:
            if verbose:
                print(f"❌ Insufficient data for {symbol}: {len(close_prices)} points")
            return None
        
        # Use the cached model system to get prediction
        current_trend, future_trend = get_linear_regression_prediction(
            symbol=symbol,
            price_data=close_prices,
            future_points=1
        )
        
        if future_trend is not None and len(future_trend) > 0:
            predicted_price = future_trend[0]
            
            if verbose:
                current_price = close_prices[-1]
                change = predicted_price - current_price
                change_pct = (change / current_price) * 100
                
                print(f"📈 {symbol} - Current: ${current_price:.2f}")
                print(f"📈 {symbol} - Predicted next close: ${predicted_price:.2f}")
                print(f"📈 {symbol} - Expected change: ${change:+.2f} ({change_pct:+.1f}%)")
            
            return predicted_price
        
        if verbose:
            print(f"❌ Prediction failed for {symbol}")
        return None
        
    except Exception as e:
        if verbose:
            print(f"❌ Error predicting {symbol}: {e}")
        return None
    
def create_price_prediction_summary(parent_tag, symbols):
    """
    Create a summary table of price predictions for multiple stocks
    
    Args:
        parent_tag: Parent container for the summary
        symbols: List of stock symbols to analyze
    """
    try:
        timestamp = str(int(time.time() * 1000))
        summary_tag = f"price_prediction_summary_{timestamp}"
        
        with dpg.child_window(
            width=-1, 
            height=200, 
            border=True, 
            parent=parent_tag,
            tag=summary_tag
        ):
            dpg.add_text("Price Prediction Summary", color=[255, 255, 255])
            dpg.add_separator()
            
            # Create summary table
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, 
                          borders_innerV=True, borders_outerV=True):
                dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Current", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Predicted", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Change", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Direction", width_fixed=True, init_width_or_weight=100)
                
                for symbol in symbols:
                    with dpg.table_row():
                        dpg.add_text(symbol)
                        dpg.add_text("Loading...", tag=f"current_price_{symbol}_{timestamp}")
                        dpg.add_text("...", tag=f"predicted_price_{symbol}_{timestamp}")
                        dpg.add_text("...", tag=f"price_change_{symbol}_{timestamp}")
                        dpg.add_text("Calculating", tag=f"price_direction_{symbol}_{timestamp}")
        
        return summary_tag
        
    except Exception as e:
        print(f"❌ Error creating price prediction summary: {e}")
        return None

# Utility functions for external access
def get_next_price_prediction(symbol):
    """
    Get next price prediction for a symbol
    
    Returns:
        dict: Prediction results
    """
    try:
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            close_prices = stock_data.price_history['close'].dropna().values
            
            if len(close_prices) > 0:
                predicted_price = predict_next_price(symbol, close_prices)
                
                if predicted_price is not None:
                    current_price = close_prices[-1]
                    change = predicted_price - current_price
                    change_percent = (change / current_price) * 100
                    
                    return {
                        'symbol': symbol,
                        'current_price': current_price,
                        'predicted_price': predicted_price,
                        'change': change,
                        'change_percent': change_percent,
                        'direction': 'Up' if change > 0 else 'Down'
                    }
        
        return {"error": "No data available"}
        
    except Exception as e:
        print(f"❌ Error getting price prediction for {symbol}: {e}")
        return {"error": str(e)}

def clear_price_model_cache(symbol=None):
    """Clear cached price models"""
    clear_model_cache(symbol)
    if symbol:
        print(f"🗑️ Cleared price model cache for {symbol}")
    else:
        print("🗑️ Cleared all price model caches")

def show_cache_info():
    """Display cache information"""
    from Indicator.linear_regression_model import get_model_cache_info
    cache_info = get_model_cache_info()
    
    if cache_info:
        print("📊 Cached Price Models:")
        for info in cache_info:
            print(f"  • {info['symbol']}: {info['age_hours']:.1f}h old, Loss: {info['training_loss']}")
    else:
        print("📊 No cached price models found")
        
# Configuration
DEFAULT_WINDOW_SIZE = 10
DEFAULT_PREDICTION_POINTS = 1
MINIMUM_DATA_POINTS = 20