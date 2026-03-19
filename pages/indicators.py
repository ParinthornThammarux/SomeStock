"""
pages/indicators.py - Technical indicators analysis page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.data_fetch import fetch_stock_data
from core.indicators import ema, sma, rsi, momentum, patterns


def render():
    """Render the indicators page"""
    st.title("Technical Indicators")
    st.markdown("---")
    
    # Sidebar configuration
    symbol = st.sidebar.text_input("Stock Symbol:", value="AAPL")
    period = st.sidebar.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    # Indicator selection
    st.sidebar.markdown("### Select Indicators")
    show_ema = st.sidebar.checkbox("EMA Crossover (12/26)", value=True)
    show_rsi = st.sidebar.checkbox("RSI (14)", value=True)
    show_momentum = st.sidebar.checkbox("Momentum (10)", value=True)
    
    # EMA parameters
    if show_ema:
        ema_fast = st.sidebar.slider("Fast EMA:", 5, 20, 12)
        ema_slow = st.sidebar.slider("Slow EMA:", 20, 50, 26)
    
    if symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            try:
                stock_data = fetch_stock_data(symbol, period=period, interval="1d")
                
                if stock_data and stock_data.has_data():
                    df = stock_data.price_history
                    
                    # Handle both 'close' and 'Close' column names
                    close_col = 'close' if 'close' in df.columns else 'Close'
                    close_prices = df[close_col].values
                    
                    # Create figure with secondary y-axis
                    from plotly.subplots import make_subplots
                    
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=("Price & EMA", "RSI", "Momentum")
                    )
                    
                    # Row 1: Price and EMA
                    fig.add_trace(
                        go.Scatter(y=close_prices, name="Price", line=dict(color="blue")),
                        row=1, col=1
                    )
                    
                    if show_ema:
                        ema_fast_data = ema.calculate_ema(close_prices, timeperiod=ema_fast)
                        ema_slow_data = ema.calculate_ema(close_prices, timeperiod=ema_slow)
                        
                        fig.add_trace(
                            go.Scatter(y=ema_fast_data, name=f"EMA {ema_fast}", line=dict(color="orange")),
                            row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(y=ema_slow_data, name=f"EMA {ema_slow}", line=dict(color="green")),
                            row=1, col=1
                        )
                    
                    # Row 2: RSI
                    if show_rsi:
                        rsi_data = rsi.calculate_rsi(close_prices, timeperiod=14)
                        fig.add_trace(
                            go.Scatter(y=rsi_data, name="RSI(14)", line=dict(color="purple")),
                            row=2, col=1
                        )
                        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    
                    # Row 3: Momentum
                    if show_momentum:
                        mom_data = momentum.calculate_momentum(close_prices, timeperiod=10)
                        fig.add_trace(
                            go.Scatter(y=mom_data, name="Momentum(10)", line=dict(color="cyan")),
                            row=3, col=1
                        )
                        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
                    
                    fig.update_layout(height=800, hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display signals
                    st.markdown("### Trading Signals")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    if show_ema:
                        with col1:
                            st.write("#### EMA Crossover")
                            crossovers = ema.detect_ema_crossovers(ema_fast_data, ema_slow_data)
                            if crossovers:
                                for idx, signal_type in crossovers[-5:]:  # Last 5
                                    color = "🟢" if signal_type == "bullish" else "🔴"
                                    st.write(f"{color} {signal_type.upper()} at bar {idx}")
                            else:
                                st.write("No crossovers detected")
                    
                    if show_rsi:
                        with col2:
                            st.write("#### RSI Signals")
                            rsi_signals = rsi.detect_rsi_signals(rsi_data)
                            if rsi_signals:
                                for idx, signal_type in rsi_signals[-5:]:
                                    color = "🟢" if signal_type == "oversold" else "🔴"
                                    st.write(f"{color} {signal_type.upper()} at bar {idx}")
                            else:
                                st.write("No extremes detected")
                    
                    if show_momentum:
                        with col3:
                            st.write("#### Momentum")
                            latest_mom = mom_data[-1] if not np.isnan(mom_data[-1]) else 0
                            trend = "📈 Bullish" if latest_mom > 0 else "📉 Bearish"
                            st.write(f"Current: {trend} ({latest_mom:.2f})")
                    
                else:
                    st.error(f"Could not fetch data for {symbol}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
