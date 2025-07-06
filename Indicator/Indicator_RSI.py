import talib
import matplotlib.pyplot as plt
from Fetch_Indicator import fetch_data
def predict_rsi(symbol, period):
    data = fetch_data(symbol)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=period)

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