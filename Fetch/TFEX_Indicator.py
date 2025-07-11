import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np

# ==================== Fetch Data ====================
# data = yf.download("AAPL", start="2020-01-01", end="2023-01-01")
def fetch_data(symbol, period="1y"):
    data.reset_index(inplace=True)
    data = yf.Ticker(symbol).history(period=period)
    data.reset_index(inplace=True)
    return data
def MA(symbol, period="1y"):
    data = fetch_data(symbol, period)
        # สร้าง Moving Average
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    # สร้างสัญญาณ Buy/Sell
    data['Signal'] = 0
    data['Signal'][20:] = np.where(data['MA20'][20:] > data['MA50'][20:], 1, 0)
    data['Position'] = data['Signal'].diff()

    # แสดงกราฟ
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['MA20'], label='MA 20')
    plt.plot(data['MA50'], label='MA 50')

    # Plot จุดซื้อ-ขาย
    plt.plot(data[data['Position'] == 1].index, 
            data['MA20'][data['Position'] == 1], 
            '^', markersize=10, color='g', label='Buy Signal')
    plt.plot(data[data['Position'] == -1].index, 
            data['MA20'][data['Position'] == -1], 
            'v', markersize=10, color='r', label='Sell Signal')

    plt.legend()
    plt.title('MA Crossover Strategy')
    plt.grid()
    plt.show()

    return data
def predict_rsi(symbol, period="1y"):
    data = fetch_data(symbol, period)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    data['RSI'] = rsi

    plt.figure(figsize=(14, 7))
    plt.plot(data['RSI'], label='RSI', color='blue')
    plt.axhline(70, linestyle='--', alpha=0.5, color='red')
    plt.axhline(30, linestyle='--', alpha=0.5, color='green')
    plt.title('Relative Strength Index (RSI)')
    plt.legend()
    plt.grid()
    plt.show()

    return data