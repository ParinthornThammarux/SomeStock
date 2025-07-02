# components/main_graph_page.py

import dearpygui.dearpygui as dpg
import math
import random

def create_main_graph(parent_tag):
    """
    Creates a content page with a graph on top and a table below with demo data.
    """
    print(f"Creating graph and table content in parent: {parent_tag}")
    
    # Add some padding from the top
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Main container
    with dpg.group(horizontal=False, parent=parent_tag):
        dpg.add_text("Stock Analysis Dashboard", color=[255, 255, 255], parent=parent_tag)
        dpg.add_separator(parent=parent_tag)
        dpg.add_spacer(height=10, parent=parent_tag)
        
        # TOP BOX - Graph
        with dpg.child_window(width=-1, height=350, parent=parent_tag, tag="graph_container"):
            dpg.add_text("Stock Price Chart", color=[200, 200, 255])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Generate demo data for the graph
            x_data = list(range(50))
            y_data = []
            base_price = 100
            for i in range(50):
                # Simulate stock price movement
                change = random.uniform(-2, 2)
                base_price += change
                y_data.append(max(80, min(120, base_price)))  # Keep price between 80-120
            
            # Create the plot
            with dpg.plot(label="Stock Price Over Time", height=280, width=-20):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag="y_axis")
                
                # Add the line series
                dpg.add_line_series(x_data, y_data, label="AAPL Stock Price", parent="y_axis", tag="stock_line")
                
                # Set axis limits
                dpg.set_axis_limits("x_axis", 0, 50)
                dpg.set_axis_limits("y_axis", 80, 120)
        
        dpg.add_spacer(height=10, parent=parent_tag)
        
        # BOTTOM BOX - Table
        with dpg.child_window(width=-1, height=-50, parent=parent_tag, tag="table_container"):
            dpg.add_text("Stock Portfolio Data", color=[200, 255, 200])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Create table with demo data
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, 
                          borders_innerV=True, borders_outerV=True, tag="portfolio_table"):
                
                # Table headers
                dpg.add_table_column(label="Symbol", width_fixed=True, init_width_or_weight=80)
                dpg.add_table_column(label="Company", width_fixed=True, init_width_or_weight=200)
                dpg.add_table_column(label="Price", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Change", width_fixed=True, init_width_or_weight=100)
                dpg.add_table_column(label="Volume", width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column(label="Market Cap", width_fixed=True, init_width_or_weight=130)
                
                # Demo data rows
                demo_stocks = [
                    ("AAPL", "Apple Inc.", 175.43, 2.15, "64.2M", "2.75T"),
                    ("GOOGL", "Alphabet Inc.", 2431.50, -15.23, "1.2M", "1.63T"),
                    ("MSFT", "Microsoft Corp.", 338.25, 5.67, "23.1M", "2.52T"),
                    ("AMZN", "Amazon.com Inc.", 3102.97, -45.12, "3.8M", "1.57T"),
                    ("TSLA", "Tesla Inc.", 248.50, 12.34, "89.5M", "789B"),
                    ("META", "Meta Platforms", 297.55, -8.91, "18.7M", "754B"),
                    ("NVDA", "NVIDIA Corp.", 421.13, 18.76, "45.2M", "1.04T"),
                    ("NFLX", "Netflix Inc.", 384.29, -2.45, "8.9M", "171B"),
                    ("CRM", "Salesforce Inc.", 198.76, 4.23, "5.6M", "196B"),
                    ("PYPL", "PayPal Holdings", 62.85, -1.78, "12.3M", "70.8B")
                ]
                
                for symbol, company, price, change, volume, market_cap in demo_stocks:
                    with dpg.table_row():
                        dpg.add_text(symbol)
                        dpg.add_text(company)
                        dpg.add_text(f"${price:.2f}")
                        
                        # Color code the change (green for positive, red for negative)
                        change_color = [0, 255, 0] if change >= 0 else [255, 0, 0]
                        change_text = f"+${change:.2f}" if change >= 0 else f"-${abs(change):.2f}"
                        dpg.add_text(change_text, color=change_color)
                        
                        dpg.add_text(volume)
                        dpg.add_text(market_cap)
        
        # Add some action buttons at the bottom
        dpg.add_spacer(height=10, parent=parent_tag)
        with dpg.group(horizontal=True, parent=parent_tag):
            dpg.add_button(label="Refresh Data", callback=refresh_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Export CSV", callback=export_data, width=120)
            dpg.add_spacer(width=10)
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

def refresh_data():
    """Refresh the graph and table data"""
    print("Refreshing stock data...")
    
    # Regenerate graph data
    x_data = list(range(50))
    y_data = []
    base_price = random.uniform(90, 110)
    for i in range(50):
        change = random.uniform(-2, 2)
        base_price += change
        y_data.append(max(80, min(120, base_price)))
    
    # Update the line series
    if dpg.does_item_exist("stock_line"):
        dpg.set_value("stock_line", [x_data, y_data])
    
    print("Data refreshed!")

def export_data():
    """Simulate data export"""
    print("Exporting portfolio data to CSV...")
    # In a real application, you would export the table data to a CSV file
    dpg.add_text("Data exported successfully!", color=[0, 255, 0], parent="table_container")

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from .content_container import show_page
    show_page("welcome")

# Keep the old function for backward compatibility
def create_graph_table_page(parent_tag):
    """Legacy function - redirects to new system"""
    return create_graph_table_content(parent_tag)