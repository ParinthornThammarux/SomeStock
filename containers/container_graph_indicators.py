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
from components.graph.graph_dpg import create_main_graph
from components.graph.graph_advanced import create_advanced_analysis_tab
from components.graph.graph_interactive import create_interactive_tab
from components.graph.graph_sankey import create_sankey_tab
from components.graph.graph_rsi import create_main_rsi_graph

# Global variables
current_stock_line_tag = None
matplotlib_helper = None
plotly_helper = None
enabled_indicators = []
current_selected_stock = None

def create_graph_indicators(parent_tag):
    """
    Enhanced version of main graph page with advanced chart options
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
    chart_tabs_tag = f"chart_tabs_{timestamp}"
    
    # Check if container already exists and delete it
    if dpg.does_item_exist(main_container_tag):
        dpg.delete_item(main_container_tag)
    
    try:
        # Create a main container with tabs for different chart types
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
                
                indicator_activation()
                    
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
            
            with dpg.group(tag="group_indicators",horizontal=True,indent=5):
                dpg.add_button(tag="rsi_button",label="RSI")
                dpg.add_button(tag="price_button",label="PRICE")
                dpg.add_button(tag="linear_price_button",label="LINEAR REGRESSION PRICE")


            # Create tab bar for different chart types
            with dpg.tab_bar(tag=chart_tabs_tag,indent=50,):
                print("created empty tab bar")
                # # Tab 1: rsi_graph testing for pun
                # with dpg.tab(label="RSI Charts", tag=f"dpg_tab_{timestamp}") as dpg_tab:
                #     try:
                #         # Pass the tab itself as parent, not the tab bar
                #         create_main_rsi_graph(dpg_tab, timestamp)
                #     except Exception as e:
                #         print(f"Error creating DPG charts tab: {e}")
                #         dpg.add_text(f"Error loading DPG charts: {e}", color=[255, 0, 0])
                
                # # Tab 2: Advanced Pandas/Matplotlib charts
                # with dpg.tab(label="Advanced Analysis", tag=f"advanced_tab_{timestamp}") as advanced_tab:
                #     try:
                #         create_advanced_analysis_tab(advanced_tab, timestamp)
                #     except Exception as e:
                #         print(f"Error creating advanced analysis tab: {e}")
                #         dpg.add_text(f"Error loading advanced analysis: {e}", color=[255, 0, 0])
                
                # # Tab 3: Interactive Plotly charts
                # with dpg.tab(label="Interactive Charts", tag=f"interactive_tab_{timestamp}") as interactive_tab:
                #     try:
                #         create_interactive_tab(interactive_tab, timestamp)
                #     except Exception as e:
                #         print(f"Error creating interactive charts tab: {e}")
                #         dpg.add_text(f"Error loading interactive charts: {e}", color=[255, 0, 0])
                
                # # Tab 4: Sankey Analysis
                # with dpg.tab(label="Flow Analysis", tag=f"sankey_tab_{timestamp}") as sankey_tab:
                #     try:
                #         create_sankey_tab(sankey_tab, timestamp)
                #     except Exception as e:
                #         print(f"Error creating sankey tab: {e}")
                #         dpg.add_text(f"Error loading flow analysis: {e}", color=[255, 0, 0])
   
    except Exception as e:
        print(f"Error creating graph tabs container: {e}")
        # Fallback to simple content
        dpg.add_text("Error loading enhanced charts", parent=parent_tag, color=[255, 0, 0])
        dpg.add_text(f"Error details: {str(e)}", parent=parent_tag, color=[255, 100, 100])
    
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
    
    # Create stock tag in the tags container
    try:
        tag = create_stock_tag(symbol, f"{symbol} Corp.", "stock_tags_container")
        if tag:
            if constants.DEBUG:
                print(f"✅ Created stock tag for {symbol}")
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
    if dpg.does_item_exist('group_indicators'):
        tag_count = len(get_all_active_tags())
        if tag_count > 0:
            # Loop through all indicator buttons and enable them
            children = dpg.get_item_children('group_indicators', slot=1)
            if children:
                for child in children:
                    # Check if it's a button
                    item_type = dpg.get_item_type(child)
                    if item_type == "mvAppItemType::mvButton":
                        dpg.configure_item(child, enabled=True)
                        print(f"✅ Enabled button: {dpg.get_item_label(child)}")
           
        else:
            # Disable all indicator buttons when no tags
            children = dpg.get_item_children('group_indicators', slot=1)
            if children:
                for child in children:
                    item_type = dpg.get_item_type(child)
                    if item_type == "mvAppItemType::mvButton":
                        dpg.configure_item(child, enabled=False)
                        print(f"❌ Disabled button: {dpg.get_item_label(child)}")
    else:
        print("group_indicators is not accessable")



def run_analysis_on_focused_stock(analysis_type):
    """Run analysis on the currently focused stock"""
    from components.stock.stock_data_manager import get_focused_tag
    
    focused_tag = get_focused_tag()
    if focused_tag:
        symbol = focused_tag.symbol
        print(f"🔄 Running {analysis_type} analysis for {symbol}")
        
        if analysis_type == "rsi":
            run_rsi_analysis(symbol)
        elif analysis_type == "price":
            run_price_analysis(symbol)
        elif analysis_type == "linear":
            run_linear_analysis(symbol)
    else:
        print("❌ No stock selected. Please click on a stock tag first.")

def run_rsi_analysis(symbol):
    """Run RSI analysis on specified stock"""
    print(f"📈 Running RSI analysis for {symbol}")
    # Add your RSI analysis code here

def run_price_analysis(symbol):
    """Run price analysis on specified stock"""
    print(f"💰 Running price analysis for {symbol}")
    # Add your price analysis code here

def run_linear_analysis(symbol):
    """Run linear regression analysis on specified stock"""
    print(f"📊 Running linear regression for {symbol}")
    # Add your linear regression analysis code here
    
    