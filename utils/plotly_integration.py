# utils/plotly_integration.py

import dearpygui.dearpygui as dpg
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import pandas as pd
import numpy as np
import webbrowser
import tempfile
import os
from pathlib import Path

class PlotlyInteractiveIntegration:
    """
    Integration for interactive Plotly charts
    Creates HTML files that can be opened in browser or embedded
    """
    
    def __init__(self):
        self.html_files = []
        self.temp_dir = tempfile.mkdtemp()
    
    def create_interactive_sankey(self, source_data=None):
        """
        Create interactive Sankey diagram based on stockdex pattern
        Similar to: https://github.com/ahnazary/stockdex
        """
        if source_data is None:
            # Demo financial flow data
            source_data = {
                'labels': [
                    'Revenue', 'Operating Revenue', 'Non-Operating Revenue',
                    'Operating Expenses', 'COGS', 'SG&A', 'R&D',
                    'Operating Income', 'Interest Expense', 'Taxes',
                    'Net Income', 'Retained Earnings', 'Dividends'
                ],
                'sources': [0, 0, 1, 1, 3, 3, 3, 7, 7, 8, 10, 10],
                'targets': [1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11, 12],
                'values': [1000, 50, 800, 200, 400, 250, 150, 50, 30, 170, 120, 50]
            }
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=source_data['labels'],
                color=[
                    "lightblue", "lightgreen", "lightcoral",
                    "lightyellow", "lightpink", "lightgray", "lightcyan",
                    "lightseagreen", "lightgoldenrodyellow", "lightsteelblue",
                    "lightslategray", "lightgreen", "lightcoral"
                ]
            ),
            link=dict(
                source=source_data['sources'],
                target=source_data['targets'],
                value=source_data['values'],
                color=[f"rgba(100, 150, 200, 0.3)" for _ in source_data['values']]
            )
        )])
        
        fig.update_layout(
            title={
                'text': "Company Financial Flow Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            font_size=12,
            width=1200,
            height=700,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        
        return self._save_interactive_plot(fig, "sankey_analysis")
    
    def create_stock_dashboard(self, ticker="AAPL"):
        """
        Create comprehensive stock analysis dashboard
        """
        # Generate sample data
        dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
        np.random.seed(42)
        
        # Stock price data
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        volume = np.random.lognormal(10, 1, len(dates))
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': volume,
            'returns': returns
        })
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Stock Price with Moving Averages', 'Volume Analysis',
                'Returns Distribution', 'Volatility Analysis',
                'Price vs Volume Correlation', 'Performance Metrics'
            ),
            specs=[
                [{"colspan": 2}, None],
                [{}, {}],
                [{}, {}]
            ]
        )
        
        # Price chart with moving averages
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['price'], name='Price', line=dict(width=1)),
            row=1, col=1
        )
        
        ma_20 = df['price'].rolling(20).mean()
        ma_50 = df['price'].rolling(50).mean()
        
        fig.add_trace(
            go.Scatter(x=df['date'], y=ma_20, name='20-day MA', line=dict(width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['date'], y=ma_50, name='50-day MA', line=dict(width=2)),
            row=1, col=1
        )
        
        # Volume chart
        fig.add_trace(
            go.Bar(x=df['date'], y=df['volume'], name='Volume', showlegend=False),
            row=2, col=1
        )
        
        # Returns histogram
        fig.add_trace(
            go.Histogram(x=df['returns'], name='Returns', nbinsx=50, showlegend=False),
            row=2, col=2
        )
        
        # Rolling volatility
        rolling_vol = df['returns'].rolling(30).std() * np.sqrt(252)
        fig.add_trace(
            go.Scatter(x=df['date'], y=rolling_vol, name='30-day Volatility', showlegend=False),
            row=3, col=1
        )
        
        # Price vs Volume scatter
        fig.add_trace(
            go.Scatter(x=df['volume'], y=df['price'], mode='markers', 
                      name='Price vs Volume', showlegend=False),
            row=3, col=2
        )
        
        fig.update_layout(
            title=f"{ticker} Stock Analysis Dashboard",
            height=900,
            width=1400,
            showlegend=True
        )
        
        return self._save_interactive_plot(fig, f"stock_dashboard_{ticker}")
    
    def create_portfolio_analysis(self):
        """
        Create portfolio analysis with multiple stocks
        """
        # Sample portfolio data
        stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        returns = [0.15, 0.12, 0.18, 0.08, 0.25]
        volatility = [0.25, 0.28, 0.22, 0.35, 0.45]
        
        # Create efficient frontier plot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Portfolio Allocation', 'Risk-Return Profile',
                'Correlation Matrix', 'Performance Attribution'
            )
        )
        
        # Portfolio pie chart
        fig.add_trace(
            go.Pie(labels=stocks, values=weights, name="Portfolio"),
            row=1, col=1
        )
        
        # Risk-return scatter
        fig.add_trace(
            go.Scatter(
                x=volatility, y=returns, mode='markers+text',
                text=stocks, textposition="top center",
                marker=dict(size=[w*1000 for w in weights], color=returns, colorscale='Viridis'),
                name="Stocks"
            ),
            row=1, col=2
        )
        
        # Generate correlation matrix
        np.random.seed(42)
        corr_matrix = np.random.rand(5, 5)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2
        np.fill_diagonal(corr_matrix, 1)
        
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix,
                x=stocks, y=stocks,
                colorscale='RdBu',
                zmid=0
            ),
            row=2, col=1
        )
        
        # Performance attribution
        attribution = [r * w for r, w in zip(returns, weights)]
        fig.add_trace(
            go.Bar(x=stocks, y=attribution, name="Contribution"),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Portfolio Analysis Dashboard",
            height=800,
            width=1200
        )
        
        return self._save_interactive_plot(fig, "portfolio_analysis")
    
    def _save_interactive_plot(self, fig, filename):
        """Save plotly figure as interactive HTML"""
        filepath = os.path.join(self.temp_dir, f"{filename}.html")
        
        # Configure plotly for better interactivity
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
        }
        
        pyo.plot(fig, filename=filepath, auto_open=False, config=config)
        self.html_files.append(filepath)
        
        return filepath
    
    def open_in_browser(self, filepath):
        """Open HTML file in default browser"""
        webbrowser.open(f"file://{os.path.abspath(filepath)}")
    
    def cleanup(self):
        """Clean up temporary files"""
        for html_file in self.html_files:
            try:
                if os.path.exists(html_file):
                    os.unlink(html_file)
            except Exception as e:
                print(f"Error cleaning up {html_file}: {e}")

