"""
pages/custom_content.py - Custom analysis and parameter tuning page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.data_fetch import fetch_stock_data
from core.indicators import ema, sma, rsi, momentum


def render():
    """Render the custom analysis page"""
    st.title("⚙️ Custom Analysis")
    st.markdown("---")
    
    # Two-column layout
    col_config, col_analysis = st.columns([1, 3])
    
    with col_config:
        st.subheader("Configuration")
        
        # Stock selection
        symbol = st.text_input("Stock Symbol:", value="AAPL")
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        
        st.markdown("---")
        
        # Indicator selection
        st.write("#### Indicators")
        indicators = {}
        
        indicators['ema'] = st.checkbox("EMA Crossover", value=True)
        if indicators['ema']:
            indicators['ema_fast'] = st.slider("EMA Fast", 5, 20, 12)
            indicators['ema_slow'] = st.slider("EMA Slow", 20, 50, 26)
        
        indicators['sma'] = st.checkbox("SMA Trend", value=False)
        if indicators['sma']:
            indicators['sma_short'] = st.slider("SMA Short", 10, 40, 20)
            indicators['sma_long'] = st.slider("SMA Long", 40, 200, 50)
        
        indicators['rsi'] = st.checkbox("RSI", value=True)
        if indicators['rsi']:
            indicators['rsi_period'] = st.slider("RSI Period", 5, 30, 14)
            indicators['rsi_oversold'] = st.slider("Oversold Level", 10, 40, 30)
            indicators['rsi_overbought'] = st.slider("Overbought Level", 60, 90, 70)
        
        indicators['momentum'] = st.checkbox("Momentum", value=True)
        if indicators['momentum']:
            indicators['mom_period'] = st.slider("Momentum Period", 5, 30, 10)
    
    # Analysis section
    with col_analysis:
        if symbol:
            with st.spinner(f"Loading {symbol}..."):
                try:
                    stock_data = fetch_stock_data(symbol, period=period, interval="1d")
                    
                    if stock_data and stock_data.has_data():
                        df = stock_data.price_history
                        
                        # Handle both 'close' and 'Close' column names
                        close_col = 'close' if 'close' in df.columns else 'Close'
                        close_prices = df[close_col].values
                        
                        # Build figure
                        fig = go.Figure()
                        
                        # Price
                        fig.add_trace(go.Scatter(
                            y=close_prices, 
                            name="Price", 
                            line=dict(color="blue", width=2)
                        ))
                        
                        # EMA
                        if indicators.get('ema'):
                            ema_fast = ema.calculate_ema(close_prices, timeperiod=indicators['ema_fast'])
                            ema_slow = ema.calculate_ema(close_prices, timeperiod=indicators['ema_slow'])
                            
                            fig.add_trace(go.Scatter(
                                y=ema_fast, 
                                name=f"EMA {indicators['ema_fast']}", 
                                line=dict(color="orange")
                            ))
                            fig.add_trace(go.Scatter(
                                y=ema_slow, 
                                name=f"EMA {indicators['ema_slow']}", 
                                line=dict(color="green")
                            ))
                        
                        # SMA
                        if indicators.get('sma'):
                            sma_short = sma.calculate_sma(close_prices, timeperiod=indicators['sma_short'])
                            sma_long = sma.calculate_sma(close_prices, timeperiod=indicators['sma_long'])
                            
                            fig.add_trace(go.Scatter(
                                y=sma_short, 
                                name=f"SMA {indicators['sma_short']}", 
                                line=dict(color="purple", dash="dash")
                            ))
                            fig.add_trace(go.Scatter(
                                y=sma_long, 
                                name=f"SMA {indicators['sma_long']}", 
                                line=dict(color="red", dash="dash")
                            ))
                        
                        fig.update_layout(
                            title=f"{symbol} Custom Analysis",
                            height=500,
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistics
                        st.markdown("### Statistics")
                        
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                        
                        with stats_col1:
                            st.metric("Latest Price", f"${close_prices[-1]:.2f}")
                        
                        with stats_col2:
                            st.metric("52W High", f"${df['high'].max():.2f}")
                        
                        with stats_col3:
                            st.metric("52W Low", f"${df['low'].min():.2f}")
                        
                        with stats_col4:
                            volatility = df[close_col].pct_change().std() * 100
                            st.metric("Volatility", f"{volatility:.2f}%")
                    
                    else:
                        st.error(f"Could not fetch data for {symbol}")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
