"""
pages/dashboard.py - Comprehensive stock dashboard with multiple indicators
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.data_fetch import fetch_stock_data , fetch_financials
from core.indicators import ema, sma, rsi, momentum
from core.utils import format_money


def render():
    """Render the dashboard page"""
    st.title("Dashboard")
    st.markdown("---")
    
    # Sidebar controls
    symbol = st.sidebar.text_input("Enter stock symbol:", value="AAPL")
    period = st.sidebar.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    
    if symbol:
        with st.spinner(f"Loading dashboard for {symbol}..."):
            try:
                # Fetch data
                stock_data = fetch_stock_data(symbol, period=period, interval="1d")
                
                if stock_data and stock_data.has_data():
                    df = stock_data.price_history
                    
                    # Handle both 'close' and 'Close' column names
                    close_col = 'close' if 'close' in df.columns else 'Close'
                    close_prices = df[close_col].values
                    
                    # Calculate indicators
                    ema12 = ema.calculate_ema(close_prices, timeperiod=12)
                    ema26 = ema.calculate_ema(close_prices, timeperiod=26)
                    sma20 = sma.calculate_sma(close_prices, timeperiod=20)
                    sma50 = sma.calculate_sma(close_prices, timeperiod=50)
                    rsi14 = rsi.calculate_rsi(close_prices, timeperiod=14)
                    mom10 = momentum.calculate_momentum(close_prices, timeperiod=10)
                    
                    # Create tabs
                    tab1, tab2, tab3, tab4 ,tab5 = st.tabs(["Price & EMAs", "Moving Averages", "RSI", "Momentum" , "Financials"])
                    
                    with tab1:
                        st.subheader(f"{symbol} - Price with EMA Crossover")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=close_prices, name="Price", line=dict(color="blue")))
                        fig.add_trace(go.Scatter(y=ema12, name="EMA 12", line=dict(color="orange")))
                        fig.add_trace(go.Scatter(y=ema26, name="EMA 26", line=dict(color="green")))
                        fig.update_layout(hovermode='x unified', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        st.subheader(f"{symbol} - Moving Averages")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=close_prices, name="Price", line=dict(color="blue")))
                        fig.add_trace(go.Scatter(y=sma20, name="SMA 20", line=dict(color="purple")))
                        fig.add_trace(go.Scatter(y=sma50, name="SMA 50", line=dict(color="red")))
                        fig.update_layout(hovermode='x unified', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab3:
                        st.subheader(f"{symbol} - Relative Strength Index (RSI 14)")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=rsi14, name="RSI", line=dict(color="brown")))
                        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                        fig.update_layout(hovermode='x unified', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab4:
                        st.subheader(f"{symbol} - Momentum (10-period)")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(y=mom10, name="Momentum", line=dict(color="cyan")))
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        fig.update_layout(hovermode='x unified', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    with tab5:
                        st.subheader(f"{symbol} Financial Statements")

                        financials = fetch_financials(symbol)

                        income = financials["income_statement"]
                        balance = financials["balance_sheet"]
                        cashflow = financials["cashflow"]

                        st.write("### Income Statement")
                        st.dataframe(income.applymap(format_money))

                        st.write("### Balance Sheet")
                        st.dataframe(balance.applymap(format_money))

                        st.write("### Cash Flow")
                        st.dataframe(cashflow.applymap(format_money))
                    
                else:
                    st.error(f"Could not fetch data for {symbol}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
                if st.checkbox("Show error details"):
                    st.write(str(e))
