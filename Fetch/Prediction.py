import os
import joblib
import math
import numpy as np
import yfinance as yf
import talib
import matplotlib.pyplot as plt
import mplfinance as mpf
import requests
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from bs4 import BeautifulSoup
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

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

# ==================== Model ====================
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
    df = fetch_data(symbol)
    close_prices = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(close_prices).flatten()

    split = int(len(scaled_prices) * 0.8)
    train_data = scaled_prices[:split]
    test_data = scaled_prices[split - window_size:]

    train_dataset = StockDataset(train_data, window_size)
    test_dataset = StockDataset(test_data, window_size)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

    model = StockPriceModel(window_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        model.train()
        for x_batch, y_batch in train_loader:
            pred = model(x_batch)
            loss = criterion(pred, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    model.eval()
    test_X = torch.tensor(test_dataset.X)
    preds = model(test_X).detach().numpy()
    y_true = test_dataset.y
    rmse = math.sqrt(mean_squared_error(y_true, preds))
    print(f"📉 Test RMSE: {rmse:.4f}")

    os.makedirs("Model", exist_ok=True)
    torch.save(model.state_dict(), f"Model/{symbol}_model.pt")
    np.save(f"Model/{symbol}_scaler.npy", scaler.data_max_)
    print(f"✅ Model & scaler saved for {symbol}")

    return model, scaler

# ==================== Load Model & Scaler ====================
def load_model(symbol, window_size=10):
    model = StockPriceModel(window_size)
    path = f"Model/{symbol}_model.pt"
    if os.path.exists(path):
        model.load_state_dict(torch.load(path))
        model.eval()
        print(f"📂 Loaded model from {path}")
        return model
    return None

def load_scaler(symbol):
    path = f"Model/{symbol}_scaler.npy"
    if os.path.exists(path):
        max_val = np.load(path)
        scaler = MinMaxScaler()
        scaler.fit(np.array([[0], [max_val.item()]]))
        return scaler
    return None
#test linear regression
def liner_regression(symbol, window_size=10, plot=True):
    df = fetch_data(symbol)
    close_prices = df["Close"].values.reshape(-1, 1)

    scaler = load_scaler(symbol)
    if scaler is None:
        scaler = MinMaxScaler()
        close_prices = scaler.fit_transform(close_prices).flatten()
    else:
        close_prices = scaler.transform(close_prices).flatten()

    x = np.arange(len(close_prices)).reshape(-1, 1)
    y = close_prices

    model = LinearRegression()
    model.fit(x, y)

    y_pred = model.predict(x)

    if plot:
        plt.figure(figsize=(12, 6))
        plt.plot(df['Date'], y, label='Actual Price')
        plt.plot(df['Date'], y_pred, label='Linear Regression', linestyle='--')
        plt.title(f"{symbol} - Linear Regression")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return model
# ==================== Price Prediction ====================
def predict_next_price(symbol, window_size=10, plot=True):
    df = fetch_data(symbol)
    close_prices = df["Close"].values.reshape(-1, 1)

    scaler = load_scaler(symbol)
    model = load_model(symbol, window_size)

    if model is None or scaler is None:
        model, scaler = train_model(symbol, window_size)

    scaled_prices = scaler.transform(close_prices).flatten()
    recent = scaled_prices[-window_size:]
    input_tensor = torch.tensor(recent, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        pred_scaled = model(input_tensor).item()
        predicted_price = scaler.inverse_transform([[pred_scaled]])[0][0]

    print(f"📈 {symbol} - Predicted next close price: ${predicted_price:.2f}")

    if plot:
        plt.plot(np.arange(len(close_prices)), close_prices, label="Actual Price")
        plt.scatter(len(close_prices), predicted_price, color="red", label="Predicted")
        plt.title(f"{symbol} - Forecasted Price")
        plt.xlabel("Days")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    return predicted_price

# ==================== RSI Prediction ====================
def predict_rsi(symbol, plot=True):
    data = fetch_data(symbol)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

    latest_rsi = data['RSI'].iloc[-1]
    print(f"📈 {symbol} - Latest RSI: {latest_rsi:.2f}")
    print(f"📊 {symbol} - RSI Interpretation: {'Overbought' if latest_rsi > 70 else 'Oversold' if latest_rsi < 30 else 'Neutral'}")

    if plot:
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

# ==================== EMA Cross Detection ====================
def detect_ema_cross(symbol, plot=True):
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
            cross_type = "Bullish" if cross_days.loc[date, 'Cross'] == 1 else "Bearish"
            print(f"  - {date.date()}: {cross_type}")
    else:
        print(f"📉 {symbol} - No EMA Cross in the last year.")

    if plot:
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

# ==================== MACD ====================
def plot_macd(symbol, plot=True):
    data = fetch_data(symbol)
    macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

    if plot:
        plt.figure(figsize=(12, 6))
        plt.plot(data['Date'], macd, label='MACD', color='blue')
        plt.plot(data['Date'], macdsignal, label='Signal Line', color='red')
        plt.bar(data['Date'], macdhist, label='Histogram', color='grey')
        plt.title(f"{symbol} - MACD")
        plt.xlabel("Date")
        plt.ylabel("MACD Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return macd, macdsignal, macdhist

# ==================== Doji Candlestick ====================
def detect_doji(symbol, plot=True):
    data = fetch_data(symbol)
    body = abs(data['Close'] - data['Open'])
    range_ = data['High'] - data['Low']
    doji = (body / range_) < 0.1  # body less than 10% of range

    dates = data['Date'][doji]

    if plot:
        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        addplots = [mpf.make_addplot(doji.astype(int), type='bar', panel=1, color='b', alpha=0.5)]
        mpf.plot(data.set_index('Date'), type='candle', style=s, addplot=addplots, title=f"{symbol} - Doji Candles")

    print(f"🕯️ {symbol} - Detected Doji on dates: {[str(d.date()) for d in dates.tolist()]}")
    return dates.tolist()

# ==================== Hammer Candlestick ====================
def detect_hammer(symbol, plot=True):
    data = fetch_data(symbol)

    body = abs(data['Close'] - data['Open'])
    lower_shadow = data['Open'].where(data['Close'] > data['Open'], data['Close']) - data['Low']
    upper_shadow = data['High'] - data['Close'].where(data['Close'] > data['Open'], data['Open'])

    hammer = (lower_shadow >= 2 * body) & (upper_shadow <= 0.1 * body)

    dates = data['Date'][hammer]

    if plot:
        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        addplots = [mpf.make_addplot(hammer.astype(int), type='bar', panel=1, color='m', alpha=0.5)]
        mpf.plot(data.set_index('Date'), type='candle', style=s, addplot=addplots, title=f"{symbol} - Hammer Candles")

    print(f"🔨 {symbol} - Detected Hammer on dates: {[str(d.date()) for d in dates.tolist()]}")
    return dates.tolist()


# ==================== Aroon Indicator ====================
def aroon_indicator(symbol, period=14, plot=True):
    data = fetch_data(symbol)
    aroon_up, aroon_down = talib.AROON(data['High'], data['Low'], timeperiod=period)

    if plot:
        plt.figure(figsize=(12, 6))
        plt.plot(data['Date'], aroon_up, label='Aroon Up', color='green')
        plt.plot(data['Date'], aroon_down, label='Aroon Down', color='red')
        plt.title(f"{symbol} - Aroon Indicator")
        plt.xlabel("Date")
        plt.ylabel("Aroon Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return aroon_up, aroon_down

# ==================== Momentum ====================
def momentum(symbol, period=10, plot=True):
    data = fetch_data(symbol)
    mom = talib.MOM(data['Close'], timeperiod=period)

    if plot:
        plt.figure(figsize=(12, 6))
        plt.plot(data['Date'], mom, label=f'Momentum ({period})', color='purple')
        plt.title(f"{symbol} - Momentum")
        plt.xlabel("Date")
        plt.ylabel("Momentum")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return mom

# ==================== PEG Ratio Scraper ====================
def fetch_peg_ratio(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)

    soup = BeautifulSoup(res.text, 'html.parser')
    peg_ratio = None
    for tr in soup.find_all('tr'):
        if 'PEG Ratio' in tr.text:
            peg_ratio = tr.find_all('td')[1].text.strip()
            break

    print(f"🔢 {symbol} - PEG Ratio: {peg_ratio}")
    return peg_ratio
