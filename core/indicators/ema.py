# core/indicators/ema.py - Pure Python EMA calculation
# No UI dependencies - just data processing

import numpy as np
import pandas as pd
import talib
from core.utils import get_close_column

def calculate_ema(prices: np.ndarray, timeperiod: int = 12) -> np.ndarray:
    """
    Calculate Exponential Moving Average using TA-Lib
    
    Args:
        prices: Array of closing prices
        timeperiod: EMA period (default 12)
    
    Returns:
        Array of EMA values
    """
    return talib.EMA(prices, timeperiod=timeperiod)


def calculate_ema_crossover(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26):
    """
    Calculate EMA crossover signals
    
    Args:
        df: DataFrame with 'close' or 'Close' column
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
    
    Returns:
        DataFrame with 'price', 'ema_fast', 'ema_slow' columns
    """
    close_prices = get_close_column(df)
    
    if len(close_prices) < slow_period:
        raise ValueError(f"Insufficient data: need at least {slow_period} points, got {len(close_prices)}")
    
    # Calculate EMAs
    ema_fast = talib.EMA(close_prices, timeperiod=fast_period)
    ema_slow = talib.EMA(close_prices, timeperiod=slow_period)
    
    # Remove NaN values
    valid_indices = ~(np.isnan(ema_fast) | np.isnan(ema_slow))
    
    result_df = pd.DataFrame({
        'price': close_prices[valid_indices],
        'ema_fast': ema_fast[valid_indices],
        'ema_slow': ema_slow[valid_indices],
        'date': df.index[len(close_prices) - np.sum(valid_indices):] if len(df) > 0 else range(np.sum(valid_indices))
    })
    
    return result_df


def detect_ema_crossovers(ema_fast: np.ndarray, ema_slow: np.ndarray):
    """
    Detect crossover points between two EMAs
    
    Returns:
        List of crossover indices (negative=bearish, positive=bullish)
    """
    crossovers = []
    
    for i in range(1, len(ema_fast)):
        # Bullish crossover (fast crosses above slow)
        if ema_fast[i-1] <= ema_slow[i-1] and ema_fast[i] > ema_slow[i]:
            crossovers.append((i, 'bullish'))
        # Bearish crossover (fast crosses below slow)
        elif ema_fast[i-1] >= ema_slow[i-1] and ema_fast[i] < ema_slow[i]:
            crossovers.append((i, 'bearish'))
    
    return crossovers
