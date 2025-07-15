# utils/stockdx_layer.py - Clean and Organized Version

import dearpygui.dearpygui as dpg
import time
import random
import requests
import pandas as pd
from utils import constants

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Rate limiting configuration
RATE_LIMIT_DELAY = 3.0  # Minimum seconds between requests
RANDOM_DELAY_MIN = 0.5  # Random delay range (min)
RANDOM_DELAY_MAX = 1.5  # Random delay range (max)
MAX_RETRIES = 3         # Maximum retry attempts
REQUEST_TIMEOUT = 30    # Request timeout in seconds

# Global state
last_request_time = 0
request_count = 0

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def fetch_data_from_stockdx(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """
    Main function to fetch stock data with multiple fallback methods.
    Updates both chart and cache with comprehensive data.
    """
    print("=" * 80)
    print(f"🔍 FETCHING DATA FOR: {symbol}")
    print("=" * 80)
    
    # Apply rate limiting
    _apply_rate_limiting()
    
    # Try multiple data sources in order of preference
    data_sources = [
        ("Yahoo Finance v8 API", _fetch_yahoo_v8_api),
        ("yfinance Library", _fetch_yfinance),
        ("Enhanced Stockdx", _fetch_enhanced_stockdx),
    ]
    
    for source_name, fetch_function in data_sources:
        try:
            print(f"🔄 Trying {source_name}...")
            data = fetch_function(symbol)
            
            if _validate_data(data):
                print(f"✅ Success with {source_name}")
                _process_successful_fetch(symbol, data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
                return
            else:
                print(f"❌ {source_name} returned invalid data")
                
        except Exception as e:
            print(f"❌ {source_name} failed: {e}")
            continue
    
    print(f"❌ All data sources failed for {symbol}")

# =============================================================================
# DATA SOURCE IMPLEMENTATIONS
# =============================================================================

def _fetch_yahoo_v8_api(symbol):
    """Fetch data directly from Yahoo Finance v8 API"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
        "Origin": "https://finance.yahoo.com",
    }
    
    params = {
        "period1": int(time.time()) - 86400,  # 24 hours ago
        "period2": int(time.time()),          # Now
        "interval": "5m",
        "includePrePost": "true",
        "events": "div%2Csplit",
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    
    if response.status_code == 200:
        data = response.json()
        chart = data['chart']['result'][0]
        quotes = chart['indicators']['quote'][0]
        
        return {
            'timestamps': chart['timestamp'],
            'open': quotes.get('open', []),
            'high': quotes.get('high', []),
            'low': quotes.get('low', []),
            'close': quotes.get('close', []),
            'volume': quotes.get('volume', []),
        }
    else:
        raise Exception(f"HTTP {response.status_code}: {response.reason}")

def _fetch_yfinance(symbol):
    """Fetch data using yfinance library (requires: pip install yfinance)"""
    try:
        import yfinance as yf
        
        # Create session with proper headers
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="1d", interval="5m")
        
        if not hist.empty:
            return {
                'close': hist['Close'].tolist(),
                'open': hist['Open'].tolist(),
                'high': hist['High'].tolist(),
                'low': hist['Low'].tolist(),
                'volume': hist['Volume'].tolist(),
                'timestamps': [int(ts.timestamp()) for ts in hist.index],
            }
        else:
            raise Exception("yfinance returned empty dataset")
            
    except ImportError:
        raise Exception("yfinance not installed. Install with: pip install yfinance")

def _fetch_enhanced_stockdx(symbol):
    """Fetch data using enhanced stockdx with improved error handling"""
    from stockdex import Ticker
    
    # Temporarily patch the get_response method for better reliability
    original_method = Ticker.get_response
    Ticker.get_response = _improved_get_response
    
    try:
        ticker = Ticker(ticker=symbol)
        df = ticker.yahoo_api_price(range='1d', dataGranularity='5m')
        
        if df is not None and not df.empty:
            return {
                'close': df['close'].tolist(),
                'open': df['open'].tolist() if 'open' in df.columns else [],
                'high': df['high'].tolist() if 'high' in df.columns else [],
                'low': df['low'].tolist() if 'low' in df.columns else [],
                'volume': df['volume'].tolist() if 'volume' in df.columns else [],
            }
        else:
            raise Exception("Stockdx returned empty dataset")
            
    finally:
        # Always restore original method
        Ticker.get_response = original_method

# =============================================================================
# CHART AND CACHE PROCESSING
# =============================================================================

def _process_successful_fetch(symbol, data, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Process successfully fetched data - update chart and cache"""
    try:
        # 1. Update chart immediately
        _update_chart_with_data(data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
        
        # 2. Convert to DataFrame for caching
        df = _convert_to_dataframe(data)
        
        # 3. Cache comprehensive data (includes fundamentals)
        _cache_comprehensive_data(symbol, df)
        
        # 4. Update request tracking
        global last_request_time
        last_request_time = time.time()
        
        print(f"✅ Successfully processed all data for {symbol}")
        
    except Exception as e:
        print(f"❌ Error processing data for {symbol}: {e}")

def _update_chart_with_data(data, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Update DPG chart with fetched data"""
    try:
        # Extract and clean close prices
        close_prices = [p for p in data['close'] if p is not None]
        if not close_prices:
            raise Exception("No valid close prices found")
            
        x_data = list(range(len(close_prices)))
        y_data = close_prices
        
        # Validate chart tags exist
        required_tags = [
            ("Line", line_tag),
            ("X-axis", x_axis_tag), 
            ("Y-axis", y_axis_tag),
            ("Plot", plot_tag)
        ]
        
        for tag_name, tag_value in required_tags:
            if not tag_value or not dpg.does_item_exist(tag_value):
                raise Exception(f"{tag_name} tag invalid or missing")
        
        # Update chart data
        print("🔄 Updating chart...")
        dpg.set_value(line_tag, [x_data, y_data])
        
        # Update axis limits
        if y_data:
            margin = 0.005  # 0.5% margin
            min_price = min(y_data) * (1 - margin)
            max_price = max(y_data) * (1 + margin)
            
            dpg.set_axis_limits(x_axis_tag, 0, len(x_data))
            dpg.set_axis_limits(y_axis_tag, min_price, max_price)
        
        print(f"✅ Chart updated - {len(y_data)} points, range: ${min(y_data):.2f} - ${max(y_data):.2f}")
        
    except Exception as e:
        print(f"❌ Error updating chart: {e}")

def _convert_to_dataframe(data):
    """Convert API data to pandas DataFrame"""
    try:
        df_data = {}
        
        # Ensure all arrays are the same length
        max_length = max(len(data.get(key, [])) for key in ['open', 'high', 'low', 'close', 'volume'])
        
        for key in ['open', 'high', 'low', 'close', 'volume']:
            values = data.get(key, [])
            # Pad with None if shorter
            while len(values) < max_length:
                values.append(None)
            df_data[key] = values[:max_length]  # Trim if longer
        
        df = pd.DataFrame(df_data)
        
        # Handle timestamps if available
        if 'timestamps' in data and data['timestamps']:
            df.index = pd.to_datetime(data['timestamps'], unit='s')
        
        return df
        
    except Exception as e:
        print(f"❌ Error converting to DataFrame: {e}")
        # Return simple DataFrame with just close prices
        return pd.DataFrame({'close': data.get('close', [])})

def _cache_comprehensive_data(symbol, price_df):
    """Cache all data including fundamentals"""
    try:
        from components.stock_data_manager import stock_data_cache, StockData
        
        # Get or create stock data object
        if symbol in stock_data_cache:
            stock_data = stock_data_cache[symbol]
        else:
            stock_data = StockData(symbol=symbol, company_name=f"{symbol} Corp.")
        
        # Update price data
        stock_data.last_updated = time.time()
        stock_data.price_history = price_df
        
        if not price_df.empty and 'close' in price_df.columns:
            stock_data.current_price = float(price_df['close'].dropna().iloc[-1])
            
            # Calculate change if we have enough data
            if len(price_df) > 1:
                prev_prices = price_df['close'].dropna()
                if len(prev_prices) > 1:
                    stock_data.previous_price = float(prev_prices.iloc[-2])
                    stock_data.change = stock_data.current_price - stock_data.previous_price
                    stock_data.change_percent = (stock_data.change / stock_data.previous_price) * 100
        
        # Extract volume if available
        if 'volume' in price_df.columns:
            volume_series = price_df['volume'].dropna()
            if not volume_series.empty:
                stock_data.volume = int(volume_series.iloc[-1])
        
        # Fetch fundamental data (safely)
        _fetch_fundamental_data(symbol, stock_data)
        
        # Update cache and UI
        stock_data_cache[symbol] = stock_data
        _update_stock_tag_cache(symbol, stock_data)
        _add_to_portfolio_table(symbol)
        
        print(f"✅ Comprehensive data cached for {symbol}")
        
    except Exception as e:
        print(f"❌ Error caching data: {e}")

def _fetch_fundamental_data(symbol, stock_data):
    """Safely fetch fundamental data"""
    try:
        from stockdex import Ticker
        
        print(f"📊 Fetching fundamentals for {symbol}...")
        
        ticker = Ticker(ticker=symbol)
        
        # Get income statement
        try:
            income_statement = ticker.yahoo_api_income_statement(frequency='quarterly', format='raw')
            if income_statement is not None and not income_statement.empty:
                _extract_revenue(income_statement, stock_data)
                _extract_net_income(income_statement, stock_data)
        except Exception as e:
            print(f"⚠️ Income statement fetch failed: {e}")
        
        # Get cash flow
        try:
            cash_flow = ticker.yahoo_api_cash_flow(frequency='quarterly', format='raw')
            if cash_flow is not None and not cash_flow.empty:
                _extract_cash_flow(cash_flow, stock_data)
        except Exception as e:
            print(f"⚠️ Cash flow fetch failed: {e}")
        
        print(f"✅ Fundamental data processed for {symbol}")
        
    except Exception as e:
        print(f"⚠️ Fundamental data fetch failed: {e}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _apply_rate_limiting():
    """Apply rate limiting to prevent API abuse"""
    global last_request_time
    
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < RATE_LIMIT_DELAY:
        sleep_time = RATE_LIMIT_DELAY - time_since_last
        print(f"⏱️ Rate limiting: waiting {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    
    # Add random delay to avoid pattern detection
    random_delay = random.uniform(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)
    print(f"⏱️ Random delay: {random_delay:.2f} seconds...")
    time.sleep(random_delay)

def _validate_data(data):
    """Validate that fetched data is usable"""
    if not data:
        return False
    
    close_prices = data.get('close', [])
    if not close_prices:
        return False
    
    # Check for valid prices (not all None)
    valid_prices = [p for p in close_prices if p is not None and p > 0]
    return len(valid_prices) > 0

def _improved_get_response(self, url):
    """Improved get_response method for stockdx with better error handling"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
        "Connection": "keep-alive",
        "DNT": "1",
    }
    
    session = requests.Session()
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                wait_time = (2 ** attempt) * 10  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
            else:
                print(f"HTTP {response.status_code}: {response.reason}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5)
                    
        except requests.exceptions.RequestException as e:
            print(f"Request error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
    
    raise Exception(f"Failed to fetch {url} after {MAX_RETRIES} attempts")

def _extract_revenue(income_statement, stock_data):
    """Extract revenue from income statement"""
    try:
        if 'quarterlyTotalRevenue' in income_statement.columns:
            latest_idx = income_statement.index[-1]
            rev_value = income_statement.loc[latest_idx, 'quarterlyTotalRevenue']
            
            if pd.notna(rev_value) and rev_value != 0:
                rev_value = float(rev_value)
                if rev_value >= 1_000_000:
                    stock_data.revenue = f"${rev_value/1_000_000:.1f}M"
                else:
                    stock_data.revenue = f"${rev_value/1_000:.1f}K"
    except Exception as e:
        print(f"⚠️ Revenue extraction failed: {e}")

def _extract_net_income(income_statement, stock_data):
    """Extract net income from income statement"""
    try:
        for col in ['quarterlyNetIncome', 'quarterlyNetIncomeCommonStockholders']:
            if col in income_statement.columns:
                latest_idx = income_statement.index[-1]
                ni_value = income_statement.loc[latest_idx, col]
                
                if pd.notna(ni_value) and ni_value != 0:
                    ni_value = float(ni_value)
                    if abs(ni_value) >= 1_000_000:
                        stock_data.net_income = f"${ni_value/1_000_000:.1f}M"
                    else:
                        stock_data.net_income = f"${ni_value/1_000:.1f}K"
                break
    except Exception as e:
        print(f"⚠️ Net income extraction failed: {e}")

def _extract_cash_flow(cash_flow, stock_data):
    """Extract cash flow data"""
    try:
        for col in ['quarterlyOperatingCashFlow', 'quarterlyFreeCashFlow']:
            if col in cash_flow.columns:
                latest_idx = cash_flow.index[-1]
                cf_value = cash_flow.loc[latest_idx, col]
                
                if pd.notna(cf_value) and cf_value != 0:
                    cf_value = float(cf_value)
                    if abs(cf_value) >= 1_000_000:
                        stock_data.cash_flow = f"${cf_value/1_000_000:.1f}M"
                    else:
                        stock_data.cash_flow = f"${cf_value/1_000:.1f}K"
                break
    except Exception as e:
        print(f"⚠️ Cash flow extraction failed: {e}")

def _update_stock_tag_cache(symbol, stock_data):
    """Update stock tag with fresh cache data"""
    try:
        from components.stock_data_manager import find_tag_by_name
        
        tag = find_tag_by_name(symbol)
        if tag:
            tag.stock_data = stock_data
            tag.update_cache_indicator()
    except Exception as e:
        print(f"⚠️ Could not update stock tag cache: {e}")

def _add_to_portfolio_table(symbol):
    """Add stock to portfolio table"""
    try:
        from components.graph_dpg import add_stock_to_portfolio_table
        add_stock_to_portfolio_table(symbol)
    except Exception as e:
        print(f"⚠️ Could not add to portfolio table: {e}")

# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Keep original function names for backward compatibility
def update_chart(df, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Legacy function - converts DataFrame to data dict and updates chart"""
    try:
        data = {
            'close': df['close'].tolist(),
            'open': df['open'].tolist() if 'open' in df.columns else [],
            'high': df['high'].tolist() if 'high' in df.columns else [],
            'low': df['low'].tolist() if 'low' in df.columns else [],
            'volume': df['volume'].tolist() if 'volume' in df.columns else [],
        }
        _update_chart_with_data(data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
    except Exception as e:
        print(f"❌ Legacy chart update failed: {e}")

def cache_comprehensive_data(symbol, price_df, ticker):
    """Legacy function - caches data without ticker dependency"""
    _cache_comprehensive_data(symbol, price_df)

# =============================================================================
# REMOVED DUPLICATE FUNCTIONS
# =============================================================================

# The following functions were removed as they were duplicates:
# - fetch_with_improved_stockdx() -> merged into _fetch_enhanced_stockdx()
# - enhanced_fetch_data_from_stockdx() -> functionality moved to main function
# - fetch_with_yfinance() -> renamed to _fetch_yfinance()
# - update_chart_with_data() -> renamed to _update_chart_with_data()
# - update_dpg_chart() -> functionality merged into _update_chart_with_data()

# =============================================================================
# CLEAN ARCHITECTURE
# =============================================================================

# Now we have ONE clear path:
# 1. fetch_data_from_stockdx() - Main entry point
# 2. _fetch_yahoo_v8_api() - Direct Yahoo API
# 3. _fetch_yfinance() - yfinance library  
# 4. _fetch_enhanced_stockdx() - Enhanced stockdx with better error handling
# 5. All processing happens in _process_successful_fetch()