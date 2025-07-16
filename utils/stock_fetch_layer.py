# utils/stockdx_layer.py - Clean and Organized Version

import dearpygui.dearpygui as dpg
import time
import random
import requests
import pandas as pd
from utils import constants
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Rate limiting configuration
RATE_LIMIT_DELAY = 8.0  # Increased from 3.0 to 8.0 seconds
RANDOM_DELAY_MIN = 2.0  # Increased from 0.5 to 2.0
RANDOM_DELAY_MAX = 4.0  # Increased from 1.5 to 4.0
MAX_RETRIES = 5         # Increased from 3 to 5
REQUEST_TIMEOUT = 45    # Increased from 30 to 45 seconds

# Global state
last_request_time = 0
request_count = 0
active_fetches = {}  # {symbol: {'stop_flag': threading.Event(), 'result': None}}


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def fetch_stock_data(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """
    Try all sources simultaneously, stop all others when first one succeeds
    """
    print("=" * 80)
    print(f"🚀 OPTIMIZED FETCHING FOR: {symbol}")
    print("=" * 80)
    
    # Create stop flag for this symbol
    stop_flag = threading.Event()
    fetch_info = {
        'stop_flag': stop_flag,
        'result': None,
        'successful_source': None
    }
    active_fetches[symbol] = fetch_info
    
    # Define fetch sources
    sources = [
        ("Yahoo Finance v8", _fetch_yahoo_v8_with_stop),
        ("yfinance Library", _fetch_yfinance_with_stop),
        ("Enhanced Stockdx", _fetch_enhanced_stockdx_with_stop),
    ]
    
    # Try Yahoo first (preferred source)
    yahoo_result = _quick_yahoo_check(symbol, stop_flag)
    if yahoo_result and yahoo_result != "RATE_LIMITED":
        print("✅ Yahoo succeeded immediately")
        _process_result(symbol, yahoo_result, "Yahoo Finance v8", line_tag, x_axis_tag, y_axis_tag, plot_tag)
        return
    
    print("🔄 Yahoo rate limited or failed, trying all sources in parallel...")
    
    # Run all sources in parallel threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all fetch tasks
        future_to_source = {}
        for source_name, fetch_function in sources:
            future = executor.submit(fetch_function, symbol, stop_flag)
            future_to_source[future] = source_name
        
        # Process results as they come in
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            
            # Check if we should stop (another source already succeeded)
            if stop_flag.is_set():
                print(f"🛑 Stopping {source_name} - another source succeeded")
                break
                
            try:
                result = future.result()
                
                if result and result != "RATE_LIMITED" and _validate_data(result):
                    print(f"✅ First success: {source_name}")
                    
                    # Signal all other threads to stop
                    stop_flag.set()
                    
                    # Process the successful result
                    _process_result(symbol, result, source_name, line_tag, x_axis_tag, y_axis_tag, plot_tag)
                    
                    # Clean up
                    if symbol in active_fetches:
                        del active_fetches[symbol]
                    return
                    
                else:
                    print(f"❌ {source_name} failed or rate limited")
                    
            except Exception as e:
                print(f"❌ {source_name} error: {e}")
    
    # If we get here, all sources failed
    print(f"❌ All sources failed for {symbol}")
    if symbol in active_fetches:
        del active_fetches[symbol]

# =============================================================================
# DATA SOURCE IMPLEMENTATIONS
# =============================================================================

# Replace _fetch_yahoo_v8_api function in stockdx_layer.py

def _quick_yahoo_check(symbol, stop_flag):
    """Quick Yahoo check with immediate rate limit detection"""
    if stop_flag.is_set():
        return None
        
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    params = {
        "period1": int(time.time()) - 86400,
        "period2": int(time.time()),
        "interval": "5m",
        "includePrePost": "false",
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=8)
        
        if response.status_code == 429:
            return "RATE_LIMITED"
        elif response.status_code == 200:
            return _parse_yahoo_response(response.json())
        else:
            return None
            
    except Exception:
        return None
# Enhanced stockdx_layer.py - Integrated Fundamental Data Fetching

def _fetch_yahoo_v8_with_stop(symbol, stop_flag):
    """Yahoo v8 fetch with integrated fundamental data"""
    
    if stop_flag.is_set():
        return None
    
    # Delay before starting
    time.sleep(2)
    
    if stop_flag.is_set():
        return None
    
    endpoints = [
        "https://query2.finance.yahoo.com/v8/finance/chart/",
        "https://query1.finance.yahoo.com/v8/finance/chart/",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    # Start with price data
    price_data = None
    for endpoint in endpoints:
        if stop_flag.is_set():
            return None
            
        for attempt in range(2):
            if stop_flag.is_set():
                return None
                
            try:
                # Fetch price data
                url = f"{endpoint}{symbol}"
                params = {
                    "period1": int(time.time()) - 86400,
                    "period2": int(time.time()),
                    "interval": "5m",
                    "includePrePost": "false",
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    price_data = _parse_yahoo_response(response.json())
                    break
                elif response.status_code == 429:
                    for i in range(10):
                        if stop_flag.is_set():
                            return None
                        time.sleep(1)
                else:
                    break
                    
            except Exception as e:
                if stop_flag.is_set():
                    return None
                continue
        
        if price_data:
            break
    
    if not price_data or stop_flag.is_set():
        return None
    
    # Try to fetch fundamental data using same Yahoo endpoints
    fundamental_data = _fetch_yahoo_fundamentals(symbol, headers, stop_flag)
    
    # Merge fundamental data into price data
    if fundamental_data:
        price_data.update(fundamental_data)
    
    return price_data

def _fetch_yahoo_fundamentals(symbol, headers, stop_flag):
    """Fetch fundamental data from Yahoo Finance"""
    
    if stop_flag.is_set():
        return {}
    
    fundamental_data = {}
    
    try:
        # Try multiple Yahoo endpoints for fundamental data
        endpoints = [
            f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
        ]
        
        for endpoint in endpoints:
            if stop_flag.is_set():
                break
                
            try:
                # Get key statistics and financial data
                params = {
                    "modules": "financialData,defaultKeyStatistics,incomeStatementHistory,cashflowStatementHistory"
                }
                
                response = requests.get(endpoint, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'quoteSummary' in data and data['quoteSummary']['result']:
                        result = data['quoteSummary']['result'][0]
                        
                        # Extract financial data
                        if 'financialData' in result:
                            fd = result['financialData']
                            fundamental_data['revenue'] = _format_yahoo_value(fd.get('totalRevenue'))
                            fundamental_data['market_cap'] = _format_yahoo_value(fd.get('marketCap'))
                        
                        # Extract from income statement
                        if 'incomeStatementHistory' in result:
                            income_data = result['incomeStatementHistory'].get('incomeStatementHistory', [])
                            if income_data:
                                latest = income_data[0]
                                fundamental_data['net_income'] = _format_yahoo_value(latest.get('netIncome'))
                        
                        # Extract from cash flow
                        if 'cashflowStatementHistory' in result:
                            cf_data = result['cashflowStatementHistory'].get('cashflowStatementHistory', [])
                            if cf_data:
                                latest = cf_data[0]
                                fundamental_data['cash_flow'] = _format_yahoo_value(latest.get('totalCashFromOperatingActivities'))
                        
                        print(f"✅ Yahoo fundamental data fetched for {symbol}")
                        break
                        
                elif response.status_code == 429:
                    print(f"⚠️ Yahoo fundamentals rate limited for {symbol}")
                    break
                    
            except Exception as e:
                print(f"⚠️ Yahoo fundamentals error: {e}")
                continue
    
    except Exception as e:
        print(f"⚠️ Yahoo fundamentals fetch failed: {e}")
    
    return fundamental_data

def _fetch_yfinance_with_stop(symbol, stop_flag):
    """yfinance fetch with integrated fundamental data"""
    
    if stop_flag.is_set():
        return None
    
    try:
        import yfinance as yf
        
        if stop_flag.is_set():
            return None
            
        ticker = yf.Ticker(symbol)
        
        # Fetch price data
        hist = ticker.history(period="1d", interval="5m")
        
        if stop_flag.is_set():
            return None
        
        if hist.empty:
            return None
        
        # Parse price data
        volume_data = hist['Volume'].fillna(0) if 'Volume' in hist.columns else []
        clean_volume = [max(0, int(vol)) for vol in volume_data]
        
        price_data = {
            'close': hist['Close'].tolist(),
            'open': hist['Open'].tolist(),
            'high': hist['High'].tolist(),
            'low': hist['Low'].tolist(),
            'volume': clean_volume,
            'timestamps': [int(ts.timestamp()) for ts in hist.index],
        }
        
        if stop_flag.is_set():
            return price_data  # Return what we have
        
        # Try to fetch fundamental data
        fundamental_data = _fetch_yfinance_fundamentals(ticker, symbol, stop_flag)
        
        # Merge fundamental data
        if fundamental_data:
            price_data.update(fundamental_data)
        
        return price_data
        
    except Exception as e:
        print(f"yfinance error: {e}")
        return None

def _fetch_yfinance_fundamentals(ticker, symbol, stop_flag):
    """Fetch fundamental data using yfinance"""
    
    if stop_flag.is_set():
        return {}
    
    fundamental_data = {}
    
    try:
        # Get basic info (cached by yfinance)
        if stop_flag.is_set():
            return {}
            
        info = ticker.info
        
        if info:
            # Extract key metrics
            if 'totalRevenue' in info:
                fundamental_data['revenue'] = _format_value(info['totalRevenue'])
            
            if 'marketCap' in info:
                fundamental_data['market_cap'] = _format_value(info['marketCap'])
            
            if 'netIncomeToCommon' in info:
                fundamental_data['net_income'] = _format_value(info['netIncomeToCommon'])
        
        if stop_flag.is_set():
            return fundamental_data
        
        # Try to get financials (may trigger additional API calls)
        try:
            financials = ticker.financials
            if not financials.empty and 'Net Income' in financials.index:
                latest_income = financials.loc['Net Income'].iloc[0]
                if pd.notna(latest_income):
                    fundamental_data['net_income'] = _format_value(latest_income)
        except Exception:
            pass  # Skip if financials fail
        
        if stop_flag.is_set():
            return fundamental_data
        
        # Try cash flow
        try:
            cashflow = ticker.cashflow
            if not cashflow.empty and 'Operating Cash Flow' in cashflow.index:
                latest_cf = cashflow.loc['Operating Cash Flow'].iloc[0]
                if pd.notna(latest_cf):
                    fundamental_data['cash_flow'] = _format_value(latest_cf)
        except Exception:
            pass  # Skip if cash flow fails
        
        print(f"✅ yfinance fundamental data fetched for {symbol}")
        
    except Exception as e:
        print(f"⚠️ yfinance fundamentals error: {e}")
    
    return fundamental_data

def _fetch_enhanced_stockdx_with_stop(symbol, stop_flag):
    """Enhanced stockdx fetch with integrated fundamental data"""
    
    if stop_flag.is_set():
        return None
    
    try:
        from stockdex import Ticker  # Note: using stockdx as specified
        
        if stop_flag.is_set():
            return None
            
        ticker = Ticker(ticker=symbol)
        
        # Fetch price data
        df = ticker.yahoo_api_price(range='1d', dataGranularity='5m')
        
        if stop_flag.is_set():
            return None
        
        if df is None or df.empty:
            return None
        
        # Parse price data
        volume_data = df['volume'].fillna(0) if 'volume' in df.columns else []
        clean_volume = [max(0, int(vol)) for vol in volume_data]
        
        price_data = {
            'close': df['close'].tolist(),
            'open': df['open'].tolist() if 'open' in df.columns else [],
            'high': df['high'].tolist() if 'high' in df.columns else [],
            'low': df['low'].tolist() if 'low' in df.columns else [],
            'volume': clean_volume,
        }
        
        if stop_flag.is_set():
            return price_data
        
        # Fetch fundamental data using stockdx methods
        fundamental_data = _fetch_stockdx_fundamentals(ticker, symbol, stop_flag)
        
        # Merge fundamental data
        if fundamental_data:
            price_data.update(fundamental_data)
        
        return price_data
        
    except Exception as e:
        print(f"stockdx error: {e}")
        return None

def _fetch_stockdx_fundamentals(ticker, symbol, stop_flag):
    """Fetch fundamental data using stockdx methods"""
    
    if stop_flag.is_set():
        return {}
    
    fundamental_data = {}
    
    try:
        # Get income statement with rate limiting awareness
        if stop_flag.is_set():
            return {}
            
        try:
            income_statement = ticker.yahoo_api_income_statement(frequency='quarterly', format='raw')
            if income_statement is not None and not income_statement.empty:
                # Extract revenue
                if 'quarterlyTotalRevenue' in income_statement.columns:
                    latest_idx = income_statement.index[-1]
                    rev_value = income_statement.loc[latest_idx, 'quarterlyTotalRevenue']
                    if pd.notna(rev_value) and rev_value != 0:
                        fundamental_data['revenue'] = _format_value(float(rev_value))
                
                # Extract net income
                for col in ['quarterlyNetIncome', 'quarterlyNetIncomeCommonStockholders']:
                    if col in income_statement.columns:
                        latest_idx = income_statement.index[-1]
                        ni_value = income_statement.loc[latest_idx, col]
                        if pd.notna(ni_value) and ni_value != 0:
                            fundamental_data['net_income'] = _format_value(float(ni_value))
                        break
        except Exception as e:
            print(f"⚠️ stockdx income statement failed: {e}")
        
        if stop_flag.is_set():
            return fundamental_data
        
        # Get cash flow with delay to avoid rate limiting
        time.sleep(1)  # Small delay between calls
        
        try:
            cash_flow = ticker.yahoo_api_cash_flow(frequency='quarterly', format='raw')
            if cash_flow is not None and not cash_flow.empty:
                for col in ['quarterlyOperatingCashFlow', 'quarterlyFreeCashFlow']:
                    if col in cash_flow.columns:
                        latest_idx = cash_flow.index[-1]
                        cf_value = cash_flow.loc[latest_idx, col]
                        if pd.notna(cf_value) and cf_value != 0:
                            fundamental_data['cash_flow'] = _format_value(float(cf_value))
                        break
        except Exception as e:
            print(f"⚠️ stockdx cash flow failed: {e}")
        
        print(f"✅ stockdx fundamental data fetched for {symbol}")
        
    except Exception as e:
        print(f"⚠️ stockdx fundamentals error: {e}")
    
    return fundamental_data

def _format_yahoo_value(value_dict):
    """Format Yahoo API value dictionary"""
    if not value_dict or 'raw' not in value_dict:
        return None
    
    return _format_value(value_dict['raw'])

def _format_value(value):
    """Format numerical value to readable string"""
    if value is None or value == 0:
        return None
    
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"${value/1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:.0f}"
    except (ValueError, TypeError):
        return None

# Updated cache processing function
def _cache_comprehensive_data(symbol, price_df, additional_data=None):
    """Enhanced cache function that handles integrated fundamental data"""
    try:
        from components.stock.stock_data_manager import stock_data_cache, StockData
        
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
        
        # Extract volume
        _extract_volume_from_cache(price_df, stock_data)
        
        # Use integrated fundamental data if available
        if additional_data:
            if 'revenue' in additional_data and additional_data['revenue']:
                stock_data.revenue = additional_data['revenue']
            
            if 'net_income' in additional_data and additional_data['net_income']:
                stock_data.net_income = additional_data['net_income']
            
            if 'cash_flow' in additional_data and additional_data['cash_flow']:
                stock_data.cash_flow = additional_data['cash_flow']
            
            if 'market_cap' in additional_data and additional_data['market_cap']:
                stock_data.market_cap = additional_data['market_cap']
            
            print(f"✅ Used integrated fundamental data for {symbol}")
        else:
            # Fallback to separate fundamental fetch only if no integrated data
            print(f"⚠️ No integrated fundamentals for {symbol}, skipping separate fetch to avoid rate limiting")
        
        # Update cache and UI
        stock_data_cache[symbol] = stock_data
        _update_stock_tag_cache(symbol, stock_data)
        _add_to_portfolio_table(symbol)
        
        print(f"✅ Comprehensive data cached for {symbol}")
        
    except Exception as e:
        print(f"❌ Error caching data: {e}")

# Updated data conversion function
def _convert_to_dataframe(data):
    """Convert API data to DataFrame and extract additional data"""
    try:
        df_data = {}
        additional_data = {}
        
        # Find max length for price data
        price_keys = ['open', 'high', 'low', 'close', 'volume']
        max_length = max(len(data.get(key, [])) for key in price_keys)
        
        # Process price data
        for key in price_keys:
            values = data.get(key, [])
            while len(values) < max_length:
                values.append(None if key != 'volume' else 0)
            df_data[key] = values[:max_length]
        
        df = pd.DataFrame(df_data)
        
        # Add timestamps if available
        if 'timestamps' in data and data['timestamps']:
            try:
                df.index = pd.to_datetime(data['timestamps'], unit='s')
            except Exception:
                pass
        
        # Extract additional fundamental data
        fundamental_keys = ['revenue', 'net_income', 'cash_flow', 'market_cap']
        for key in fundamental_keys:
            if key in data and data[key]:
                additional_data[key] = data[key]
        
        return df, additional_data
        
    except Exception as e:
        print(f"❌ Error converting to DataFrame: {e}")
        return pd.DataFrame({'close': data.get('close', [])}), {}

# Updated main processing function
def _process_successful_fetch(symbol, data, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Process successfully fetched data with integrated fundamentals"""
    try:
        # 1. Update chart immediately
        _update_chart_with_data(data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
        
        # 2. Convert to DataFrame and extract additional data
        df, additional_data = _convert_to_dataframe(data)
        
        # 3. Cache comprehensive data (includes any integrated fundamentals)
        _cache_comprehensive_data(symbol, df, additional_data)
        
        # 4. Update request tracking
        global last_request_time
        last_request_time = time.time()
        
        print(f"✅ Successfully processed all data for {symbol}")
        
    except Exception as e:
        print(f"❌ Error processing data for {symbol}: {e}")
def _parse_yahoo_response(data):
    """Parse Yahoo API response"""
    try:
        chart = data['chart']['result'][0]
        quotes = chart['indicators']['quote'][0]
        
        # Parse volume
        raw_volume = quotes.get('volume', [])
        clean_volume = [max(0, int(vol)) if vol is not None else 0 for vol in raw_volume]
        
        return {
            'timestamps': chart['timestamp'],
            'open': quotes.get('open', []),
            'high': quotes.get('high', []),
            'low': quotes.get('low', []),
            'close': quotes.get('close', []),
            'volume': clean_volume,
        }
    except Exception:
        return None

def _process_result(symbol, data, source_name, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Process the successful result"""
    print(f"🎯 Processing result from {source_name} for {symbol}")
    
    # Use existing processing function
    _process_successful_fetch(symbol, data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
    
    print(f"✅ Completed processing {symbol} from {source_name}")

def stop_all_fetches_for_symbol(symbol):
    """Stop all active fetches for a symbol (e.g., when user switches stocks)"""
    if symbol in active_fetches:
        active_fetches[symbol]['stop_flag'].set()
        print(f"🛑 Stopped all fetches for {symbol}")

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
    """Convert API data to DataFrame - volume already cleaned by each API"""
    try:
        df_data = {}
        
        # Find max length
        max_length = max(len(data.get(key, [])) for key in ['open', 'high', 'low', 'close', 'volume'])
        
        # Process each column - volume is already clean
        for key in ['open', 'high', 'low', 'close', 'volume']:
            values = data.get(key, [])
            # Pad to max length
            while len(values) < max_length:
                values.append(None if key != 'volume' else 0)
            df_data[key] = values[:max_length]
        
        df = pd.DataFrame(df_data)
        
        # Add timestamps if available
        if 'timestamps' in data and data['timestamps']:
            try:
                df.index = pd.to_datetime(data['timestamps'], unit='s')
            except Exception:
                pass  # Skip timestamp index if it fails
        
        return df
        
    except Exception as e:
        print(f"❌ Error converting to DataFrame: {e}")
        # Fallback to just close prices
        return pd.DataFrame({'close': data.get('close', [])})
    
def _cache_comprehensive_data(symbol, price_df):
    """Cache all data including fundamentals"""
    try:
        from components.stock.stock_data_manager import stock_data_cache, StockData
        
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
        _extract_volume_from_cache(price_df, stock_data)
        
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
    """Apply enhanced rate limiting to prevent API abuse"""
    global last_request_time, request_count
    
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    # Adaptive delay based on request count
    if request_count > 15:
        base_delay = 15.0  # Much longer delay after many requests
    elif request_count > 10:
        base_delay = 12.0
    elif request_count > 5:
        base_delay = 10.0
    else:
        base_delay = RATE_LIMIT_DELAY
    
    if time_since_last < base_delay:
        sleep_time = base_delay - time_since_last
        print(f"⏱️ Rate limiting: waiting {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    
    # Add random delay to avoid pattern detection
    random_delay = random.uniform(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)
    print(f"⏱️ Random delay: {random_delay:.2f} seconds...")
    time.sleep(random_delay)
    
    # Update counters
    last_request_time = time.time()
    request_count += 1
    
    # Reset counter periodically
    if request_count > 20:
        print("🔄 Resetting request counter and taking longer break...")
        time.sleep(30)  # Take a 30-second break
        request_count = 0

def reset_rate_limiting():
    """Reset rate limiting counters - call this when switching symbols"""
    global last_request_time, request_count
    request_count = 0
    last_request_time = 0
    print("🔄 Rate limiting counters reset")
    
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

def _extract_volume_from_cache(price_df, stock_data):
    """Extract volume from DataFrame - already cleaned by API functions"""
    try:
        if 'volume' not in price_df.columns:
            return
        
        # Get the latest non-zero volume
        volume_series = price_df['volume']
        for i in range(len(volume_series) - 1, -1, -1):
            vol = volume_series.iloc[i]
            if vol > 0:
                stock_data.volume = int(vol)
                break
                
    except Exception as e:
        print(f"⚠️ Could not extract volume: {e}")
        
def _update_stock_tag_cache(symbol, stock_data):
    """Update stock tag with fresh cache data"""
    try:
        from components.stock.stock_data_manager import find_tag_by_name
        
        tag = find_tag_by_name(symbol)
        if tag:
            tag.stock_data = stock_data
            tag.update_cache_indicator()
    except Exception as e:
        print(f"⚠️ Could not update stock tag cache: {e}")

def _add_to_portfolio_table(symbol):
    """Add stock to portfolio table"""
    try:
        from components.graph.graph_dpg import add_stock_to_portfolio_table
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
