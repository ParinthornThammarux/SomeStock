
"""
Real-Time Price Graph using Stockdex Library
============================================

Simple script to display real-time price graphs for TSLA and CPALL stocks
using the stockdex library with interactive Plotly charts.

Requirements:
    pip install stockdex plotly

Author: Stock Analysis Example
Date: 2025
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Try to import stockdx
try:
    from stockdex import Ticker
    print("✅ Stockdex library imported successfully!")
except ImportError:
    print("❌ Stockdex library not found. Please install it using: pip install stockdex")
    exit(1)

def get_price_data(symbol, period='1d', interval='5m'):
    """Get real-time price data for a stock symbol"""
    try:
        print(f"📊 Fetching price data for {symbol}...")
        ticker = Ticker(ticker=symbol)
        
        # Get intraday price data (most recent available)
        price_data = ticker.yahoo_api_price(range=period, dataGranularity=interval)
        
        if price_data is not None and not price_data.empty:
            print(f"✅ Successfully retrieved {len(price_data)} data points for {symbol}")
            
            # Debug: Print column names and first few rows
            print(f"📋 Available columns: {list(price_data.columns)}")
            print(f"📋 Data shape: {price_data.shape}")
            print(f"📋 Sample data:")
            print(price_data.head(2))
            
            return price_data
        else:
            print(f"⚠️  No price data available for {symbol}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {str(e)}")
        return None

def get_column_mapping(price_data):
    """Map DataFrame columns to standard names"""
    columns = price_data.columns.tolist()
    col_map = {}
    
    for col in columns:
        col_lower = col.lower()
        if 'open' in col_lower:
            col_map['open'] = col
        elif 'high' in col_lower:
            col_map['high'] = col
        elif 'low' in col_lower:
            col_map['low'] = col
        elif 'close' in col_lower or 'adj' in col_lower:
            col_map['close'] = col
        elif 'volume' in col_lower:
            col_map['volume'] = col
    
    return col_map

def create_price_graph(symbol, price_data):
    """Create an interactive price graph using Plotly"""
    if price_data is None:
        return None
    
    col_map = get_column_mapping(price_data)
    print(f"🔍 Column mapping for {symbol}: {col_map}")
    
    # Check if we have the required columns for candlestick
    required_cols = ['open', 'high', 'low', 'close']
    has_all_ohlc = all(col in col_map for col in required_cols)
    
    if has_all_ohlc:
        # Create candlestick chart
        print(f"📊 Creating candlestick chart for {symbol}")
        fig = go.Figure(data=go.Candlestick(
            x=price_data.index,
            open=price_data[col_map['open']],
            high=price_data[col_map['high']],
            low=price_data[col_map['low']],
            close=price_data[col_map['close']],
            name=f"{symbol} OHLC"
        ))
    elif 'close' in col_map:
        # Fall back to line chart
        print(f"📈 Creating line chart for {symbol}")
        fig = go.Figure(data=go.Scatter(
            x=price_data.index,
            y=price_data[col_map['close']],
            mode='lines',
            name=f"{symbol} Price",
            line=dict(width=2)
        ))
    else:
        # Use the first numeric column available
        numeric_cols = price_data.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            print(f"📊 Using column '{numeric_cols[0]}' for {symbol}")
            fig = go.Figure(data=go.Scatter(
                x=price_data.index,
                y=price_data[numeric_cols[0]],
                mode='lines',
                name=f"{symbol} Price",
                line=dict(width=2)
            ))
        else:
            print(f"❌ No suitable numeric columns found for {symbol}")
            return None
    
    # Add volume if available
    if 'volume' in col_map:
        fig.add_trace(go.Bar(
            x=price_data.index,
            y=price_data[col_map['volume']],
            name='Volume',
            yaxis='y2',
            opacity=0.3,
            marker_color='blue'
        ))
        
        # Update layout with volume axis
        fig.update_layout(
            yaxis2=dict(
                title="Volume",
                side="right",
                overlaying="y"
            )
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"{symbol} Real-Time Price Chart",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        yaxis=dict(
            title="Price ($)",
            side="left"
        ),
        xaxis_title="Time",
        template="plotly_dark",
        showlegend=True,
        height=600,
        width=1200,
        hovermode='x unified'
    )
    
    # Update x-axis to show time nicely
    fig.update_xaxes(
        rangeslider_visible=False,
        type="date"
    )
    
    return fig

def display_current_stats(symbol, price_data):
    """Display current price statistics"""
    if price_data is None:
        return
    
    col_map = get_column_mapping(price_data)
    
    try:
        if 'close' in col_map:
            current_price = price_data[col_map['close']].iloc[-1]
            print(f"\n📈 {symbol} Current Statistics:")
            print(f"   Current Price: ${current_price:.2f}")
            
            if 'open' in col_map:
                open_price = price_data[col_map['open']].iloc[0]
                change = current_price - open_price
                change_pct = (change / open_price) * 100
                print(f"   Day Change: ${change:.2f} ({change_pct:+.2f}%)")
            
            if 'high' in col_map:
                high_price = price_data[col_map['high']].max()
                print(f"   Day High: ${high_price:.2f}")
            
            if 'low' in col_map:
                low_price = price_data[col_map['low']].min()
                print(f"   Day Low: ${low_price:.2f}")
            
            if 'volume' in col_map:
                volume = price_data[col_map['volume']].iloc[-1]
                print(f"   Volume: {volume:,.0f}")
        else:
            print(f"\n⚠️  Could not find price data for {symbol}")
            print(f"   Available columns: {list(price_data.columns)}")
            
    except Exception as e:
        print(f"\n❌ Error displaying stats for {symbol}: {str(e)}")
        print(f"   Available columns: {list(price_data.columns)}")

def main():
    """Main function to display real-time price graphs"""
    print("🏦 REAL-TIME STOCK PRICE GRAPHS")
    print("=" * 40)
    print("Fetching real-time price data and creating interactive charts...")
    
    # Stock symbols to analyze
    stocks = [
        ("TSLA", "Tesla Inc."),
        ("CPALL.BK", "CP All Public Company Limited"),
        ("NVDA","Nvidia Corp")
    ]
    
    # Create subplot for multiple stocks
    fig_combined = make_subplots(
        rows=len(stocks), cols=1,
        subplot_titles=[f"{symbol} - {name}" for symbol, name in stocks],
        vertical_spacing=0.08
    )
    
    for i, (symbol, name) in enumerate(stocks, 1):
        print(f"\n{'='*50}")
        print(f"📊 Analyzing {symbol} - {name}")
        print(f"{'='*50}")
        
        # Get price data (1 day with 5-minute intervals for real-time feel)
        price_data = get_price_data(symbol, period='1d', interval='5m')
        
        if price_data is not None:
            # Display current statistics
            display_current_stats(symbol, price_data)
            
            # Create individual graph
            print(f"🎨 Creating interactive chart for {symbol}...")
            individual_fig = create_price_graph(symbol, price_data)
            
            if individual_fig:
                # Show individual chart
                individual_fig.show()
                print(f"✅ Interactive chart for {symbol} opened in browser!")
            
            # Add to combined chart
            col_map = get_column_mapping(price_data)
            if 'close' in col_map:
                fig_combined.add_trace(
                    go.Scatter(
                        x=price_data.index,
                        y=price_data[col_map['close']],
                        mode='lines',
                        name=f"{symbol}",
                        line=dict(width=2)
                    ),
                    row=i, col=1
                )
        else:
            print(f"❌ Could not create chart for {symbol}")
    
    # Show combined chart
    fig_combined.update_layout(
        title={
            'text': "Real-Time Stock Price Comparison",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        template="plotly_dark",
        height=800,
        showlegend=True
    )
    
    print(f"\n🎨 Creating combined comparison chart...")
    fig_combined.show()
    print(f"✅ Combined chart opened in browser!")
    
    print("\n🎉 Real-time price graphs completed!")
    print("📊 Check your browser for interactive charts!")

if __name__ == "__main__":
    # Check required packages
    required_packages = ['stockdex', 'plotly']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\nInstall them using: pip install {' '.join(missing_packages)}")
        exit(1)
    
    # Run the main analysis
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your internet connection and try again.")