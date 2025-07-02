# pages/enhanced_main_graph_page.py

import dearpygui.dearpygui as dpg
import math
import random
import time
import pandas as pd
import numpy as np

from utils import constants
from utils.matplotlib_integration import DPGMatplotlibIntegration, create_stock_analysis_page
from utils.plotly_integration import PlotlyInteractiveIntegration, create_interactive_charts_page

# Global variables
current_stock_line_tag = None
matplotlib_helper = None
plotly_helper = None

def create_enhanced_main_graph(parent_tag):
    """
    Enhanced version of main graph page with advanced chart options
    """
    global matplotlib_helper, plotly_helper
    
    print(f"Creating enhanced graph content in parent: {parent_tag}")
    
    # Initialize helpers
    matplotlib_helper = DPGMatplotlibIntegration()
    plotly_helper = PlotlyInteractiveIntegration()
    
    # Create unique identifier for this instance
    timestamp = str(int(time.time() * 1000))
    
    # Create a main container with tabs for different chart types
    main_container_tag = f"enhanced_main_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, tag=main_container_tag, no_scrollbar=False):
        
        # Title
        dpg.add_text("Advanced Stock Analysis Dashboard", color=[255, 255, 255])
        dpg.add_separator()
        dpg.add_spacer(height=10)
        
        # Create tab bar for different chart types
        with dpg.tab_bar(tag=f"chart_tabs_{timestamp}"):
            
            # Tab 1: Original DPG charts
            with dpg.tab(label="📊 DPG Charts"):
                create_original_dpg_charts(f"chart_tabs_{timestamp}", timestamp)
            
            # Tab 2: Advanced Pandas/Matplotlib charts
            with dpg.tab(label="📈 Advanced Analysis"):
                create_advanced_analysis_tab(f"chart_tabs_{timestamp}", timestamp)
            
            # Tab 3: Interactive Plotly charts
            with dpg.tab(label="🔬 Interactive Charts"):
                create_interactive_tab(f"chart_tabs_{timestamp}", timestamp)
            
            # Tab 4: Sankey Analysis
            with dpg.tab(label="💰 Flow Analysis"):
                create_sankey_tab(f"chart_tabs_{timestamp}", timestamp)

def create_original_dpg_charts(parent_tag, timestamp):
    """Original DPG charts (from your existing code)"""
    global current_stock_line_tag
    
    dpg.add_spacer(height=20)
    
    # Generate demo data for the graph
    x_data = list(range(50))
    y_data = []
    base_price = 100
    for i in range(50):
        change = random.uniform(-2, 2)
        base_price += change
        y_data.append(max(80, min(120, base_price)))
    
    # Create the plot with unique tags
    plot_tag = f"plot_{timestamp}"
    x_axis_tag = f"x_axis_{timestamp}"
    y_axis_tag = f"y_axis_{timestamp}"
    line_tag = f"stock_line_{timestamp}"
    graph_container_tag = f"graph_container_{timestamp}"
    
    # Use a group to contain the plot
    with dpg.group():
        with dpg.child_window(width=-1, height=300, tag=graph_container_tag, border=True):
            with dpg.plot(label="", height=-1, width=-1, tag=plot_tag, no_title=True):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag=x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag=y_axis_tag)
                dpg.add_line_series(x_data, y_data, label="AAPL Stock Price", parent=y_axis_tag, tag=line_tag)
                dpg.set_axis_limits(x_axis_tag, 0, 50)
                dpg.set_axis_limits(y_axis_tag, 80, 120)

    current_stock_line_tag = line_tag
    
    # Control buttons
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        # Green theme for add button
        with dpg.theme(tag=f"green_button_theme_{timestamp}"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 128, 0, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 180, 0, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 100, 0, 255])
        
        # Red theme for heart button
        with dpg.theme(tag=f"red_button_theme_{timestamp}"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [128, 0, 0, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [180, 0, 0, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 0, 0, 255])

        add_button_tag = f"add_stock_button_{timestamp}"
        fav_button_tag = f"add_fav_stock_button_{timestamp}"
        
        dpg.add_button(tag=add_button_tag, label=constants.ICON_PLUS, width=30, height=30, callback=plus_button_callback)
        dpg.bind_item_font(add_button_tag, constants.font_awesome_icon_font_id)
        dpg.bind_item_theme(add_button_tag, f"green_button_theme_{timestamp}")
        
        dpg.add_button(tag=fav_button_tag, label=constants.ICON_HEART, width=30, height=30, callback=fav_button_callback)
        dpg.bind_item_font(fav_button_tag, constants.font_awesome_icon_font_id)
        dpg.bind_item_theme(fav_button_tag, f"red_button_theme_{timestamp}")
        
        dpg.add_spacer(width=20)
        dpg.add_button(label="Refresh Data", callback=refresh_data, width=120)

def create_advanced_analysis_tab(parent_tag, timestamp):
    """Advanced analysis with pandas and matplotlib"""
    global matplotlib_helper
    
    dpg.add_spacer(height=20)
    dpg.add_text("Advanced Financial Analysis", color=[200, 200, 255])
    dpg.add_text("Powered by Pandas & Matplotlib", color=[150, 150, 150])
    dpg.add_spacer(height=10)
    
    # Control buttons
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="📊 Generate Advanced Charts",
            callback=lambda: generate_advanced_charts(parent_tag, timestamp),
            width=250, height=40
        )
        dpg.add_spacer(width=20)
        dpg.add_button(
            label="📈 Timeframe Analysis",
            callback=lambda: generate_timeframe_analysis(parent_tag, timestamp),
            width=200, height=40
        )
    
    dpg.add_spacer(height=20)
    
    # Container for generated charts
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    with dpg.child_window(width=-1, height=-1, tag=chart_container_tag, border=False):
        dpg.add_text("Click the buttons above to generate advanced analysis charts", 
                    color=[150, 150, 150])

