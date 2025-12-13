# core/indicators/patterns.py - Candlestick pattern detection

import numpy as np
import pandas as pd
import talib


def detect_doji(open_prices: np.ndarray, high_prices: np.ndarray, 
                low_prices: np.ndarray, close_prices: np.ndarray) -> np.ndarray:
    """
    Detect Doji candlestick patterns
    
    Returns:
        Array with 100 for Doji, 0 otherwise
    """
    return talib.CDLDOJI(open_prices, high_prices, low_prices, close_prices)


def detect_hammer(open_prices: np.ndarray, high_prices: np.ndarray, 
                  low_prices: np.ndarray, close_prices: np.ndarray) -> np.ndarray:
    """
    Detect Hammer candlestick patterns
    
    Returns:
        Array with 100 for Hammer, 0 otherwise
    """
    return talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)
