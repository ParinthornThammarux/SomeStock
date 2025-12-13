"""
Streamlit Application - Stock Analysis Tool
Main entry point for the migrated application from DearPyGUI

Run with: streamlit run app/streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "welcome"

# Sidebar navigation
st.sidebar.title("📈 Stock Analysis")
page = st.sidebar.radio(
    "Navigation",
    ["Welcome", "Search Stock", "Dashboard", "Indicators", "Custom Analysis"],
    key="page_selector"
)

# Page routing
if page == "Welcome":
    st.session_state.current_page = "welcome"
elif page == "Search Stock":
    st.session_state.current_page = "search"
elif page == "Dashboard":
    st.session_state.current_page = "dashboard"
elif page == "Indicators":
    st.session_state.current_page = "indicators"
elif page == "Custom Analysis":
    st.session_state.current_page = "custom"

# Import and render pages
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pages.welcome import render as welcome_render
from pages.search import render as search_render
from pages.dashboard import render as dashboard_render
from pages.indicators import render as indicators_render
from pages.custom_content import render as custom_render

page_map = {
    "welcome": welcome_render,
    "search": search_render,
    "dashboard": dashboard_render,
    "indicators": indicators_render,
    "custom": custom_render,
}

# Render the current page
if st.session_state.current_page in page_map:
    try:
        page_map[st.session_state.current_page]()
    except Exception as e:
        st.error(f"Error loading page: {e}")
        if st.checkbox("Show error details"):
            import traceback
            st.write(traceback.format_exc())
else:
    welcome_render()

# Footer
st.sidebar.markdown("---")
from utils.constants import VERSION
st.sidebar.markdown(f"Version: {VERSION}")
