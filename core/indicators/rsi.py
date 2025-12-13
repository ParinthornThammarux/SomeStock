# core/indicators/rsi.py - Relative Strength Index calculation

import numpy as np
import pandas as pd
import talib


def calculate_rsi(prices: np.ndarray, timeperiod: int = 14) -> np.ndarray:
    """
    Calculate Relative Strength Index using TA-Lib
    
    Args:
        prices: Array of closing prices
        timeperiod: RSI period (default 14)
    
    Returns:
        Array of RSI values (0-100)
    """
    return talib.RSI(prices, timeperiod=timeperiod)


def detect_rsi_signals(rsi_values: np.ndarray, oversold: int = 30, overbought: int = 70):
    """
    Detect overbought/oversold conditions
    
    Args:
        rsi_values: Array of RSI values
        oversold: Oversold threshold (default 30)
        overbought: Overbought threshold (default 70)
    
    Returns:
        List of (index, signal_type) tuples
    """
    signals = []
    
    for i, rsi in enumerate(rsi_values):
        if not np.isnan(rsi):
            if rsi < oversold:
                signals.append((i, 'oversold'))
            elif rsi > overbought:
                signals.append((i, 'overbought'))
    
    return signals
