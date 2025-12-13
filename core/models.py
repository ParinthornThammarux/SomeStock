# core/models.py - Pure Python data models, no UI dependencies

import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class StockData:
    """Pure data model for stock information"""
    symbol: str
    name: str
    price_history: Optional[pd.DataFrame] = None
    period: str = "1y"
    interval: str = "1d"
    
    def has_data(self) -> bool:
        """Check if price history exists and is not empty"""
        return self.price_history is not None and not self.price_history.empty
    
    def get_close_prices(self) -> Optional[pd.Series]:
        """Get closing prices - handles both 'close' and 'Close' column names"""
        if not self.has_data():
            return None
        
        df = self.price_history
        
        # Try lowercase first, then capitalized
        if 'close' in df.columns:
            return df['close'].dropna()
        elif 'Close' in df.columns:
            return df['Close'].dropna()
        
        return None
    
    def get_ohlcv(self) -> Optional[tuple]:
        """Get Open, High, Low, Close, Volume arrays"""
        if not self.has_data():
            return None
        
        df = self.price_history
        # Support both lowercase and capitalized column names
        required = [['open', 'Open'], ['high', 'High'], ['low', 'Low'], ['close', 'Close'], ['volume', 'Volume']]
        
        col_names = []
        for col_pair in required:
            col = None
            for name in col_pair:
                if name in df.columns:
                    col = name
                    break
            if col is None:
                return None
            col_names.append(col)
        
        return (
            df[col_names[0]].values,
            df[col_names[1]].values,
            df[col_names[2]].values,
            df[col_names[3]].values,
            df[col_names[4]].values
        )
