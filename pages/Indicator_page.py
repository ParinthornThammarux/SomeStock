import dearpygui.dearpygui as dpg
from Indicator import Indicator_VMA as IV

def Create_Indicator_page(parent_tag):
    dpg.add_spacer(height=30, parent=parent_tag)
    
    with dpg.group(horizontal=False, parent=parent_tag):
        # Header
        dpg.add_text("📈 Technical Indicator Analysis", color=[255, 255, 255])
        dpg.add_separator()
        dpg.add_spacer(height=20)
        
        # Input controls
        with dpg.group(horizontal=True):
            dpg.add_text("Stock Symbol:", color=[200, 200, 200])
            dpg.add_input_text(tag="symbol_input", width=150, hint="e.g. AAPL", 
                             on_enter=True, callback=lambda: calculate_indicator())
            dpg.add_spacer(width=20)
            dpg.add_button(label="📊 Analyze", callback=calculate_indicator)
        
        dpg.add_spacer(height=15)
        
        with dpg.group(horizontal=True):
            dpg.add_text("Indicator:", color=[200, 200, 200])
            dpg.add_combo(["VMA", "SMA", "RSI"], 
                         default_value="VMA", tag="indicator_selector", width=150)
            dpg.add_spacer(width=20)
            dpg.add_button(label="🔄 Clear", callback=clear_plot)
        
        dpg.add_spacer(height=20)
        
        # Plot area
        with dpg.child_window(tag="plot_area", width=-1, height=450, border=True):
            dpg.add_text("📊 Chart will appear here", color=[150, 150, 150])
            dpg.add_spacer(height=20)
            dpg.add_text("• Enter a stock symbol above", color=[100, 100, 100])
            dpg.add_text("• Select an indicator type", color=[100, 100, 100])
            dpg.add_text("• Click 'Analyze' to generate the chart", color=[100, 100, 100])
        
        dpg.add_spacer(height=20)
        
        # ปุ่มแยกมาเลยตรงนี้
        dpg.add_button(label="⬅️ Back to Welcome", callback=go_to_welcome, width=150)

def calculate_indicator():
    symbol = dpg.get_value("symbol_input").strip().upper()
    indicator = dpg.get_value("indicator_selector")
    
    if not symbol:
        dpg.delete_item("plot_area", children_only=True)
        dpg.add_text("❗ Please enter a stock symbol", parent="plot_area", color=[255, 150, 100])
        return
    
    try:
        if indicator == "VMA":
            IV.VMA(symbol, plot_area="plot_area")
        elif indicator == "SMA":
            dpg.delete_item("plot_area", children_only=True)
            dpg.add_text("⚠️ SMA indicator coming soon!", parent="plot_area", color=[255, 255, 100])
            dpg.add_text("Please use VMA for now.", parent="plot_area", color=[150, 150, 150])
        elif indicator == "RSI":
            dpg.delete_item("plot_area", children_only=True)
            dpg.add_text("⚠️ RSI indicator coming soon!", parent="plot_area", color=[255, 255, 100])
            dpg.add_text("Please use VMA for now.", parent="plot_area", color=[150, 150, 150])
        else:
            dpg.delete_item("plot_area", children_only=True)
            dpg.add_text("❌ Unknown indicator selected", parent="plot_area", color=[255, 100, 100])
    except Exception as e:
        dpg.delete_item("plot_area", children_only=True)
        dpg.add_text(f"❌ Error: {str(e)}", parent="plot_area", color=[255, 100, 100])

def clear_plot():
    dpg.delete_item("plot_area", children_only=True)
    dpg.add_text("📊 Chart will appear here", color=[150, 150, 150], parent="plot_area")
    dpg.add_spacer(height=20, parent="plot_area")
    dpg.add_text("• Enter a stock symbol above", color=[100, 100, 100], parent="plot_area")
    dpg.add_text("• Select an indicator type", color=[100, 100, 100], parent="plot_area")
    dpg.add_text("• Click 'Analyze' to generate the chart", color=[100, 100, 100], parent="plot_area")

def go_to_welcome():
    try:
        from containers.container_content import show_page
        show_page("welcome")
    except ImportError:
        dpg.delete_item("plot_area", children_only=True)
        dpg.add_text("❌ Navigation error - container_content not found", 
                    parent="plot_area", color=[255, 100, 100])