# core/indicators/volume.py - Volume-based indicators

import numpy as np
import pandas as pd
import talib


def calculate_ad(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                 volume: np.ndarray) -> np.ndarray:
    """
    Calculate Accumulation/Distribution Line
    
    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of closing prices
        volume: Array of volumes
    
    Returns:
        Array of A/D values
    """
    return talib.AD(high, low, close, volume)


def calculate_obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    """
    Calculate On-Balance Volume
    
    Args:
        close: Array of closing prices
        volume: Array of volumes
    
    Returns:
        Array of OBV values
    """
    return talib.OBV(close, volume)
