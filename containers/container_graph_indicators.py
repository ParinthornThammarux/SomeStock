# containers/graph_tabs_container.py

# This acts as a container for all the graph types tabs 
import dearpygui.dearpygui as dpg
import random
import time

from components.stock.stock_data_manager import create_stock_tag, get_all_active_tags, get_favorited_stocks, find_tag_by_symbol,restore_tags_to_container
from components.stock_search import create_stock_search
from utils import constants
from utils.matplotlib_integration import DPGMatplotlibIntegration
from utils.plotly_integration import PlotlyInteractiveIntegration

# Import them from relative files
from components.graph.graph_price import create_price_chart_for_stock
from components.graph.graph_rsi import create_rsi_chart_for_stock

# Global variables
matplotlib_helper = None
plotly_helper = None
chart_tabs_tag = None
from utils.constants import active_indicator_buttons

def create_graph_indicators(parent_tag):
    """
    container for showing multiple graph indicator types
    """
    global matplotlib_helper, plotly_helper
    
    print(f"Creating enhanced graph content in parent: {parent_tag}")
    
    # Initialize helpers
    try:
        matplotlib_helper = DPGMatplotlibIntegration()
        plotly_helper = PlotlyInteractiveIntegration()
    except Exception as e:
        print(f"Warning: Could not initialize chart helpers: {e}")
        matplotlib_helper = None
        plotly_helper = None
    
    # Create unique identifier for this instance
    timestamp = str(int(time.time() * 1000))
    
    # Create unique tags to avoid conflicts
    main_container_tag = f"enhanced_main_container_{timestamp}"
    global chart_tabs_tag
    chart_tabs_tag = f"chart_tabs_{timestamp}"
    
    # Check if container already exists and delete it
    if dpg.does_item_exist(main_container_tag):
        dpg.delete_item(main_container_tag)
    
    try:
        create_indicator_button_themes()
        with dpg.child_window(
            width=-1, 
            height=-1, 
            parent=parent_tag, 
            tag=main_container_tag, 
            no_scrollbar=False,
            border=False
        ):
            
            # Title
            dpg.add_text("Advanced Stock Analysis Dashboard", color=[255, 255, 255],indent=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_text("Active Stocks", color=[255, 255, 255],indent=5)
            dpg.add_spacer(height=5)


            # Stock tags container
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True, tag='stock_tags_container'):
                        dpg.add_spacer(width=-1)
                restore_tags_to_container('stock_tags_container')
                

                    
                with dpg.group(horizontal=True):
                    # Create themes with unique tags
                    timestamp = str(int(time.time() * 1000))
                    green_theme_tag = f"green_button_theme_{timestamp}"
                    red_theme_tag = f"red_button_theme_{timestamp}"
                    
                    # Only create themes if they don't exist
                    if not dpg.does_item_exist(green_theme_tag):
                        with dpg.theme(tag=green_theme_tag):
                            with dpg.theme_component(dpg.mvButton):
                                dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 128, 0, 255])
                                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 180, 0, 255])
                                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 100, 0, 255])
                    
                    if not dpg.does_item_exist(red_theme_tag):
                        with dpg.theme(tag=red_theme_tag):
                            with dpg.theme_component(dpg.mvButton):
                                dpg.add_theme_color(dpg.mvThemeCol_Button, [128, 0, 0, 255])
                                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [180, 0, 0, 255])
                                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 0, 0, 255])

                    add_stock_btn_tag = f"add_stock_button_{timestamp}"
                    add_fav_btn_tag = f"add_fav_stock_button_{timestamp}"
                    
                    dpg.add_button(tag=add_stock_btn_tag, label=constants.ICON_PLUS, width=30, height=30, callback=plus_button_callback)
                    if constants.font_awesome_icon_font_id:
                        dpg.bind_item_font(add_stock_btn_tag, constants.font_awesome_icon_font_id)
                    dpg.bind_item_theme(add_stock_btn_tag, green_theme_tag)
                    
                    # Heart button
                    dpg.add_button(tag=add_fav_btn_tag, label=constants.ICON_HEART, width=30, height=30, callback=fav_button_callback)
                    if constants.font_awesome_icon_font_id:
                        dpg.bind_item_font(add_fav_btn_tag, constants.font_awesome_icon_font_id)
                    dpg.bind_item_theme(add_fav_btn_tag, red_theme_tag)
                    
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            with dpg.group(indent=10):
                dpg.add_text("Step 1 : Choose active stocks", tag="hint_1")
                dpg.add_text("Step 2 : Pick indicators", tag="hint_2")
                
            # Update the button creation section (around line 92)
            with dpg.group(tag="group_indicators",horizontal=True,indent=5):
                dpg.add_button(tag="rsi_button",label="RSI",callback=lambda: toggle_indicator_button("rsi_button"))
                dpg.add_button(tag="price_button",label="PRICE",callback=lambda: toggle_indicator_button("price_button"))
                dpg.add_button(tag="linear_price_button",label="LINEAR REGRESSION PRICE",callback=lambda: toggle_indicator_button("linear_price_button"))
                
            dpg.bind_item_theme("rsi_button", "indicator_button_inactive_theme")
            dpg.bind_item_theme("price_button", "indicator_button_inactive_theme")
            dpg.bind_item_theme("linear_price_button", "indicator_button_inactive_theme")
            
            #Set initial state
            indicator_activation()

            # Create tab bar for different chart types
            dpg.add_spacer(height=10)
            with dpg.tab_bar(tag=chart_tabs_tag,indent=50):
                print("📈 created empty tab bar")
             
    except Exception as e:
        print(f"Error creating graph tabs container: {e}")
        # Fallback to simple content
        dpg.add_text("Error loading enhanced charts", parent=parent_tag, color=[255, 0, 0])
        dpg.add_text(f"Error details: {str(e)}", parent=parent_tag, color=[255, 100, 100])

