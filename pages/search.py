"""
pages/search.py - Stock search and quick analysis page
"""

import streamlit as st
import pandas as pd
from core.data_fetch import fetch_stock_data


def load_stock_list():
    """Get list of common stocks"""
    return {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "MSFT": "Microsoft Corporation",
        "TSLA": "Tesla Inc.",
        "AMZN": "Amazon.com Inc.",
    }


def render():
    """Render the stock search page"""
    st.title("🔍 Search Stock")
    st.markdown("---")
    
    # Load available stocks
    try:
        stock_list = load_stock_list()
        stock_symbols = list(stock_list.keys()) if stock_list else []
    except Exception as e:
        print(f"Error loading stock list: {e}")
        stock_symbols = []
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.selectbox(
            "Select or search for a stock symbol:",
            stock_symbols if stock_symbols else ["AAPL", "GOOGL", "MSFT", "TSLA"],
            index=0
        )
    
    with col2:
        period = st.selectbox(
            "Period:",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
    
    if symbol:
        st.write(f"### Analysis for {symbol}")
        
        # Fetch data
        with st.spinner(f"Fetching data for {symbol}..."):
            try:
                # Fetch stock data
                stock_data = fetch_stock_data(symbol, period=period, interval="1d")
                
                if stock_data and stock_data.has_data():
                    # Display price data
                    col1, col2, col3 = st.columns(3)
                    
                    df = stock_data.price_history
                    
                    # Handle both 'close' and 'Close' column names
                    close_col = 'close' if 'close' in df.columns else 'Close'
                    
                    latest_price = df[close_col].iloc[-1] if len(df) > 0 else 0
                    prev_price = df[close_col].iloc[-2] if len(df) > 1 else latest_price
                    change = latest_price - prev_price
                    change_pct = (change / prev_price * 100) if prev_price != 0 else 0
                    
                    with col1:
                        st.metric("Current Price", f"${latest_price:.2f}", f"{change:.2f} ({change_pct:.2f}%)")
                    
                    with col2:
                        st.metric("High (52w)", f"${df['high'].max():.2f}")
                    
                    with col3:
                        st.metric("Low (52w)", f"${df['low'].min():.2f}")
                    
                    # Plot price chart
                    chart_df = df[[close_col]].copy()
                    chart_df.columns = ['Price']
                    st.line_chart(chart_df)
                    
                    # Show data table
                    st.subheader("Price History")
                    st.dataframe(df[['open', 'high', 'low', 'close', 'volume']].tail(20), use_container_width=True)
                    
                else:
                    st.error(f"Could not fetch data for {symbol}")
                    
            except Exception as e:
                st.error(f"Error fetching data: {e}")
