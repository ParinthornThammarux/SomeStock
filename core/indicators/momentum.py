# core/indicators/momentum.py - Momentum indicator calculation

import numpy as np
import pandas as pd
import talib


def calculate_momentum(prices: np.ndarray, timeperiod: int = 10) -> np.ndarray:
    """
    Calculate Momentum (Price Rate of Change)
    
    Args:
        prices: Array of closing prices
        timeperiod: Momentum period (default 10)
    
    Returns:
        Array of momentum values
    """
    return talib.MOM(prices, timeperiod=timeperiod)


def calculate_roc(prices: np.ndarray, timeperiod: int = 12) -> np.ndarray:
    """
    Calculate Rate of Change
    
    Args:
        prices: Array of closing prices
        timeperiod: ROC period (default 12)
    
    Returns:
        Array of ROC values (percentage)
    """
    return talib.ROC(prices, timeperiod=timeperiod)