def create_indicator_button_themes():
    """Create themes for active/inactive indicator buttons"""
    
    # Inactive theme (grey background, white text)
    if not dpg.does_item_exist("indicator_button_inactive_theme"):
        with dpg.theme(tag="indicator_button_inactive_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [100, 100, 100, 255])           # Grey background
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [120, 120, 120, 255])    # Lighter grey on hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [80, 80, 80, 255])        # Darker grey when clicked
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 255, 255])             # White text
    
    # Active theme (green background, white text)
    if not dpg.does_item_exist("indicator_button_active_theme"):
        with dpg.theme(tag="indicator_button_active_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 150, 0, 255])               # Green background
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 180, 0, 255])        # Brighter green on hover
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 120, 0, 255])         # Darker green when clicked
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 255, 255])    
       
def toggle_indicator_button(button_tag):
    """Toggle indicator button between active/inactive state"""
    global active_indicator_buttons
        
    button_label = dpg.get_item_label(button_tag)
    
    if button_tag in active_indicator_buttons:
        # Button is active, make it inactive
        active_indicator_buttons.remove(button_tag)
        dpg.bind_item_theme(button_tag, "indicator_button_inactive_theme")
        print(f"🔘 {button_label} deactivated")
    else:
        # Button is inactive, make it active
        active_indicator_buttons.add(button_tag)
        dpg.bind_item_theme(button_tag, "indicator_button_active_theme")
        print(f"🟢 {button_label} activated")
    
    if len(active_indicator_buttons) == 0:
        dpg.configure_item("hint_2", show =True)
    else:
        dpg.configure_item("hint_2", show = False)
    populate_chart_tabs()
    print(f"📊 Active indicators: {[dpg.get_item_label(tag) for tag in active_indicator_buttons]}")

def reset_all_indicator_buttons():
    """Reset all indicator buttons to inactive state"""
    global active_indicator_buttons
    
    if dpg.does_item_exist('group_indicators'):
        children = dpg.get_item_children('group_indicators', slot=1)
        if children:
            for child in children:
                if dpg.get_item_type(child) == "mvAppItemType::mvButton":
                    dpg.bind_item_theme(child, "indicator_button_inactive_theme")
                    button_label = dpg.get_item_label(child)
                    print(f"🔘 Reset {button_label} to inactive")

    active_indicator_buttons.clear()
    populate_chart_tabs()
    print("🔄 All indicator buttons reset to inactive")

