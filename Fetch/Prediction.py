from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import talib
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup

def predict_next_price(symbol):
    data = yf.Ticker(symbol).history(period="1y").dropna()  # ดึงข้อมูลย้อนหลัง 1 ปีและลบค่า NaN

    # ใช้เฉพาะราคาปิด (Close)
    data = data.reset_index()
    data['Day'] = np.arange(len(data))  # สร้างตัวแปร x = วัน
    X = data[['Day']]
    y = data['Close']

    # สร้างและฝึกโมเดล Linear Regression
    model = LinearRegression()
    model.fit(X, y)

    # ทำนายราคาวันถัดไป
    #plot จากราคาย้อนหลัง
    next_day = np.array([[len(data)]])
    predicted_price = model.predict(next_day)[0]

    # แสดงผล
    print(f"📈 {symbol} - Predicted next close price: ${predicted_price:.2f}")

    # วาดกราฟ
    plt.plot(data['Day'], y, label='Actual Price')
    plt.plot(data['Day'], model.predict(X), label='Trend Line')
    plt.scatter(next_day, predicted_price, color='red', label='Predicted Price')
    plt.title(f"{symbol} - Linear Regression Forecast")
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()

    return predicted_price
def predict_rsi(symbol):
    data = yf.Ticker(symbol).history(period="1y").dropna()  # ดึงข้อมูลย้อนหลัง 1 ปีและลบค่า NaN

    # คำนวณ RSI
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

    # แสดงผล RSI ล่าสุด
    latest_rsi = data['RSI'].iloc[-1]
    print(f"📈 {symbol} - Latest RSI: {latest_rsi:.2f}")
    # วาดกราฟ RSI
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['RSI'], label='RSI', color='purple')
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
#ตรวจหา Hammer Candlestick
def detect_hammer(symbol):
    data = yf.Ticker(symbol).history(period="1y").dropna()

    # คำนวณ Hammer Candlestick
    data['Hammer'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])

    # กรองแถวที่มี Hammer
    hammer_days = data[data['Hammer'] != 0]

    if not hammer_days.empty:
        print(f"📈 {symbol} - Hammer detected on the following dates:")
        for date in hammer_days.index:
            print(f"  - {date.date()}: {hammer_days.loc[date, 'Hammer']}")
    else:
        print(f"📈 {symbol} - No Hammer detected in the last year.")

    # สร้างกราฟ candlestick โดยใช้ mplfinance และไฮไลต์ Hammer
    add_plot = mpf.make_addplot(data['Hammer'].apply(lambda x: data['Low'].min() if x != 0 else None),
                                type='scatter', markersize=100, marker='v', color='red')
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

#ตรวจหา Doji Candlestick
def detect_doji(symbol):
    data = yf.Ticker(symbol).history(period="1y").dropna()

    # คำนวณ Doji Candlestick
    data['Doji'] = talib.CDLDOJI(data['Open'], data['High'], data['Low'], data['Close'])

    # กรองแถวที่มี Doji
    doji_days = data[data['Doji'] != 0]

    if not doji_days.empty:
        print(f"📈 {symbol} - Doji detected on the following dates:")
        for date in doji_days.index:
            print(f"  - {date.date()}: {doji_days.loc[date, 'Doji']}")
    else:
        print(f"📈 {symbol} - No Doji detected in the last year.")

    # สร้างกราฟ candlestick โดยใช้ mplfinance และไฮไลต์ Doji
    add_plot = mpf.make_addplot(data['Doji'].apply(lambda x: data['Low'].min() if x != 0 else None),
                                type='scatter', markersize=100, marker='v', color='blue')
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

#ตรวจหา EMA Cross
def detect_ema_cross(symbol):
    data = yf.Ticker(symbol).history(period="1y").dropna()

    # คำนวณ EMA
    data['EMA_12'] = talib.EMA(data['Close'], timeperiod=12)
    data['EMA_26'] = talib.EMA(data['Close'], timeperiod=26)

    # คำนวณสัญญาณ Cross
    data['Signal'] = np.where(data['EMA_12'] > data['EMA_26'], 1, 0)
    data['Cross'] = np.diff(np.insert(data['Signal'], 0, 0))  # คำนวณ cross ที่เปลี่ยนจาก 0 เป็น 1 หรือ 1 เป็น 0

    # กรองวันที่เกิด cross
    cross_days = data[data['Cross'] != 0]

    if not cross_days.empty:
        print(f"📈 {symbol} - EMA Cross detected on:")
        for date in cross_days.index:
            cross_type = "Bullish Cross (12 > 26)" if data.loc[date, 'Cross'] == 1 else "Bearish Cross (12 < 26)"
            print(f"  - {date.date()}: {cross_type}")
    else:
        print(f"📉 {symbol} - No EMA Cross in the last year.")

    # วาดกราฟ
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Close Price', alpha=0.3)
    plt.plot(data.index, data['EMA_12'], label='EMA 12', color='blue')
    plt.plot(data.index, data['EMA_26'], label='EMA 26', color='orange')

    # Plot จุด Cross
    bullish = data[data['Cross'] == 1]
    bearish = data[data['Cross'] == -1]
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

#ตรวจหา PEG Ratio

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
                print(float(cells[i+1].text))
                return float(cells[i+1].text)
    return None