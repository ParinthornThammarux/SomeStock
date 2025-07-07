import os
import joblib
from sklearn.linear_model import LinearRegression
import yfinance as yf
import numpy as np
import talib
import matplotlib.pyplot as plt
import mplfinance as mpf
import requests
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from bs4 import BeautifulSoup

# ==================== Dataset ====================
class StockDataset(Dataset):
    def __init__(self, prices, window_size=10):
        self.X, self.y = [], []
        for i in range(len(prices) - window_size):
            self.X.append(prices[i:i + window_size])
            self.y.append(prices[i + window_size])
        self.X = np.array(self.X, dtype=np.float32)
        self.y = np.array(self.y, dtype=np.float32).reshape(-1, 1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ==================== PyTorch Model ====================
class StockPriceModel(nn.Module):
    def __init__(self, input_size):
        super(StockPriceModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)

# ==================== Fetch Data ====================
def fetch_data(symbol, period="1y"):
    data = yf.Ticker(symbol).history(period=period)
    data.reset_index(inplace=True)
    return data

# ==================== Train Model ====================
def train_model(symbol, window_size=10, epochs=100):
    prices = fetch_data(symbol)
    dataset = StockDataset(prices, window_size)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = StockPriceModel(window_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        for x_batch, y_batch in loader:
            pred = model(x_batch)
            loss = criterion(pred, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    os.makedirs("Model", exist_ok=True)
    model_path = f"Model/{symbol}_model.pt"
    torch.save(model.state_dict(), model_path)
    print(f"✅ Model saved to {model_path}")
    return model

# ==================== Load Model ====================
def load_model(symbol, window_size=10):
    model = StockPriceModel(window_size)
    model_path = f"Model/{symbol}_model.pt"
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        model.eval()
        print(f"📂 Loaded model from {model_path}")
        return model
    return None

# ==================== Predict Next Price ====================
def predict_next_price(symbol, window_size=10):
    prices = fetch_data(symbol)
    model = load_model(symbol, window_size)
    if model is None:
        model = train_model(symbol, window_size)

    recent_prices = prices[-window_size:]
    input_tensor = torch.tensor(recent_prices, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        predicted = model(input_tensor).item()

    print(f"📈 {symbol} - Predicted next close price: ${predicted:.2f}")

    plt.plot(np.arange(len(prices)), prices, label='Actual Price')
    plt.scatter(len(prices), predicted, color='red', label='Predicted Price')
    plt.title(f"{symbol} - PyTorch Forecast")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

    return predicted

# ==================== RSI Prediction ====================
def predict_rsi(symbol):
    data = fetch_data(symbol)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

    latest_rsi = data['RSI'].iloc[-1]
    print(f"📈 {symbol} - Latest RSI: {latest_rsi:.2f}")

    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], data['RSI'], label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    plt.title(f"{symbol} - RSI (14)")
    plt.xlabel("Date")
    plt.ylabel("RSI")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return latest_rsi

# ==================== Hammer Candlestick Detection ====================
def detect_hammer(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)
    data['Hammer'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])

    hammer_days = data[data['Hammer'] != 0]

    if not hammer_days.empty:
        print(f"📈 {symbol} - Hammer detected on the following dates:")
        for date in hammer_days.index:
            print(f"  - {date.date()}: {hammer_days.loc[date, 'Hammer']}")
    else:
        print(f"📈 {symbol} - No Hammer detected in the last year.")

    add_plot = mpf.make_addplot(hammer_days['Low'], type='scatter', markersize=100, marker='v', color='red')
    mpf.plot(
        data,
        type='candle',
        style='yahoo',
        title=f'{symbol} - Candlestick with Hammer Pattern',
        ylabel='Price',
        volume=True,
        addplot=add_plot,
        figscale=1.2,
        figratio=(16, 9),
        tight_layout=True
    )

    return hammer_days

# ==================== Doji Candlestick Detection ====================
def detect_doji(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)
    data['Doji'] = talib.CDLDOJI(data['Open'], data['High'], data['Low'], data['Close'])

    doji_days = data[data['Doji'] != 0]

    if not doji_days.empty:
        print(f"📈 {symbol} - Doji detected on the following dates:")
        for date in doji_days.index:
            print(f"  - {date.date()}: {doji_days.loc[date, 'Doji']}")
    else:
        print(f"📈 {symbol} - No Doji detected in the last year.")

    add_plot = mpf.make_addplot(doji_days['Low'], type='scatter', markersize=100, marker='v', color='blue')
    mpf.plot(
        data,
        type='candle',
        style='yahoo',
        title=f'{symbol} - Candlestick with Doji Pattern',
        ylabel='Price',
        volume=True,
        addplot=add_plot,
        figscale=1.2,
        figratio=(16, 9),
        tight_layout=True
    )

    return doji_days

# ==================== EMA Cross Detection ====================
def detect_ema_cross(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    data['EMA_12'] = talib.EMA(data['Close'], timeperiod=12)
    data['EMA_26'] = talib.EMA(data['Close'], timeperiod=26)

    data['Signal'] = np.where(data['EMA_12'] > data['EMA_26'], 1, 0)
    data['Cross'] = data['Signal'].diff()

    cross_days = data[data['Cross'] != 0]

    if not cross_days.empty:
        print(f"📈 {symbol} - EMA Cross detected on:")
        for date in cross_days.index:
            cross_type = "Bullish Cross (12 > 26)" if cross_days.loc[date, 'Cross'] == 1 else "Bearish Cross (12 < 26)"
            print(f"  - {date.date()}: {cross_type}")
    else:
        print(f"📉 {symbol} - No EMA Cross in the last year.")

    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Close Price', alpha=0.3)
    plt.plot(data.index, data['EMA_12'], label='EMA 12', color='blue')
    plt.plot(data.index, data['EMA_26'], label='EMA 26', color='orange')

    bullish = cross_days[cross_days['Cross'] == 1]
    bearish = cross_days[cross_days['Cross'] == -1]
    plt.scatter(bullish.index, bullish['Close'], marker='^', color='green', label='Bullish Cross', s=100)
    plt.scatter(bearish.index, bearish['Close'], marker='v', color='red', label='Bearish Cross', s=100)

    plt.title(f"{symbol} - EMA 12/26 Crossover")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return cross_days

# ==================== PEG Ratio Prediction ====================
def predict_peg_ratio(symbol):
    url = f"https://finviz.com/quote.ashx?t={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", class_="snapshot-table2")
    if not table:
        print("❌ Table not found.")
        return None

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        for i in range(0, len(cells), 2):
            if cells[i].text == "PEG":
                peg = cells[i+1].text
                try:
                    peg_value = float(peg)
                    print(f"📊 {symbol} - PEG Ratio: {peg_value}")
                    return peg_value
                except ValueError:
                    print(f"⚠️ PEG Ratio not available or invalid: {peg}")
                    return None
    return None

# ==================== MACD Prediction ====================
def predict_MACD(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    macd, macd_signal, macd_hist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    data['MACD'] = macd
    data['Signal'] = macd_signal
    data['Hist'] = macd_hist

    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['MACD'], label='MACD', color='blue')
    plt.plot(data.index, data['Signal'], label='Signal Line', color='red')
    plt.bar(data.index, data['Hist'], label='MACD Histogram', color='grey', alpha=0.5)
    plt.title(f"{symbol} - MACD Indicator")
    plt.xlabel("Date")
    plt.ylabel("MACD Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    latest_macd = data['MACD'].iloc[-1]
    latest_signal = data['Signal'].iloc[-1]
    print(f"📈 {symbol} - Latest MACD: {latest_macd:.2f}, Signal Line: {latest_signal:.2f}")

    prev_macd = data['MACD'].iloc[-2]
    prev_signal = data['Signal'].iloc[-2]

    if prev_macd < prev_signal and latest_macd > latest_signal:
        print("📊 Bullish MACD crossover detected!")
    elif prev_macd > prev_signal and latest_macd < latest_signal:
        print("📉 Bearish MACD crossover detected!")
    else:
        print("ℹ️ No MACD crossover at the latest date.")

    return latest_macd, latest_signal

# ==================== Polynomial Regression Prediction ====================
def predict_price_binomial(symbol):
    data = fetch_data(symbol)
    y = data['Close'].values
    x = np.arange(len(y))

    coefficients = np.polyfit(x, y, 2)
    polynomial = np.poly1d(coefficients)

    next_x = np.array([len(y)])
    predicted_y = polynomial(next_x)
    print(f"📈 {symbol} - Predicted next close price using polynomial regression: ${predicted_y[0]:.2f}")

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label='Actual Price', color='blue')
    plt.plot(x, polynomial(x), label='Polynomial Fit', color='red')
    plt.scatter(next_x, predicted_y, color='green', s=100, label='Prediction')
    plt.title(f"{symbol} - Polynomial Regression (degree=2)")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()
    return predicted_y[0]

# ==================== Momentum Prediction ====================
def predict_momentum(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)
    data['Momentum'] = talib.MOM(data['Close'], timeperiod=10)

    latest_momentum = data['Momentum'].iloc[-1]
    print(f"📈 {symbol} - Latest Momentum: {latest_momentum:.2f}")

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Momentum'], label='Momentum', color='purple')
    plt.axhline(0, color='black', linestyle='--', label='Zero Line')
    plt.title(f"{symbol} - Momentum (10)")
    plt.xlabel("Date")
    plt.ylabel("Momentum")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return latest_momentum

def predict_aroon(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    data['Aroon_Up'], data['Aroon_Down'] = talib.AROON(data['High'], data['Low'], timeperiod=14)

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Aroon_Up'], label='Aroon Up', color='green')
    plt.plot(data.index, data['Aroon_Down'], label='Aroon Down', color='red')
    plt.axhline(70, color='blue', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='orange', linestyle='--', label='Oversold (30)')
    plt.title(f"{symbol} - Aroon Indicator")
    plt.xlabel("Date")
    plt.ylabel("Aroon Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    latest_aroon_up = data['Aroon_Up'].iloc[-1]
    latest_aroon_down = data['Aroon_Down'].iloc[-1]
    prev_aroon_up = data['Aroon_Up'].iloc[-2]
    prev_aroon_down = data['Aroon_Down'].iloc[-2]
    print(f"📈 {symbol} - Latest Aroon Up: {latest_aroon_up:.2f}, Aroon Down: {latest_aroon_down:.2f}")

    signal = None
    if prev_aroon_up < prev_aroon_down and latest_aroon_up > latest_aroon_down and latest_aroon_up > 50:
        signal = "BUY"
        print("✅ Buy Signal: Aroon Up crossed above Aroon Down and is strong (>50).")
    elif prev_aroon_down < prev_aroon_up and latest_aroon_down > latest_aroon_up and latest_aroon_down > 50:
        signal = "SELL"
        print("❌ Sell Signal: Aroon Down crossed above Aroon Up and is strong (>50).")
    else:
        signal = "HOLD"
        print("⚠️ No clear signal. Market may be sideways or indecisive.")
    return latest_aroon_up, latest_aroon_down,signal

def sushiroll(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    open = data['Open']
    close = data['Close']

    condi1  = close.shift(1) < open.shift(1)
    condi2 = close > open
    condi3 = open< close.shift(1)
    condi4 = close > open.shift(1)

    # mpf.plot(data, type='candle', addplot=ap, volume=True, title=f"{symbol} Sushi Roll Reverse Pattern")
    print(f"📈 {symbol} - Sushi Roll Reverse Pattern Detected: {condi1 & condi2 & condi3 & condi4.sum()} occurrences")
    return condi1 & condi2 & condi3 & condi4
# ==========================================
def VMA(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    dv = data['Close'] * (data['Volume'])
    data['VMA'] = dv.rolling(window=20).sum() / data['Volume'].rolling(window=20).sum()

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['VMA'], label='VMA', color='orange')
    plt.title(f"{symbol} - Volume Moving Average")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    latest_vma = data['VMA'].iloc[-1]
    print(f"📈 {symbol} - Latest VMA: {latest_vma:.2f}")

    return latest_vma
def calculate_Roc(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    data['ROC'] = talib.ROC(data['Close'], timeperiod=10)

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['ROC'], label='Rate of Change (ROC)', color='purple')
    plt.axhline(0, color='black', linestyle='--', label='Zero Line')
    plt.title(f"{symbol} - Rate of Change (ROC)")
    plt.xlabel("Date")
    plt.ylabel("ROC Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    latest_roc = data['ROC'].iloc[-1]
    print(f"📈 {symbol} - Latest ROC: {latest_roc:.2f}")

    return latest_roc
def calculate_WILLR(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    data['WILLR'] = talib.WILLR(data['High'], data['Low'], data['Close'], timeperiod=14)

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['WILLR'], label='Williams %R', color='orange')
    plt.axhline(-20, color='red', linestyle='--', label='Overbought (-20)')
    plt.axhline(-80, color='green', linestyle='--', label='Oversold (-80)')
    plt.title(f"{symbol} - Williams %R")
    plt.xlabel("Date")
    plt.ylabel("Williams %R Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    latest_willr = data['WILLR'].iloc[-1]
    print(f"📈 {symbol} - Latest Williams %R: {latest_willr:.2f}")
    if(latest_willr > -20):
        print("📈 Overbought condition detected.")
    elif(latest_willr < -80):
        print("📉 Oversold condition detected.")
    return latest_willr