def populate_chart_tabs():
    """Populate chart tabs based on active indicator buttons and active stocks"""
    global active_indicator_buttons
    global chart_tabs_tag
    
    print(f"🔧 populate_chart_tabs called")
    print(f"📊 Active indicators: {len(active_indicator_buttons)}")
    
    if not chart_tabs_tag or not dpg.does_item_exist(chart_tabs_tag):
        print("❌ Could not find chart tabs container")
        return
    
    # Clear existing tabs
    children = dpg.get_item_children(chart_tabs_tag, 1)
    if children:
        print(f"🧹 Clearing {len(children)} existing tabs")
        for child in children:
            dpg.delete_item(child)
    
    # Get all active stocks
    active_stocks = get_all_active_tags()
    print(f"📊 Active stocks: {len(active_stocks)}")
    
    # Create tabs based on active indicators
    for button_tag in active_indicator_buttons:
        button_label = dpg.get_item_label(button_tag)
        tab_tag = f"{button_label.lower()}_tab"
        
        with dpg.tab(label=f"{button_label} Analysis", tag=tab_tag, parent=chart_tabs_tag):            
            # This should never run!
            if len(active_stocks) == 0:
                # No stocks selected
                dpg.add_text("No stocks selected. Add stocks using the + button above.", 
                           color=[255, 150, 100], indent=20)
            else:
                # Create charts for each active stock
                dpg.add_spacer(height=10)
                # Create a scrollable container for multiple charts
                with dpg.child_window(width=-1, height=-1, border=False, 
                                    tag=f"{button_label.lower()}_charts_container"):
                    
                    #dpg.add_text(f"Analyzing {len(active_stocks)} stock(s) with {button_label}",       color=[150, 255, 150], indent=10)
                    
                    for i, stock_tag in enumerate(active_stocks):
                        symbol = stock_tag.symbol
                        company_name = stock_tag.company_name
                        
                        # Create individual chart container for each stock
                        chart_container_tag = f"{button_label.lower()}_{symbol}_chart"  # Remove timestamp
                        
                        # Stock header
                        with dpg.group(horizontal=True):
                            dpg.add_text(f"{i+1}.{symbol}", color=[255, 255, 255],indent=5)
                            dpg.add_text(f"({company_name})", color=[150, 150, 150])
                                                                                
                        # Placeholder for actual chart components
                        if button_label == "RSI":
                            create_rsi_chart_for_stock(f"{button_label.lower()}_charts_container", symbol)
                        elif button_label == "PRICE":
                            create_price_chart_for_stock(f"{button_label.lower()}_charts_container", symbol)
                        elif button_label == "LINEAR REGRESSION PRICE":
                            dpg.add_text(f"Linear regression for {symbol}", 
                                        color=[255, 200, 150])
                        
                        # Add spacing between charts
                        if i < len(active_stocks) - 1:
                            dpg.add_spacer(height=15)
        
        print(f"📊 Created tab for {button_label} with {len(active_stocks)} stock charts")
    
    if len(active_indicator_buttons) == 0:
        # Show default message when no indicators are active
        with dpg.tab(label="Select Indicators", tag="default_tab", parent=chart_tabs_tag):  # Remove timestamp
            dpg.add_spacer(height=50)
            dpg.add_text("💡 Select indicator buttons above to see analysis charts", 
                       color=[150, 150, 150], indent=50)
            dpg.add_spacer(height=20)
            dpg.add_text("Available indicators: RSI, PRICE, LINEAR REGRESSION", 
                       color=[100, 100, 100], indent=50)
            dpg.add_spacer(height=10)
            dpg.add_text(f"Active stocks: {len(get_all_active_tags())}", 
                       color=[100, 100, 100], indent=50)
                   
def get_active_indicators():
    """Get list of currently active indicator button labels"""
    return [dpg.get_item_label(tag) for tag in active_indicator_buttons if dpg.does_item_exist(tag)]

def plus_button_callback():
    """Open stock search dialog - exact same as graph_dpg.py"""
    print("Plus button clicked!")
    create_stock_search(
        mode="callback",  # Change to callback mode
        callback=handle_stock_selection,  # Add callback
        line_tag=None,
        x_axis_tag=None,
        y_axis_tag=None,
        plot_tag=None
    )
    
def handle_stock_selection(symbol):
    """Handle stock selection from search"""
    if constants.DEBUG:
        print(f"📊 Stock selected: {symbol}")
    
    try:
        tag = create_stock_tag(symbol, f"{symbol} Corp.", "stock_tags_container")
        if tag:
            if constants.DEBUG:
                print(f"✅ Created stock tag for {symbol}")
            indicator_activation()
        else:
            print(f"❌ Failed to create tag for {symbol}")
    except Exception as e:
        print(f"❌ Error creating stock tag: {e}")

def fav_button_callback():
    """Heart button callback - exact same as graph_dpg.py"""
    print("Heart button clicked!")
    # Show favorited stocks
    from components.stock.stock_data_manager import get_favorited_stocks
    favorites = get_favorited_stocks()
    print(f"Favorited stocks: {favorites}")

def indicator_activation():
    """Enable/disable indicator buttons based on whether stock tags exist"""
    print(f"🔧 indicator_activation() called")
    
    if dpg.does_item_exist('group_indicators'):
        has_stocks = len(get_all_active_tags()) > 0
        print(f"📊 Active stock tags count: {len(get_all_active_tags())}")
        print(f"🔘 Has stocks: {has_stocks}")
        
        dpg.configure_item("hint_1", show= not has_stocks)
        
        if len(active_indicator_buttons) == 0:
            dpg.configure_item("hint_2", show= has_stocks)
        else:
            dpg.configure_item("hint_2", show= False)

        
        # Show/hide the entire group
        dpg.configure_item('group_indicators', show=has_stocks)
        
        # Reset buttons to inactive when no stocks
        if not has_stocks:
            reset_all_indicator_buttons()
        else:
            populate_chart_tabs()
        
        print(f"{'👁️' if has_stocks else '🙈'} Group indicators {'shown' if has_stocks else 'hidden'}")
    else:
        print("❌ group_indicators does not exist")

    
    