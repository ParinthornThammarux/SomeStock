import talib
import matplotlib.pyplot as plt
from Fetch_Indicator import fetch_data
def EMACross_Shortterm(symbol):
    data = fetch_data(symbol)
    data['EMA5'] = talib.EMA(data['Close'], timeperiod=5)
    data['EMA8'] = talib.EMA(data['Close'], timeperiod=8)
    data['EMA13'] = talib.EMA(data['Close'], timeperiod=13)

    latest_ema5 = data['EMA5'].iloc[-1]
    latest_ema8 = data['EMA8'].iloc[-1]
    latest_ema13 = data['EMA13'].iloc[-1]

    print(f"📈 {symbol} - Latest EMA5: {latest_ema5:.2f}, EMA8: {latest_ema8:.2f}, EMA13: {latest_ema13:.2f}")
    plt.figure(figsize=(10, 5))
    plt.plot(data['Date'], data['EMA5'], label='EMA5', color='blue')
    plt.plot(data['Date'], data['EMA8'], label='EMA8', color='orange')
    plt.plot(data['Date'], data['EMA13'], label='EMA13', color='green')
    plt.xlabel("Date")
    plt.ylabel("EMA")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.title(f"{symbol} - EMA Cross (5, 8, 13)")
      
    return latest_ema5, latest_ema8, latest_ema13
