import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
#คำนวณindicators
def calculate_MA(ticker):
    try:
        end_date = datetime.today()
        start_date = end_date - relativedelta(months=6)
        stock = yf.Ticker(ticker)
        sdat  = stock.history(start = start_date , end = end_date)
        sdat["MA5"] = sdat["Close"].rolling(window=5).mean()
        sdat["MA12"] = sdat["Close"].rolling(window=12).mean()
        sdat["MA26"] = sdat["Close"].rolling(window=26).mean()
        sdat["MA50"] = sdat["Close"].rolling(window=50).mean()
        sdat["MA200"] = sdat["Close"].rolling(window=200).mean()
        return sdat[ ["MA5","MA12","MA26","MA50","MA200"] ]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
#fetch ราคา
def fetch_rawdata(ticker):
    try:
        enddate = datetime.today()
        startdate = enddate-timedelta(days=30)
        stock = yf.Ticker(ticker)
        sdat = stock.history(start = startdate , end = enddate)
        return sdat
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None