import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(ticker):
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        df["MA5"] = df["Close"].rolling(window=5).mean()
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["% Change"] = df["Close"].pct_change() * 100
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None