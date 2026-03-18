# core/utils.py - Utility functions for core module

import numpy as np
import pandas as pd


def get_close_column(df: pd.DataFrame) -> np.ndarray:
    """
    Get close prices from dataframe, handling both 'close' and 'Close' column names
    """
    if 'close' in df.columns:
        return df['close'].dropna().values
    elif 'Close' in df.columns:
        return df['Close'].dropna().values
    else:
        raise ValueError("DataFrame must have 'close' or 'Close' column")


def get_ohlcv_columns(df: pd.DataFrame) -> tuple:
    """
    Get Open, High, Low, Close, Volume columns handling both cases
    Returns: (open, high, low, close, volume) arrays
    """
    cols = {}
    
    # Map column names
    for col in df.columns:
        col_lower = col.lower()
        if col_lower == 'open':
            cols['open'] = col
        elif col_lower == 'high':
            cols['high'] = col
        elif col_lower == 'low':
            cols['low'] = col
        elif col_lower == 'close':
            cols['close'] = col
        elif col_lower == 'volume':
            cols['volume'] = col
    
    required = ['open', 'high', 'low', 'close', 'volume']
    if not all(k in cols for k in required):
        missing = [k for k in required if k not in cols]
        raise ValueError(f"Missing columns: {missing}")
    
    return (
        df[cols['open']].values,
        df[cols['high']].values,
        df[cols['low']].values,
        df[cols['close']].values,
        df[cols['volume']].values
    )
def format_money(value):
    if pd.isna(value):
        return "-"
    
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f} B"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f} M"
    else:
        return f"{value:,.0f}"
