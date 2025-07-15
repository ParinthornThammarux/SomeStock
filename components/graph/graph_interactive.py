# components/graph_interactive.py

import dearpygui.dearpygui as dpg
from utils import constants
from utils.plotly_integration import PlotlyInteractiveIntegration
import numpy as np


def create_interactive_tab(parent_tag, timestamp):
    """Interactive charts tab"""
    
    dpg.add_spacer(height=20)
    dpg.add_text("Interactive Financial Dashboards", color=[200, 255, 200])
    dpg.add_text("Powered by Plotly - Opens in Browser", color=[150, 150, 150])
    dpg.add_spacer(height=20)
    
    # Interactive chart buttons
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="📊 Stock Dashboard",
            callback=lambda: open_stock_dashboard_enhanced(),
            width=180, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="📋 Portfolio Analysis",
            callback=lambda: open_portfolio_analysis_enhanced(),
            width=180, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="🔬 Correlation Matrix",
            callback=lambda: open_correlation_analysis(),
            width=180, height=50
        )
    
    dpg.add_spacer(height=30)
    
    # Instructions
    dpg.add_text("Features:", color=[200, 200, 255])
    dpg.add_text("• Fully interactive charts with zoom, pan, and hover", color=[150, 150, 150])
    dpg.add_text("• Multiple timeframes and technical indicators", color=[150, 150, 150])
    dpg.add_text("• Export capabilities (PNG, HTML, PDF)", color=[150, 150, 150])
    dpg.add_text("• Real-time data integration ready", color=[150, 150, 150])
    
def open_stock_dashboard_enhanced():
    """Open enhanced stock dashboard"""
    try:
        plotly_helper = PlotlyInteractiveIntegration()
        filepath = plotly_helper.create_stock_dashboard("AAPL")
        plotly_helper.open_in_browser(filepath)
        print(f"Opened enhanced stock dashboard: {filepath}")
    except Exception as e:
        print(f"Error opening stock dashboard: {e}")

def open_portfolio_analysis_enhanced():
    """Open portfolio analysis"""
    try:
        plotly_helper = PlotlyInteractiveIntegration()
        filepath = plotly_helper.create_portfolio_analysis()
        plotly_helper.open_in_browser(filepath)
        print(f"Opened portfolio analysis: {filepath}")
    except Exception as e:
        print(f"Error opening portfolio analysis: {e}")
    

def open_correlation_analysis():
    """Open correlation analysis"""
    try:
        plotly_helper = PlotlyInteractiveIntegration()
        
        # Create correlation-focused analysis
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Generate correlation matrix
        stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA']
        np.random.seed(42)
        returns_data = np.random.multivariate_normal(
            mean=[0.1] * len(stocks),
            cov=np.random.rand(len(stocks), len(stocks)) * 0.01 + np.eye(len(stocks)) * 0.02,
            size=252
        )
        
        corr_matrix = np.corrcoef(returns_data.T)
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=stocks,
            y=stocks,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Stock Correlation Matrix",
            xaxis_title="Stocks",
            yaxis_title="Stocks",
            width=800,
            height=600
        )
        
        filepath = plotly_helper._save_interactive_plot(fig, "correlation_analysis")
        plotly_helper.open_in_browser(filepath)
        print(f"Opened correlation analysis: {filepath}")
    except Exception as e:
        print(f"Error opening correlation analysis: {e}")