# core/indicators/sma.py - Simple Moving Average calculation

import numpy as np
import pandas as pd
import talib
from core.utils import get_close_column


def calculate_sma(prices: np.ndarray, timeperiod: int = 20) -> np.ndarray:
    """
    Calculate Simple Moving Average using TA-Lib
    
    Args:
        prices: Array of closing prices
        timeperiod: SMA period (default 20)
    
    Returns:
        Array of SMA values
    """
    return talib.SMA(prices, timeperiod=timeperiod)


def calculate_sma_trend(df: pd.DataFrame, short_period: int = 20, long_period: int = 50):
    """
    Calculate trend using dual SMAs
    
    Args:
        df: DataFrame with 'close' or 'Close' column
        short_period: Short SMA period
        long_period: Long SMA period
    
    Returns:
        DataFrame with SMA values and trend signals
    """
    close_prices = get_close_column(df)
    
    sma_short = talib.SMA(close_prices, timeperiod=short_period)
    sma_long = talib.SMA(close_prices, timeperiod=long_period)
    
    # Remove NaN values
    valid_indices = ~(np.isnan(sma_short) | np.isnan(sma_long))
    
    result_df = pd.DataFrame({
        'price': close_prices[valid_indices],
        'sma_short': sma_short[valid_indices],
        'sma_long': sma_long[valid_indices],
    })
    
    return result_df
