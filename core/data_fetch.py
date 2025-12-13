# core/data_fetch.py - Pure Python data fetching layer
# No UI dependencies, returns raw data

import pandas as pd
import yfinance as yf
from typing import Optional
from core.models import StockData
import time


def fetch_stock_data(symbol: str, period: str = "1y", interval: str = "1d") -> Optional[StockData]:
    """
    Fetch stock data from yfinance
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Interval (1m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        StockData object with price history, or None if failed
    """
    try:
        print(f"📡 Fetching {symbol} data (period={period}, interval={interval})")
        
        ticker = yf.Ticker(symbol)
        
        # Get price history
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            print(f"❌ No data available for {symbol}")
            return None
        
        # Normalize column names to lowercase
        hist.columns = [col.lower() for col in hist.columns]
        
        # Get company info
        try:
            info = ticker.info
            name = info.get('longName', symbol)
        except:
            name = symbol
        
        print(f"✅ Successfully fetched {len(hist)} bars for {symbol}")
        print(f"   Columns: {list(hist.columns)}")
        
        # Return StockData object
        return StockData(
            symbol=symbol,
            name=name,
            price_history=hist,
            period=period,
            interval=interval
        )
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


def fetch_multiple_stocks(symbols: list, period: str = "1y", interval: str = "1d") -> dict:
    """
    Fetch data for multiple stocks
    
    Returns:
        Dictionary of {symbol: StockData}
    """
    results = {}
    
    for symbol in symbols:
        data = fetch_stock_data(symbol, period=period, interval=interval)
        if data:
            results[symbol] = data
        time.sleep(0.5)  # Rate limiting
    
    return results
