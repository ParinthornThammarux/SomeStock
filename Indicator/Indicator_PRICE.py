# components/graph/graph_price.py

import dearpygui.dearpygui as dpg
import numpy as np
import pandas as pd
import time
import threading
import os
import math
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

# Import the global fetching system
from utils.stock_fetch_layer import fetch_stock_data
from components.stock.stock_data_manager import get_cached_stock_data, find_tag_by_symbol

# ==================== Dataset ====================
class StockDataset(Dataset):
    def __init__(self, prices, window_size=10):
        self.X, self.y = [], []
        for i in range(len(prices) - window_size):
            self.X.append(prices[i:i + window_size])
            self.y.append(prices[i + window_size])
        self.X = np.array(self.X, dtype=np.float32)
        self.y = np.array(self.y, dtype=np.float32).reshape(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ==================== Model ====================
class StockPriceModel(nn.Module):
    def __init__(self, input_size):
        super(StockPriceModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)

# ==================== Main Chart Creation Function ====================
def create_price_chart_for_stock(parent_tag, symbol, container_height=280):
    """
    Create a price prediction chart for a specific stock within a container
    
    Args:
        parent_tag: Parent container tag to create the chart in
        symbol: Stock symbol to analyze
        container_height: Height of the chart container
    """
    try:
        print(f"💰 Creating price prediction chart for {symbol}")
        
        # Generate unique tags for this stock's price chart
        timestamp = str(int(time.time() * 1000))
        chart_container_tag = f"price_chart_container_{symbol}_{timestamp}"
        plot_tag = f"price_plot_{symbol}_{timestamp}"
        x_axis_tag = f"price_x_axis_{symbol}_{timestamp}"
        y_axis_tag = f"price_y_axis_{symbol}_{timestamp}"
        actual_line_tag = f"price_actual_line_{symbol}_{timestamp}"
        prediction_line_tag = f"price_prediction_line_{symbol}_{timestamp}"
        linear_line_tag = f"price_linear_line_{symbol}_{timestamp}"
        
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
                dpg.add_text(f"Price Analysis: {symbol}", color=[255, 255, 255])
                dpg.add_spacer(width=20)
                dpg.add_text("Loading...", tag=f"price_status_{symbol}_{timestamp}", color=[255, 255, 0])
            
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Create the plot
            with dpg.plot(
                label="", 
                height=-1, 
                width=-1, 
                tag=plot_tag
            ):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Time Period", tag=x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                
                # Initialize empty line series
                dpg.add_line_series([], [], parent=y_axis_tag, tag=actual_line_tag, label=f"Actual {symbol}")
                dpg.add_line_series([], [], parent=y_axis_tag, tag=prediction_line_tag, label=f"ML Prediction")
                dpg.add_line_series([], [], parent=y_axis_tag, tag=linear_line_tag, label=f"Linear Trend")
                
                # Set initial axis limits
                dpg.set_axis_limits(x_axis_tag, 0, 100)
                dpg.set_axis_limits(y_axis_tag, 0, 200)
        
        # Start price analysis in background
        thread = threading.Thread(
            target=_fetch_and_analyze_price_async, 
            args=(symbol, actual_line_tag, prediction_line_tag, linear_line_tag, 
                  x_axis_tag, y_axis_tag, plot_tag, f"price_status_{symbol}_{timestamp}")
        )
        thread.daemon = True
        thread.start()
        
        return chart_container_tag
        
    except Exception as e:
        print(f"❌ Error creating price chart for {symbol}: {e}")
        return None

def _fetch_and_analyze_price_async(symbol, actual_line_tag, prediction_line_tag, linear_line_tag,
                                   x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Use the global fetching system to get data and perform price analysis"""
    try:
        # Update status
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Checking cache...")
            dpg.configure_item(status_tag, color=[255, 255, 0])
        
        # Try to get cached data first
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        
        if stock_data and stock_data.price_history is not None and not stock_data.price_history.empty and stock_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol} price analysis")
            _process_price_data(stock_data.price_history, symbol, actual_line_tag, prediction_line_tag, 
                              linear_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            print(f"🔄 Fetching fresh data for {symbol} price analysis using global fetch system")
            
            # Update status
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Fetching fresh data...")
            
            # Use the global fetch system - this will update the cache
            fetch_stock_data(symbol, actual_line_tag, x_axis_tag, y_axis_tag, plot_tag)
            
            # Wait for data to be fetched and cached, then process for price analysis
            _wait_for_cache_and_process_price(symbol, actual_line_tag, prediction_line_tag, linear_line_tag,
                                            x_axis_tag, y_axis_tag, plot_tag, status_tag)
        
    except Exception as e:
        print(f"❌ Error in price data fetching for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Error: {str(e)[:30]}...")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _wait_for_cache_and_process_price(symbol, actual_line_tag, prediction_line_tag, linear_line_tag,
                                     x_axis_tag, y_axis_tag, plot_tag, status_tag, max_wait=30):
    """Wait for the global fetch system to update cache, then process price analysis"""
    try:
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check if cache has been updated with fresh data
            stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
            
            if (stock_data and stock_data.price_history is not None 
                and not stock_data.price_history.empty 
                and stock_data.is_cache_valid()):
                
                print(f"✅ Cache updated for {symbol}, processing price analysis")
                _process_price_data(stock_data.price_history, symbol, actual_line_tag, prediction_line_tag,
                                  linear_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
                return
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout - try with whatever data we have
        print(f"⚠️ Timeout waiting for {symbol} data, using available data")
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            _process_price_data(stock_data.price_history, symbol, actual_line_tag, prediction_line_tag,
                              linear_line_tag, x_axis_tag, y_axis_tag, plot_tag, status_tag)
        else:
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "No data available")
                dpg.configure_item(status_tag, color=[255, 100, 100])
                
    except Exception as e:
        print(f"❌ Error waiting for cache update: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Cache error")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _process_price_data(price_df, symbol, actual_line_tag, prediction_line_tag, linear_line_tag,
                       x_axis_tag, y_axis_tag, plot_tag, status_tag):
    """Process the cached price data to perform price analysis and prediction"""
    try:
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Analyzing prices...")
        
        # Get close prices from the DataFrame
        if 'close' not in price_df.columns:
            print(f"❌ No 'close' column in price data for {symbol}")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Invalid price data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        close_prices = price_df['close'].dropna().values
        
        if len(close_prices) < 20:  # Need sufficient data for ML analysis
            print(f"❌ Insufficient price data for {symbol}: {len(close_prices)} points")
            if dpg.does_item_exist(status_tag):
                dpg.set_value(status_tag, "Insufficient data")
                dpg.configure_item(status_tag, color=[255, 100, 100])
            return
        
        # Prepare x-axis data
        x_data = list(range(len(close_prices)))
        
        # 1. Plot actual prices
        if dpg.does_item_exist(actual_line_tag):
            dpg.set_value(actual_line_tag, [x_data, close_prices.tolist()])
        
        # 2. Calculate and plot linear regression
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Computing linear trend...")
        
        linear_trend = _calculate_linear_regression(close_prices)
        if linear_trend is not None and dpg.does_item_exist(linear_line_tag):
            dpg.set_value(linear_line_tag, [x_data, linear_trend.tolist()])
        
        # 3. Calculate ML prediction
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, "Training ML model...")
        
        ml_prediction = _calculate_ml_prediction(symbol, close_prices)
        if ml_prediction is not None and dpg.does_item_exist(prediction_line_tag):
            # Extend x-axis for prediction
            pred_x = x_data + [len(close_prices)]
            pred_y = close_prices.tolist() + [ml_prediction]
            dpg.set_value(prediction_line_tag, [pred_x, pred_y])
        
        # Update axis limits
        if dpg.does_item_exist(x_axis_tag):
            dpg.set_axis_limits(x_axis_tag, 0, len(x_data) + 1)
        if dpg.does_item_exist(y_axis_tag):
            price_min = np.min(close_prices) * 0.95
            price_max = np.max(close_prices) * 1.05
            dpg.set_axis_limits(y_axis_tag, price_min, price_max)
        
        # Update status with analysis results
        current_price = close_prices[-1]
        trend_direction = "📈 Upward" if linear_trend[-1] > linear_trend[0] else "📉 Downward"
        prediction_text = f"${ml_prediction:.2f}" if ml_prediction else "N/A"
        
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Current: ${current_price:.2f} | Pred: {prediction_text} | {trend_direction}")
            dpg.configure_item(status_tag, color=[100, 255, 100])
        
        print(f"✅ Price analysis updated for {symbol} - Current: ${current_price:.2f}, Prediction: {prediction_text}")
        
    except Exception as e:
        print(f"❌ Error processing price data for {symbol}: {e}")
        if dpg.does_item_exist(status_tag):
            dpg.set_value(status_tag, f"Analysis error")
            dpg.configure_item(status_tag, color=[255, 100, 100])

def _calculate_linear_regression(prices):
    """Calculate linear regression trend line"""
    try:
        x = np.arange(len(prices)).reshape(-1, 1)
        y = prices.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(x, y)
        trend = model.predict(x).flatten()
        
        return trend
        
    except Exception as e:
        print(f"❌ Error calculating linear regression: {e}")
        return None

def _calculate_ml_prediction(symbol, prices, window_size=10):
    """Calculate ML-based price prediction"""
    try:
        if len(prices) < window_size + 10:  # Need enough data for training
            print(f"⚠️ Insufficient data for ML prediction: {len(prices)} points")
            return None
        
        # Check if model exists, if not train a simple one
        model_path = f"Model/{symbol}_model.pt"
        scaler_path = f"Model/{symbol}_scaler.npy"
        
        # Create models directory if it doesn't exist
        os.makedirs("Model", exist_ok=True)
        
        # Prepare data
        scaler = MinMaxScaler()
        scaled_prices = scaler.fit_transform(prices.reshape(-1, 1)).flatten()
        
        # Quick training for real-time prediction
        if len(scaled_prices) > window_size + 5:
            train_data = scaled_prices[:-5]  # Leave last 5 for validation
            
            dataset = StockDataset(train_data, window_size)
            if len(dataset) > 0:
                dataloader = DataLoader(dataset, batch_size=min(8, len(dataset)), shuffle=True)
                
                model = StockPriceModel(window_size)
                criterion = nn.MSELoss()
                optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
                
                # Quick training (fewer epochs for real-time)
                model.train()
                for epoch in range(20):  # Reduced epochs for speed
                    for x_batch, y_batch in dataloader:
                        pred = model(x_batch)
                        loss = criterion(pred, y_batch)
                        
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
                
                # Make prediction
                model.eval()
                recent = scaled_prices[-window_size:]
                input_tensor = torch.tensor(recent, dtype=torch.float32).unsqueeze(0)
                
                with torch.no_grad():
                    pred_scaled = model(input_tensor).item()
                    predicted_price = scaler.inverse_transform([[pred_scaled]])[0][0]
                
                return predicted_price
        
        return None
        
    except Exception as e:
        print(f"❌ Error calculating ML prediction: {e}")
        return None

# ==================== Utility Functions ====================
def get_price_prediction_for_symbol(symbol, window_size=10):
    """
    Get price prediction for a symbol
    
    Returns:
        tuple: (current_price, predicted_price, trend_direction)
    """
    try:
        stock_data = get_cached_stock_data(symbol, f"{symbol} Corp.")
        if stock_data and stock_data.price_history is not None:
            prices = stock_data.price_history['close'].dropna().values
            if len(prices) > 0:
                current_price = prices[-1]
                predicted_price = _calculate_ml_prediction(symbol, prices, window_size)
                
                # Calculate trend
                if len(prices) > 10:
                    recent_trend = np.mean(prices[-5:]) - np.mean(prices[-10:-5])
                    trend = "Up" if recent_trend > 0 else "Down"
                else:
                    trend = "Neutral"
                
                return current_price, predicted_price, trend
        
        return None, None, "No Data"
        
    except Exception as e:
        print(f"❌ Error getting price prediction for {symbol}: {e}")
        return None, None, "Error"

def verify_dependencies():
    """Verify required dependencies are installed"""
    try:
        import torch
        import sklearn
        print("✅ PyTorch and scikit-learn are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install torch scikit-learn")
        return False

# Call this when the module is imported
if __name__ == "__main__":
    verify_dependencies()