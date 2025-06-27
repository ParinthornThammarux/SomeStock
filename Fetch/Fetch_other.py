import yfinance as yf

def fetch_other_asset(symbol):

    try:
        asset_data = yf.Ticker(symbol)
        hist = asset_data.history(period="max")
        return hist
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None