# DPG Integration functions
def create_interactive_charts_page(parent_tag):
    """Create page with interactive chart options"""
    
    plotly_helper = PlotlyInteractiveIntegration()
    
    dpg.add_text("Interactive Financial Analysis", parent=parent_tag, color=[255, 255, 255])
    dpg.add_separator(parent=parent_tag)
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Chart selection buttons
    with dpg.group(horizontal=True, parent=parent_tag):
        dpg.add_button(
            label="📊 Interactive Sankey",
            callback=lambda: open_sankey_chart(plotly_helper),
            width=200, height=50
        )
        
        dpg.add_spacer(width=20)
        
        dpg.add_button(
            label="📈 Stock Dashboard",
            callback=lambda: open_stock_dashboard(plotly_helper),
            width=200, height=50
        )
        
        dpg.add_spacer(width=20)
        
        dpg.add_button(
            label="📋 Portfolio Analysis",
            callback=lambda: open_portfolio_analysis(plotly_helper),
            width=200, height=50
        )
    
    dpg.add_spacer(height=30, parent=parent_tag)
    
    # Instructions
    dpg.add_text("Instructions:", parent=parent_tag, color=[200, 200, 255])
    dpg.add_text("• Click any button above to open interactive charts in your browser", parent=parent_tag)
    dpg.add_text("• Charts are fully interactive with zoom, pan, and hover features", parent=parent_tag)
    dpg.add_text("• Based on financial analysis patterns from stockdex", parent=parent_tag)
    
    # Store helper for cleanup
    if not hasattr(dpg, '_plotly_helpers'):
        dpg._plotly_helpers = []
    dpg._plotly_helpers.append(plotly_helper)

def open_sankey_chart(plotly_helper):
    """Open interactive Sankey chart"""
    filepath = plotly_helper.create_interactive_sankey()
    plotly_helper.open_in_browser(filepath)
    print(f"Opened Sankey chart: {filepath}")

def open_stock_dashboard(plotly_helper):
    """Open stock analysis dashboard"""
    filepath = plotly_helper.create_stock_dashboard("AAPL")
    plotly_helper.open_in_browser(filepath)
    print(f"Opened stock dashboard: {filepath}")

def open_portfolio_analysis(plotly_helper):
    """Open portfolio analysis"""
    filepath = plotly_helper.create_portfolio_analysis()
    plotly_helper.open_in_browser(filepath)
    print(f"Opened portfolio analysis: {filepath}")