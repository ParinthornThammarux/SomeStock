import dearpygui.dearpygui as dpg
import json
import os

stock_data = None
chart_tags = {}

from utils.stockdex_layer import fetch_data_from_stockdx
from components.stock_tag import add_stock_tag

def load_stock_data():
    """Load stock data from JSON file on startup"""
    global stock_data
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir) 
        json_path = os.path.join(project_root, 'utils', 'stock_data.json')
        
        print(f"Looking for JSON at: {json_path}")  # Debug line
        
        with open(json_path, 'r', encoding='utf-8') as f:
            stock_data = json.load(f)
        print(f"✅ Loaded {stock_data['metadata']['total_stocks']} stocks")
    except Exception as e:
        print(f"Error loading stock data: {e}")
        stock_data = None

def create_stock_search(line_tag, x_axis_tag, y_axis_tag, plot_tag):
    
    # Check if popup already exists and delete it
    if dpg.does_item_exist("stock_search_popup"):
        dpg.delete_item("stock_search_popup")
    
    # Use global chart_tags
    global chart_tags
    
    # Store the tags for use in callbacks
    chart_tags = {
        'line_tag': line_tag,
        'x_axis_tag': x_axis_tag,
        'y_axis_tag': y_axis_tag,
        'plot_tag': plot_tag
    }
    
    # Get mouse position
    mouse_pos = dpg.get_mouse_pos()
    
    # Create small popup window near mouse
    with dpg.window(
        label="Stock Search",
        tag="stock_search_popup",
        width=550,
        height=600,
        pos=[mouse_pos[0] + 10, mouse_pos[1] + 10],
        no_resize=True,
        no_collapse=True,
        modal=True,
        popup=True
    ):
        dpg.add_text("Input Stock Symbol or Stock Name")
        dpg.add_separator()
        dpg.add_spacer(height=3)
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag='stock_name', hint="ie. AAPL, TSLA", width=280, callback=typing_callback)
            dpg.add_text("Click on stock to search", color=[242, 226, 5])
        # Table with 4 columns
        with dpg.table(header_row=True, tag="stock_results_table", borders_innerH=True, borders_outerH=True, 
                    borders_innerV=True, borders_outerV=True, height=-1):
            dpg.add_table_column(label="Symbol", width_fixed=False, init_width_or_weight=70)
            dpg.add_table_column(label="Company Name", width_fixed=False, init_width_or_weight=160, width_stretch=True)
            dpg.add_table_column(label="Industry", width_fixed=False, init_width_or_weight=100)
            dpg.add_table_column(label="Market Cap", width_fixed=False, init_width_or_weight=100)

        dpg.add_button(label="Search", width=60, callback=search_callback)

def search_callback():
    symbol = dpg.get_value('stock_name')
    print(f"Searching for: {symbol}")
    # Close the popup
    if dpg.does_item_exist("stock_search_popup"):
        dpg.delete_item("stock_search_popup")

def create_table_button_theme():
    """Create a theme that makes buttons look like normal table text"""
    with dpg.theme(tag="table_button_theme"):
        with dpg.theme_component(dpg.mvButton):
            # Remove button background and borders
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])           # Transparent background
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [40, 40, 40, 100])  # Subtle hover
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [60, 60, 60, 150])   # Subtle click
            
            # Remove button border
            dpg.add_theme_color(dpg.mvThemeCol_Border, [0, 0, 0, 0])
            
            # Set text color to match normal table text
            dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 255, 255])
            
            # Remove padding and rounding
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 2, 2)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0)
            
def typing_callback():
    search_term = dpg.get_value('stock_name').upper().strip()
    # Clear existing table rows
    clear_table_rows("stock_results_table")
    
    if not search_term or not stock_data:
        return
    
    matching_stocks = []
    
    # First: Search by symbol using index
    if search_term in stock_data['search_index']:
        matching_stocks = stock_data['search_index'][search_term]
    else:
        # Fallback: manual search in stocks array for symbols
        for stock in stock_data['stocks']:
            if stock['symbol'].upper().startswith(search_term):
                matching_stocks.append(stock)
    
    # Second: Search by company name (manual search)
    name_matches = []
    
    # remove cuz laggy
    for stock in stock_data['stocks']:
        company_name = stock['company_name'].upper()
        # Check if company name contains the search term
        if company_name.startswith(search_term):
            # Avoid duplicates (in case symbol and name both match)
            if stock not in matching_stocks:
                name_matches.append(stock)
    
    # Combine results - symbol matches first, then name matches
    all_matches = matching_stocks + name_matches
    
    if not dpg.does_item_exist("table_button_theme"):
        create_table_button_theme()
        
    # Populate table with results
    for stock in all_matches:
        with dpg.table_row(parent="stock_results_table"):
            symbol_button = dpg.add_button(
                label=stock['symbol'], 
                callback=lambda s, a, u: row_clicked(u), 
                user_data=stock, 
                width=-1, 
                height=20
            )
            name_button = dpg.add_button(
                label=stock['company_name'], 
                callback=lambda s, a, u: row_clicked(u), 
                user_data=stock, 
                width=-1, 
                height=20
            )
            industry_button = dpg.add_button(
                label=stock['industry'], 
                callback=lambda s, a, u: row_clicked(u), 
                user_data=stock, 
                width=-1, 
                height=20
            )
            cap_button = dpg.add_button(
                label=stock['market_cap'], 
                callback=lambda s, a, u: row_clicked(u), 
                user_data=stock, 
                width=-1, 
                height=20
            )
            dpg.bind_item_theme(symbol_button, "table_button_theme")
            dpg.bind_item_theme(name_button, "table_button_theme")
            dpg.bind_item_theme(industry_button, "table_button_theme")
            dpg.bind_item_theme(cap_button, "table_button_theme")

            
def row_clicked(stock_data):
    #print(f"Selected stock: {stock_data['symbol']} - {stock_data['company_name']}")
    add_stock_tag(stock_data['symbol'],stock_data['company_name'])
    if dpg.does_item_exist("stock_search_popup"):
        dpg.delete_item("stock_search_popup")
        
    # fetch and display data (move to inside create stock tag?)
    fetch_data_from_stockdx(
        stock_data['symbol'],
        chart_tags['line_tag'],
        chart_tags['x_axis_tag'],
        chart_tags['y_axis_tag'],
        chart_tags['plot_tag']
    )
    
def clear_table_rows(table_tag):
    """Clear all rows from a table while keeping headers"""
    if dpg.does_item_exist(table_tag):
        # Get all children of the table
        children = dpg.get_item_children(table_tag, slot=1)  # slot 1 = table rows
        if children:
            for child in children:
                if dpg.get_item_type(child) == "mvAppItemType::mvTableRow":
                    dpg.delete_item(child)
