from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import talib

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
    plt.plot(data.index, data['RSI'], label='RSI', color='blue')
    plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    plt.title(f"{symbol} - RSI Analysis")

    return latest_rsi
    