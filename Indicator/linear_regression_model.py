# Indicator/Models/linear_regression_model.py

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import os
from pathlib import Path
import time
import pickle

# Create models cache directory
MODELS_CACHE_DIR = Path("cache/Models")
MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class LinearRegressionModel(nn.Module):
    """Simple linear regression model for stock price prediction"""
    
    def __init__(self, input_size=1):
        super(LinearRegressionModel, self).__init__()
        self.linear = nn.Linear(input_size, 1)
    
    def forward(self, x):
        return self.linear(x)

class StockLinearRegressionPredictor:
    """Stock price predictor using linear regression with caching"""
    
    def __init__(self, symbol, cache_duration_hours=24):
        self.symbol = symbol
        self.cache_duration = cache_duration_hours * 3600  # Convert to seconds
        self.model = None
        self.scaler_params = None
        self.model_path = MODELS_CACHE_DIR / f"{symbol}_linear_model.pth"
        self.metadata_path = MODELS_CACHE_DIR / f"{symbol}_linear_metadata.pkl"
        
    def _is_cache_valid(self):
        """Check if cached model is still valid"""
        if not (self.model_path.exists() and self.metadata_path.exists()):
            return False
        
        try:
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Check if cache is within valid time window
            cache_age = time.time() - metadata.get('timestamp', 0)
            return cache_age < self.cache_duration
            
        except Exception as e:
            print(f"❌ Error checking cache validity: {e}")
            return False
    
    def _save_model_to_cache(self, model, scaler_params, training_loss):
        """Save trained model and metadata to cache"""
        try:
            # Save model state
            torch.save(model.state_dict(), self.model_path)
            
            # Save metadata
            metadata = {
                'symbol': self.symbol,
                'timestamp': time.time(),
                'scaler_params': scaler_params,
                'training_loss': training_loss,
                'model_type': 'LinearRegression'
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            print(f"✅ Model cached for {self.symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving model to cache: {e}")
            return False
    
    def _load_model_from_cache(self):
        """Load model and metadata from cache"""
        try:
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Load model
            model = LinearRegressionModel(input_size=1)
            model.load_state_dict(torch.load(self.model_path))
            model.eval()
            
            self.model = model
            self.scaler_params = metadata['scaler_params']
            
            print(f"📦 Loaded cached model for {self.symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model from cache: {e}")
            return False
    
    def train_model(self, price_data, epochs=1000, learning_rate=0.01):
        """Train linear regression model on price data"""
        try:
            if len(price_data) < 10:
                print(f"❌ Insufficient data for training: {len(price_data)} points")
                return None, None
            
            print(f"🔄 Training linear regression model for {self.symbol}...")
            
            # Prepare data
            prices = np.array(price_data).astype(np.float32)
            x = np.arange(len(prices)).reshape(-1, 1).astype(np.float32)
            y = prices.reshape(-1, 1)
            
            # Normalize data
            x_mean, x_std = x.mean(), x.std()
            y_mean, y_std = y.mean(), y.std()
            
            x_norm = (x - x_mean) / (x_std + 1e-8)
            y_norm = (y - y_mean) / (y_std + 1e-8)
            
            # Store normalization parameters
            self.scaler_params = {
                'x_mean': x_mean, 'x_std': x_std,
                'y_mean': y_mean, 'y_std': y_std
            }
            
            # Convert to tensors
            x_tensor = torch.from_numpy(x_norm)
            y_tensor = torch.from_numpy(y_norm)
            
            # Initialize model
            model = LinearRegressionModel(input_size=1)
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
            
            # Training loop
            model.train()
            final_loss = 0
            
            for epoch in range(epochs):
                optimizer.zero_grad()
                predictions = model(x_tensor)
                loss = criterion(predictions, y_tensor)
                loss.backward()
                optimizer.step()
                
                if epoch % 100 == 0:
                    print(f"Epoch {epoch}/{epochs}, Loss: {loss.item():.6f}")
                
                final_loss = loss.item()
            
            model.eval()
            self.model = model
            
            # Save to cache
            self._save_model_to_cache(model, self.scaler_params, final_loss)
            
            print(f"✅ Model training completed for {self.symbol}, Final Loss: {final_loss:.6f}")
            return model, self.scaler_params
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return None, None
    
    def get_or_train_model(self, price_data):
        """Get cached model or train new one if cache is invalid"""
        try:
            # Try to load from cache first
            if self._is_cache_valid() and self._load_model_from_cache():
                print(f"📦 Using cached model for {self.symbol}")
                return self.model, self.scaler_params
            
            # Cache is invalid or doesn't exist, train new model
            print(f"🔄 Cache invalid/missing for {self.symbol}, training new model...")
            return self.train_model(price_data)
            
        except Exception as e:
            print(f"❌ Error in get_or_train_model: {e}")
            return None, None
    
    def predict_trend(self, price_data, future_points=10):
        """Predict future price trend"""
        try:
            model, scaler_params = self.get_or_train_model(price_data)
            
            if model is None or scaler_params is None:
                return None, None
            
            # Prepare prediction data
            current_length = len(price_data)
            future_x = np.arange(current_length, current_length + future_points).reshape(-1, 1).astype(np.float32)
            
            # Normalize using stored parameters
            future_x_norm = (future_x - scaler_params['x_mean']) / (scaler_params['x_std'] + 1e-8)
            future_x_tensor = torch.from_numpy(future_x_norm)
            
            # Make predictions
            with torch.no_grad():
                future_predictions_norm = model(future_x_tensor)
                future_predictions = (future_predictions_norm.numpy() * scaler_params['y_std']) + scaler_params['y_mean']
            
            # Generate regression line for current data
            current_x = np.arange(current_length).reshape(-1, 1).astype(np.float32)
            current_x_norm = (current_x - scaler_params['x_mean']) / (scaler_params['x_std'] + 1e-8)
            current_x_tensor = torch.from_numpy(current_x_norm)
            
            with torch.no_grad():
                current_predictions_norm = model(current_x_tensor)
                current_predictions = (current_predictions_norm.numpy() * scaler_params['y_std']) + scaler_params['y_mean']
            
            return current_predictions.flatten(), future_predictions.flatten()
            
        except Exception as e:
            print(f"❌ Error in prediction: {e}")
            return None, None
    
    @staticmethod
    def clear_cache_for_symbol(symbol):
        """Clear cached model for a specific symbol"""
        try:
            model_path = MODELS_CACHE_DIR / f"{symbol}_linear_model.pth"
            metadata_path = MODELS_CACHE_DIR / f"{symbol}_linear_metadata.pkl"
            
            removed_files = []
            if model_path.exists():
                model_path.unlink()
                removed_files.append(str(model_path))
            
            if metadata_path.exists():
                metadata_path.unlink()
                removed_files.append(str(metadata_path))
            
            if removed_files:
                print(f"🗑️ Cleared cache for {symbol}: {removed_files}")
            else:
                print(f"ℹ️ No cache found for {symbol}")
                
        except Exception as e:
            print(f"❌ Error clearing cache for {symbol}: {e}")
    
    @staticmethod
    def clear_all_cache():
        """Clear all cached models"""
        try:
            cache_files = list(MODELS_CACHE_DIR.glob("*_linear_*"))
            removed_count = 0
            
            for file_path in cache_files:
                file_path.unlink()
                removed_count += 1
            
            print(f"🗑️ Cleared {removed_count} cached model files")
            
        except Exception as e:
            print(f"❌ Error clearing all cache: {e}")
    
    @staticmethod
    def get_cache_info():
        """Get information about cached models"""
        try:
            cache_files = list(MODELS_CACHE_DIR.glob("*_linear_metadata.pkl"))
            cache_info = []
            
            for metadata_file in cache_files:
                try:
                    with open(metadata_file, 'rb') as f:
                        metadata = pickle.load(f)
                    
                    cache_age = time.time() - metadata.get('timestamp', 0)
                    cache_info.append({
                        'symbol': metadata.get('symbol', 'Unknown'),
                        'age_hours': cache_age / 3600,
                        'training_loss': metadata.get('training_loss', 'Unknown'),
                        'model_type': metadata.get('model_type', 'Unknown')
                    })
                    
                except Exception:
                    continue
            
            return cache_info
            
        except Exception as e:
            print(f"❌ Error getting cache info: {e}")
            return []

def get_linear_regression_prediction(symbol, price_data, future_points=10):
    """Convenience function to get linear regression prediction"""
    predictor = StockLinearRegressionPredictor(symbol)
    return predictor.predict_trend(price_data, future_points)

def clear_model_cache(symbol=None):
    """Convenience function to clear model cache"""
    if symbol:
        StockLinearRegressionPredictor.clear_cache_for_symbol(symbol)
    else:
        StockLinearRegressionPredictor.clear_all_cache()

def get_model_cache_info():
    """Convenience function to get cache information"""
    return StockLinearRegressionPredictor.get_cache_info()