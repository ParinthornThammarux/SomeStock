def test_stockdx_connection():
    # Try different formats for the ticker symbols:

    # For US stocks (TSLA):
    ticker_formats = [
        "TSLA",           # Basic format
        "TSLA.US",        # With country suffix
        "NASDAQ:TSLA",    # With exchange prefix
    ]

    # For Thai stocks (CPALL):
    thai_formats = [
        "CPALL.BK",       # What we used before (worked in standalone)
        "CPALL",          # Without suffix
        "SET:CPALL",      # With exchange prefix
        "CPALL.BKK",      # Alternative suffix
    ]
    
    """Test stockdx library with various ticker formats"""
    from stockdex import Ticker
    
    test_symbols = [
        "TSLA", "AAPL", "MSFT",           # US stocks
        "CPALL.BK", "CPALL", "PTT.BK"     # Thai stocks
    ]
    
    for symbol in test_symbols:
        try:
            print(f"Testing {symbol}...")
            ticker = Ticker(ticker=symbol)
            
            # Try to get just basic info first
            data = ticker.yahoo_api_price(range='1d', dataGranularity='1h')
            
            if data is not None and not data.empty:
                print(f"✅ {symbol} - Success! Got {len(data)} data points")
                print(f"   Sample: {data['close'].iloc[-1]:.2f}")
            else:
                print(f"⚠️  {symbol} - No data returned")
                
        except Exception as e:
            print(f"❌ {symbol} - Error: {str(e)}")
    
    print("\nTesting complete!")

# Run this first to see which symbols work
test_stockdx_connection()