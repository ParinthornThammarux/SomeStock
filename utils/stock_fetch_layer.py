# utils/stock_fetch_layer.py - Unified Fetch Version

import dearpygui.dearpygui as dpg
import time
import random
import requests
import pandas as pd
from utils import constants
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================

# Rate limiting configuration
RATE_LIMIT_DELAY = 5.0  # Reduced since we're making fewer calls
RANDOM_DELAY_MIN = 1.0
RANDOM_DELAY_MAX = 2.0
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Global state
last_request_time = 0
request_count = 0
active_fetches = {}  # {symbol: {'stop_flag': threading.Event(), 'result': None}}

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def fetch_stock_data(symbol, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """
    Unified fetch - gets ALL data from each source in a single call
    """
    print("=" * 80)
    print(f"🚀 UNIFIED FETCH FOR: {symbol}")
    print("=" * 80)
    
    # Stop any existing fetches for this symbol
    stop_all_fetches_for_symbol(symbol)
    
    # Create stop flag for this symbol
    stop_flag = threading.Event()
    fetch_info = {
        'stop_flag': stop_flag,
        'result': None,
        'successful_source': None
    }
    active_fetches[symbol] = fetch_info
    
    # Define unified fetch sources (priority order)
    sources = [
        ("yfinance Complete", _fetch_yfinance_complete),
        ("yahooquery Complete", _fetch_yahoo_complete),
        ("stockdx Complete", _fetch_stockdx_complete),
    ]
    
    # Try sources in parallel - first to succeed wins
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all fetch tasks
        future_to_source = {}
        for source_name, fetch_function in sources:
            future = executor.submit(fetch_function, symbol, stop_flag)
            future_to_source[future] = source_name
        
        print(f"🚀 Started {len(sources)} unified fetches for {symbol}")
        
        # Process results as they come in
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            
            # Check if we should stop
            if stop_flag.is_set():
                print(f"🛑 Stopping {source_name} - another source succeeded")
                break
                
            try:
                result = future.result()
                
                if result and _validate_complete_data(result):
                    print(f"✅ First success: {source_name}")
                    
                    # Signal all other threads to stop
                    stop_flag.set()
                    
                    # Process the complete result
                    _process_complete_result(symbol, result, source_name, line_tag, x_axis_tag, y_axis_tag, plot_tag)
                    
                    # Clean up
                    if symbol in active_fetches:
                        del active_fetches[symbol]
                    return
                    
                else:
                    print(f"❌ {source_name} failed or incomplete data")
                    
            except Exception as e:
                print(f"❌ {source_name} error: {e}")
    
    # If we get here, all sources failed
    print(f"❌ All unified sources failed for {symbol}")
    if symbol in active_fetches:
        del active_fetches[symbol]

# =============================================================================
# UNIFIED FETCH FUNCTIONS
# =============================================================================

def _fetch_yfinance_complete(symbol, stop_flag):
    """Fetch complete data from yfinance in one call"""
    if stop_flag.is_set():
        return None
    
    try:
        print(f"📡 yfinance complete fetch for {symbol}")
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        
        # Check stop flag
        if stop_flag.is_set():
            return None
        
        # Get price data
        print(f"🔄 Getting price history for {symbol}")
        hist = ticker.history(period="1d", interval="5m")
        
        if stop_flag.is_set():
            return None
        
        if hist.empty:
            print(f"❌ No price history for {symbol}")
            return None
        
        # Get fundamental data
        print(f"🔄 Getting fundamentals for {symbol}")
        try:
            info = ticker.info
        except Exception as e:
            print(f"⚠️ Could not get info for {symbol}: {e}")
            info = {}
        
        if stop_flag.is_set():
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
        
        # Parse fundamental data
        fundamentals = {}
        if info and isinstance(info, dict):
            # Revenue
            for revenue_key in ['totalRevenue', 'revenue']:
                if revenue_key in info and info[revenue_key] and info[revenue_key] != 0:
                    try:
                        fundamentals['revenue'] = _format_value(info[revenue_key])
                        break
                    except:
                        continue
            
            # Market cap
            if 'marketCap' in info and info['marketCap'] and info['marketCap'] != 0:
                try:
                    fundamentals['market_cap'] = _format_value(info['marketCap'])
                except:
                    pass
            
            # Net income
            for ni_key in ['netIncomeToCommon', 'netIncome']:
                if ni_key in info and info[ni_key] and info[ni_key] != 0:
                    try:
                        fundamentals['net_income'] = _format_value(info[ni_key])
                        break
                    except:
                        continue
            
            # Cash flow - try multiple keys
            for cf_key in ['operatingCashflow', 'freeCashflow', 'totalCashFromOperatingActivities', 'operatingCashFlow', 'freeCashFlow']:
                if cf_key in info and info[cf_key] and info[cf_key] != 0:
                    try:
                        fundamentals['cash_flow'] = _format_value(info[cf_key])
                        break
                    except:
                        continue
        
        # Combine everything
        complete_data = {
            **price_data,  # price, volume, timestamps
            **fundamentals  # revenue, net_income, etc.
        }
        
        print(f"✅ yfinance complete: price + {list(fundamentals.keys())}")
        return complete_data
        
    except ImportError:
        print(f"❌ yfinance not available")
        return None
    except Exception as e:
        print(f"❌ yfinance complete error for {symbol}: {e}")
        return None

def _fetch_yahoo_complete(symbol, stop_flag):
    """Fetch complete data from Yahoo using yahooquery for comprehensive data"""
    if stop_flag.is_set():
        return None
    
    try:
        print(f"📡 yahooquery complete fetch for {symbol}")
        from yahooquery import Ticker
        
        # Create ticker object
        ticker = Ticker(symbol)
        
        if stop_flag.is_set():
            return None
        
        # Get comprehensive data in one call
        print(f"🔄 Getting comprehensive data for {symbol}")
        
        # Get price history
        hist = ticker.history(period="1d", interval="5m")
        
        if stop_flag.is_set():
            return None
        
        if hist.empty:
            print(f"❌ No price history for {symbol}")
            return None
        
        # Parse price data
        volume_data = hist['volume'].fillna(0) if 'volume' in hist.columns else []
        clean_volume = [max(0, int(vol)) for vol in volume_data]
        
        price_data = {
            'close': hist['close'].tolist(),
            'open': hist['open'].tolist(),
            'high': hist['high'].tolist(),
            'low': hist['low'].tolist(),
            'volume': clean_volume,
            'timestamps': [int(ts.timestamp()) for ts in hist.index],
        }
        
        if stop_flag.is_set():
            return price_data
        
        # Get comprehensive fundamental data
        fundamentals = {}
        
        try:
            # Get summary detail (includes key metrics)
            summary = ticker.summary_detail
            if summary and not summary.empty:
                row = summary.iloc[0]
                
                # Market cap
                if 'marketCap' in row and pd.notna(row['marketCap']):
                    fundamentals['market_cap'] = _format_value(row['marketCap'])
                
                # PE ratio
                if 'trailingPE' in row and pd.notna(row['trailingPE']):
                    fundamentals['pe_ratio'] = float(row['trailingPE'])
                
                # Volume
                if 'volume' in row and pd.notna(row['volume']):
                    fundamentals['volume'] = int(row['volume'])
                
                # Average volume
                if 'averageVolume' in row and pd.notna(row['averageVolume']):
                    fundamentals['avg_volume'] = int(row['averageVolume'])
        
        except Exception as e:
            print(f"⚠️ Could not get summary detail: {e}")
        
        if stop_flag.is_set():
            return {**price_data, **fundamentals}
        
        try:
            # Get financial data
            financial_data = ticker.financial_data
            if financial_data and not financial_data.empty:
                row = financial_data.iloc[0]
                
                # Revenue
                if 'totalRevenue' in row and pd.notna(row['totalRevenue']):
                    fundamentals['revenue'] = _format_value(row['totalRevenue'])
                
                # Operating cash flow
                if 'operatingCashflow' in row and pd.notna(row['operatingCashflow']):
                    fundamentals['cash_flow'] = _format_value(row['operatingCashflow'])
                
                # Free cash flow
                if 'freeCashflow' in row and pd.notna(row['freeCashflow']):
                    fundamentals['free_cash_flow'] = _format_value(row['freeCashflow'])
        
        except Exception as e:
            print(f"⚠️ Could not get financial data: {e}")
        
        if stop_flag.is_set():
            return {**price_data, **fundamentals}
        
        try:
            # Get income statement for net income
            income_stmt = ticker.income_statement(frequency='quarterly')
            if income_stmt and not income_stmt.empty:
                # Get most recent quarter
                latest_data = income_stmt.iloc[0]
                
                # Net income
                if 'NetIncome' in latest_data and pd.notna(latest_data['NetIncome']):
                    fundamentals['net_income'] = _format_value(latest_data['NetIncome'])
                elif 'NetIncomeCommonStockholders' in latest_data and pd.notna(latest_data['NetIncomeCommonStockholders']):
                    fundamentals['net_income'] = _format_value(latest_data['NetIncomeCommonStockholders'])
        
        except Exception as e:
            print(f"⚠️ Could not get income statement: {e}")
        
        if stop_flag.is_set():
            return {**price_data, **fundamentals}
        
        try:
            # Get company profile for additional info
            profile = ticker.asset_profile
            if profile and not profile.empty:
                row = profile.iloc[0]
                
                # Company name
                if 'longName' in row and pd.notna(row['longName']):
                    fundamentals['company_name'] = str(row['longName'])
                
                # Industry
                if 'industry' in row and pd.notna(row['industry']):
                    fundamentals['industry'] = str(row['industry'])
                
                # Sector
                if 'sector' in row and pd.notna(row['sector']):
                    fundamentals['sector'] = str(row['sector'])
        
        except Exception as e:
            print(f"⚠️ Could not get asset profile: {e}")
        
        # Combine everything
        complete_data = {
            **price_data,
            **fundamentals
        }
        
        fund_keys = [k for k, v in fundamentals.items() if v is not None]
        print(f"✅ yahooquery complete: price + fundamentals: {fund_keys}")
        return complete_data
        
    except ImportError:
        print(f"❌ yahooquery not available")
    except Exception as e:
        print(f"❌ yahooquery error for {symbol}: {e}")
        return None

def _parse_yahoo_comprehensive_fundamentals(data):
    """Parse comprehensive Yahoo fundamentals response"""
    try:
        fundamentals = {}
        
        if 'quoteSummary' in data and data['quoteSummary']['result']:
            result = data['quoteSummary']['result'][0]
            
            # Financial data
            if 'financialData' in result and result['financialData']:
                fd = result['financialData']
                
                if 'totalRevenue' in fd and fd['totalRevenue']:
                    fundamentals['revenue'] = _format_yahoo_value(fd['totalRevenue'])
                
                if 'operatingCashflow' in fd and fd['operatingCashflow']:
                    fundamentals['cash_flow'] = _format_yahoo_value(fd['operatingCashflow'])
                
                if 'freeCashflow' in fd and fd['freeCashflow']:
                    fundamentals['free_cash_flow'] = _format_yahoo_value(fd['freeCashflow'])
            
            # Summary detail
            if 'summaryDetail' in result and result['summaryDetail']:
                sd = result['summaryDetail']
                
                if 'marketCap' in sd and sd['marketCap']:
                    fundamentals['market_cap'] = _format_yahoo_value(sd['marketCap'])
                
                if 'trailingPE' in sd and sd['trailingPE']:
                    fundamentals['pe_ratio'] = sd['trailingPE'].get('raw') if isinstance(sd['trailingPE'], dict) else sd['trailingPE']
                
                if 'volume' in sd and sd['volume']:
                    fundamentals['volume'] = sd['volume'].get('raw') if isinstance(sd['volume'], dict) else sd['volume']
                
                if 'averageVolume' in sd and sd['averageVolume']:
                    fundamentals['avg_volume'] = sd['averageVolume'].get('raw') if isinstance(sd['averageVolume'], dict) else sd['averageVolume']
            
            # Asset profile
            if 'assetProfile' in result and result['assetProfile']:
                ap = result['assetProfile']
                
                if 'longName' in ap and ap['longName']:
                    fundamentals['company_name'] = ap['longName']
                
                if 'industry' in ap and ap['industry']:
                    fundamentals['industry'] = ap['industry']
                
                if 'sector' in ap and ap['sector']:
                    fundamentals['sector'] = ap['sector']
            
            # Income statement history
            if 'incomeStatementHistory' in result and result['incomeStatementHistory']:
                try:
                    income_history = result['incomeStatementHistory']['incomeStatementHistory']
                    if income_history and len(income_history) > 0:
                        latest_income = income_history[0]  # Most recent
                        
                        if 'netIncome' in latest_income and latest_income['netIncome']:
                            fundamentals['net_income'] = _format_yahoo_value(latest_income['netIncome'])
                        elif 'netIncomeToCommon' in latest_income and latest_income['netIncomeToCommon']:
                            fundamentals['net_income'] = _format_yahoo_value(latest_income['netIncomeToCommon'])
                except Exception:
                    pass
        
        return fundamentals
        
    except Exception as e:
        print(f"❌ Error parsing comprehensive Yahoo fundamentals: {e}")
        return {}
def _fetch_stockdx_complete(symbol, stop_flag):
    """Fetch complete data from stockdx in one call"""
    if stop_flag.is_set():
        return None
    
    try:
        print(f"📡 stockdx complete fetch for {symbol}")
        from stockdex import Ticker
        
        ticker = Ticker(ticker=symbol)
        
        if stop_flag.is_set():
            return None
        
        # Get price data
        print(f"🔄 Getting stockdx price data for {symbol}")
        df = ticker.yahoo_api_price(range='1d', dataGranularity='5m')
        
        if stop_flag.is_set():
            return None
        
        if df is None or df.empty:
            print(f"❌ No stockdx price data for {symbol}")
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
        
        # Get fundamental data
        fundamentals = {}
        
        if stop_flag.is_set():
            return price_data  # Return at least price data
        
        try:
            print(f"🔄 Getting stockdx income statement for {symbol}")
            # Try income statement
            income_statement = None
            try:
                income_statement = ticker.yahoo_api_income_statement(frequency='quarterly', format='raw')
            except:
                try:
                    income_statement = ticker.yahoo_api_income_statement(frequency='annual', format='raw')
                except:
                    pass
            
            if income_statement is not None and not income_statement.empty:
                _extract_revenue_from_statement(income_statement, fundamentals)
                _extract_net_income_from_statement(income_statement, fundamentals)
            
            if stop_flag.is_set():
                return {**price_data, **fundamentals}
            
            print(f"🔄 Getting stockdx cash flow for {symbol}")
            # Try cash flow
            cash_flow = None
            try:
                cash_flow = ticker.yahoo_api_cash_flow(frequency='quarterly', format='raw')
            except:
                try:
                    cash_flow = ticker.yahoo_api_cash_flow(frequency='annual', format='raw')
                except:
                    pass
            
            if cash_flow is not None and not cash_flow.empty:
                _extract_cash_flow_from_statement(cash_flow, fundamentals)
                
        except Exception as e:
            print(f"⚠️ stockdx fundamentals error for {symbol}: {e}")
        
        # Combine everything
        complete_data = {
            **price_data,
            **fundamentals
        }
        
        print(f"✅ stockdx complete: price + {list(fundamentals.keys())}")
        return complete_data
        
    except ImportError:
        print(f"❌ stockdx not available")
        return None
    except Exception as e:
        print(f"❌ stockdx complete error for {symbol}: {e}")
        return None

# =============================================================================
# PROCESSING AND CACHING
# =============================================================================

def _process_complete_result(symbol, data, source_name, line_tag, x_axis_tag, y_axis_tag, plot_tag):
    """Process complete result with both price and fundamental data"""
    print(f"🎯 Processing complete result from {source_name} for {symbol}")
    
    # 1. Update chart immediately with price data
    _update_chart_with_data(data, line_tag, x_axis_tag, y_axis_tag, plot_tag)
    
    # 2. Convert to DataFrame for caching
    df = _convert_price_to_dataframe(data)
    
    # 3. Extract fundamentals
    fundamentals = _extract_fundamentals_from_data(data)
    
    # 4. Cache everything at once
    _cache_complete_data(symbol, df, fundamentals)
    
    # 5. Add to table with complete data
    _add_to_portfolio_table_direct(symbol)
    
    # 6. Update request tracking
    global last_request_time
    last_request_time = time.time()
    
    print(f"✅ Complete processing finished for {symbol} from {source_name}")

def _cache_complete_data(symbol, price_df, fundamentals):
    """Cache complete data (price + fundamentals) in one operation"""
    try:
        from components.stock.stock_data_manager import stock_data_cache, StockData
        
        # Create comprehensive stock data object
        stock_data = StockData(symbol=symbol, company_name=fundamentals.get('company_name', f"{symbol} Corp."))
        
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
        
        # Update fundamental data
        if 'revenue' in fundamentals and fundamentals['revenue']:
            stock_data.revenue = fundamentals['revenue']
        
        if 'net_income' in fundamentals and fundamentals['net_income']:
            stock_data.net_income = fundamentals['net_income']
        
        if 'cash_flow' in fundamentals and fundamentals['cash_flow']:
            stock_data.cash_flow = fundamentals['cash_flow']
        
        if 'market_cap' in fundamentals and fundamentals['market_cap']:
            stock_data.market_cap = fundamentals['market_cap']
        
        # Update cache
        stock_data_cache[symbol] = stock_data
        
        # Update stock tag if it exists
        _update_stock_tag_cache(symbol, stock_data)
        
        fund_summary = [k for k, v in fundamentals.items() if v] or ['none']
        print(f"✅ Complete data cached for {symbol}: price + fundamentals: {fund_summary}")
        
    except Exception as e:
        print(f"❌ Error caching complete data: {e}")

def _add_to_portfolio_table_direct(symbol):
    """Add stock to portfolio table using the fixed direct method"""
    try:
        print(f"📋 Adding {symbol} to portfolio table with complete data")
        
        # Import the internal function directly (bypasses lock issues)
        from components.graph.graph_dpg import _add_stock_to_table_internal, current_table_tag
        
        # Check if table exists
        if not current_table_tag or not dpg.does_item_exist(current_table_tag):
            print(f"❌ Portfolio table not available for {symbol}")
            return
        
        # Check if symbol already exists
        from components.graph.graph_dpg import symbol_exists_in_table
        if symbol_exists_in_table(symbol):
            print(f"📋 {symbol} already exists in table, skipping")
            return
        
        # Add directly
        _add_stock_to_table_internal(symbol)
        print(f"✅ Added {symbol} to table with complete data")
        
    except Exception as e:
        print(f"❌ Error adding {symbol} to table: {e}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _validate_complete_data(data):
    """Validate that we have usable complete data"""
    if not data or data == "RATE_LIMITED":
        return False
    
    # Must have price data
    close_prices = data.get('close', [])
    if not close_prices:
        return False
    
    # Check for valid prices
    valid_prices = [p for p in close_prices if p is not None and p > 0]
    if len(valid_prices) == 0:
        return False
    
    # Don't require fundamentals - nice to have but not mandatory
    return True

def _extract_fundamentals_from_data(data):
    """Extract fundamental data from complete response"""
    fundamentals = {}
    
    fundamental_keys = ['revenue', 'net_income', 'cash_flow', 'market_cap', 'company_name']
    for key in fundamental_keys:
        if key in data and data[key]:
            fundamentals[key] = data[key]
    
    return fundamentals

def _convert_price_to_dataframe(data):
    """Convert price data to DataFrame"""
    try:
        df_data = {}
        
        # Process price data
        price_keys = ['open', 'high', 'low', 'close', 'volume']
        max_length = max(len(data.get(key, [])) for key in price_keys if key in data)
        
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
        
        return df
        
    except Exception as e:
        print(f"❌ Error converting price to DataFrame: {e}")
        return pd.DataFrame({'close': data.get('close', [])})

def _parse_yahoo_price_response(data):
    """Parse Yahoo price API response"""
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
    except Exception as e:
        print(f"❌ Error parsing Yahoo price response: {e}")
        return None

def _parse_yahoo_fundamentals(data):
    """Parse Yahoo fundamentals response"""
    try:
        fundamentals = {}
        
        if 'quoteSummary' in data and data['quoteSummary']['result']:
            result = data['quoteSummary']['result'][0]
            
            if 'financialData' in result:
                fd = result['financialData']
                if 'totalRevenue' in fd and fd['totalRevenue']:
                    fundamentals['revenue'] = _format_yahoo_value(fd['totalRevenue'])
                if 'marketCap' in fd and fd['marketCap']:
                    fundamentals['market_cap'] = _format_yahoo_value(fd['marketCap'])
            
            # Try to get cash flow from cash flow statement
            if 'cashflowStatementHistory' in result:
                try:
                    cf_history = result['cashflowStatementHistory']['cashflowStatements']
                    if cf_history and len(cf_history) > 0:
                        latest_cf = cf_history[0]  # Most recent
                        if 'totalCashFromOperatingActivities' in latest_cf:
                            fundamentals['cash_flow'] = _format_yahoo_value(latest_cf['totalCashFromOperatingActivities'])
                except:
                    pass
        
        return fundamentals
        
    except Exception as e:
        print(f"❌ Error parsing Yahoo fundamentals: {e}")
        return {}

def _extract_revenue_from_statement(income_statement, fundamentals):
    """Extract revenue from income statement"""
    try:
        if 'quarterlyTotalRevenue' in income_statement.columns:
            latest_idx = income_statement.index[-1]
            rev_value = income_statement.loc[latest_idx, 'quarterlyTotalRevenue']
            if pd.notna(rev_value) and rev_value != 0:
                fundamentals['revenue'] = _format_value(float(rev_value))
    except Exception:
        pass

def _extract_net_income_from_statement(income_statement, fundamentals):
    """Extract net income from income statement"""
    try:
        for col in ['quarterlyNetIncome', 'quarterlyNetIncomeCommonStockholders']:
            if col in income_statement.columns:
                latest_idx = income_statement.index[-1]
                ni_value = income_statement.loc[latest_idx, col]
                if pd.notna(ni_value) and ni_value != 0:
                    fundamentals['net_income'] = _format_value(float(ni_value))
                break
    except Exception:
        pass

def _extract_cash_flow_from_statement(cash_flow, fundamentals):
    """Extract cash flow from cash flow statement"""
    try:
        for col in ['quarterlyOperatingCashFlow', 'quarterlyFreeCashFlow']:
            if col in cash_flow.columns:
                latest_idx = cash_flow.index[-1]
                cf_value = cash_flow.loc[latest_idx, col]
                if pd.notna(cf_value) and cf_value != 0:
                    fundamentals['cash_flow'] = _format_value(float(cf_value))
                break
    except Exception:
        pass

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

def _extract_volume_from_cache(price_df, stock_data):
    """Extract volume from DataFrame"""
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
        from components.stock.stock_data_manager import find_tag_by_symbol
        
        tag = find_tag_by_symbol(symbol)
        if tag:
            tag.stock_data = stock_data
            tag.update_cache_indicator()
    except Exception as e:
        print(f"⚠️ Could not update stock tag cache: {e}")

def stop_all_fetches_for_symbol(symbol):
    """Stop all active fetches for a symbol"""
    try:
        if symbol in active_fetches:
            active_fetches[symbol]['stop_flag'].set()
            print(f"🛑 Stopped fetch for {symbol}")
        
        if symbol in active_fetches:
            del active_fetches[symbol]
        
        print(f"🧹 Cleaned up fetch for {symbol}")
        
    except Exception as e:
        print(f"❌ Error stopping fetches for {symbol}: {e}")

# Legacy compatibility
def reset_rate_limiting():
    """Reset rate limiting counters"""
    global last_request_time, request_count
    request_count = 0
    last_request_time = 0
    print("🔄 Rate limiting counters reset")

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