def create_interactive_tab(parent_tag, timestamp):
    """Interactive charts tab"""
    global plotly_helper
    
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

def create_sankey_tab(parent_tag, timestamp):
    """Sankey flow analysis tab"""
    global plotly_helper
    
    dpg.add_spacer(height=20)
    dpg.add_text("Financial Flow Analysis", color=[255, 200, 100])
    dpg.add_text("Sankey Diagrams for Cash Flow & Portfolio Analysis", color=[150, 150, 150])
    dpg.add_spacer(height=20)
    
    # Sankey options
    with dpg.group(horizontal=True):
        dpg.add_button(
            label="💰 Cash Flow Analysis",
            callback=lambda: open_cashflow_sankey(),
            width=200, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="🏦 Revenue Breakdown",
            callback=lambda: open_revenue_sankey(),
            width=200, height=50
        )
        
        dpg.add_spacer(width=15)
        
        dpg.add_button(
            label="📊 Asset Allocation",
            callback=lambda: open_asset_allocation_sankey(),
            width=200, height=50
        )
    
    dpg.add_spacer(height=30)
    
    # Sample data display
    dpg.add_text("Sample Financial Flow Structure:", color=[200, 200, 255])
    
    with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, 
                   borders_innerV=True, borders_outerV=True, height=200):
        dpg.add_table_column(label="Source", width_fixed=True, init_width_or_weight=150)
        dpg.add_table_column(label="Target", width_fixed=True, init_width_or_weight=150)
        dpg.add_table_column(label="Amount ($M)", width_fixed=True, init_width_or_weight=100)
        
        flows = [
            ("Revenue", "Operating Expenses", "800"),
            ("Revenue", "Net Income", "200"),
            ("Operating Expenses", "COGS", "400"),
            ("Operating Expenses", "SG&A", "250"),
            ("Operating Expenses", "R&D", "150"),
            ("Net Income", "Retained Earnings", "120"),
            ("Net Income", "Dividends", "80")
        ]
        
        for source, target, amount in flows:
            with dpg.table_row():
                dpg.add_text(source)
                dpg.add_text(target)
                dpg.add_text(amount, color=[150, 255, 150])

# Callback functions
def plus_button_callback():
    """Callback for the plus button"""
    print("Plus button clicked!")

def fav_button_callback():
    """Callback for the heart button"""
    print("Heart button clicked!")

def refresh_data():
    """Refresh the graph data"""
    global current_stock_line_tag
    print("Refreshing stock data...")
    
    # Generate new data
    x_data = list(range(50))
    y_data = []
    base_price = random.uniform(90, 110)
    for i in range(50):
        change = random.uniform(-2, 2)
        base_price += change
        y_data.append(max(80, min(120, base_price)))
    
    # Update the line series
    if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
        dpg.set_value(current_stock_line_tag, [x_data, y_data])
        print("Graph data refreshed!")
    else:
        print("Graph not found for refresh")

