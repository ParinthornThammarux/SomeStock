"""
pages/welcome.py - Welcome page for Streamlit app
"""

import streamlit as st
from utils import constants


def render():
    """Render the welcome page"""
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Welcome to SomeStock")
        st.markdown("---")
        
        st.write("### A Stock Analysis Tool using Technical Indicators")
        
        st.markdown(f"""
        **Version:** {constants.VERSION}
        
        This application provides:
        - Real-time stock data fetching
        - Technical indicators (EMA, SMA, RSI, Momentum)
        - Candlestick pattern detection (Doji, Hammer)
        - Trend analysis and crossover signals
        
        #### Get Started:
        1. Use the **Search Stock** page to find and analyze stocks
        2. View detailed **Dashboard** with multiple timeframes
        3. Apply **Indicators** to identify trading signals
        4. Create **Custom Analysis** with your own parameters
        """)
        
        st.markdown("---")
        st.info("Select a page from the sidebar to begin!")