def generate_advanced_charts(parent_tag, timestamp):
    """Generate advanced matplotlib charts"""
    global matplotlib_helper
    
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    
    # Clear existing content
    if dpg.does_item_exist(chart_container_tag):
        dpg.delete_item(chart_container_tag, children_only=True)
    
    # Generate new charts
    dpg.add_text("Generating advanced analysis...", parent=chart_container_tag, color=[255, 255, 0])
    
    # Create advanced pandas chart
    matplotlib_helper.create_advanced_pandas_chart(chart_container_tag, width=1000, height=600)
    
    dpg.add_spacer(height=20, parent=chart_container_tag)
    dpg.add_button(label="Refresh Charts", 
                  callback=lambda: generate_advanced_charts(parent_tag, timestamp),
                  parent=chart_container_tag)

def generate_timeframe_analysis(parent_tag, timestamp):
    """Generate timeframe-specific analysis"""
    global matplotlib_helper
    
    chart_container_tag = f"advanced_charts_container_{timestamp}"
    
    # Clear existing content
    if dpg.does_item_exist(chart_container_tag):
        dpg.delete_item(chart_container_tag, children_only=True)
    
    # Create sample timeframe data
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'price': 100 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, len(dates))))
    })
    
    # Generate timeframe chart
    matplotlib_helper.create_pandas_timeframe_chart(sample_data, chart_container_tag, width=1000, height=400)
    
    dpg.add_spacer(height=20, parent=chart_container_tag)
    dpg.add_text("Timeframe Analysis Complete", parent=chart_container_tag, color=[0, 255, 0])

def open_stock_dashboard_enhanced():
    """Open enhanced stock dashboard"""
    global plotly_helper
    filepath = plotly_helper.create_stock_dashboard("AAPL")
    plotly_helper.open_in_browser(filepath)
    print(f"Opened enhanced stock dashboard: {filepath}")

def open_portfolio_analysis_enhanced():
    """Open portfolio analysis"""
    global plotly_helper
    filepath = plotly_helper.create_portfolio_analysis()
    plotly_helper.open_in_browser(filepath)
    print(f"Opened portfolio analysis: {filepath}")

def open_correlation_analysis():
    """Open correlation analysis"""
    global plotly_helper
    
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

def open_cashflow_sankey():
    """Open cash flow Sankey diagram"""
    global plotly_helper
    filepath = plotly_helper.create_interactive_sankey()
    plotly_helper.open_in_browser(filepath)
    print(f"Opened cash flow Sankey: {filepath}")

def open_revenue_sankey():
    """Open revenue breakdown Sankey"""
    global plotly_helper
    
    # Custom revenue data
    revenue_data = {
        'labels': [
            'Total Revenue', 'Product Sales', 'Services', 'Subscriptions',
            'North America', 'Europe', 'Asia Pacific', 'Other',
            'Enterprise', 'Consumer', 'Government'
        ],
        'sources': [0, 0, 0, 1, 1, 1, 1, 2, 2, 2],
        'targets': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'values': [700, 200, 100, 300, 250, 100, 50, 120, 60, 20]
    }
    
    filepath = plotly_helper.create_interactive_sankey(revenue_data)
    plotly_helper.open_in_browser(filepath)
    print(f"Opened revenue Sankey: {filepath}")

def open_asset_allocation_sankey():
    """Open asset allocation Sankey"""
    global plotly_helper
    
    # Asset allocation data
    asset_data = {
        'labels': [
            'Portfolio', 'Equities', 'Bonds', 'Alternatives',
            'US Stocks', 'International', 'Emerging Markets',
            'Government Bonds', 'Corporate Bonds', 'REITs', 'Commodities'
        ],
        'sources': [0, 0, 0, 1, 1, 1, 2, 2, 3, 3],
        'targets': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'values': [600, 300, 100, 350, 150, 100, 200, 100, 60, 40]
    }
    
    filepath = plotly_helper.create_interactive_sankey(asset_data)
    plotly_helper.open_in_browser(filepath)
    print(f"Opened asset allocation Sankey: {filepath}")

# Cleanup function
def cleanup_chart_helpers():
    """Clean up chart helpers"""
    global matplotlib_helper, plotly_helper
    
    if matplotlib_helper:
        matplotlib_helper.cleanup()
    if plotly_helper:
        plotly_helper.cleanup()

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    cleanup_chart_helpers()
    from .content_container import show_page
    show_page("welcome")