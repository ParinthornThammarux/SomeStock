import dearpygui.dearpygui as dpg
from Indicator import Indicator_VMA


def Create_Indicator_page(parent_tag):
    dpg.add_spacer(height=50, parent=parent_tag)

    with dpg.group(horizontal=False, parent=parent_tag):
        dpg.add_text("Indicator Module", color=[255, 255, 255])
        dpg.add_separator()
        dpg.add_spacer(height=20)

        # Input symbol
        dpg.add_text("Enter Stock Symbol:")
        dpg.add_input_text(tag="symbol_input", width=200, hint="e.g. AAPL")
        dpg.add_spacer(height=10)

        # Indicator selection
        dpg.add_text("Select Indicator:")
        dpg.add_combo(["VMA", "SMA", "RSI"], default_value="VMA", tag="indicator_selector", width=200)
        dpg.add_spacer(height=10)

        dpg.add_button(label="Calculate", width=150, callback=calculate_indicator)

        # Plot area
        with dpg.child_window(tag="plot_area", width=-1, height=420, border=True):
            dpg.add_text("📊 Chart will appear here")
        dpg.add_spacer(height=10)

        dpg.add_spacer(height=20)
        dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)


def calculate_indicator():
    symbol = dpg.get_value("symbol_input")
    indicator = dpg.get_value("indicator_selector")

    if not symbol:
        dpg.delete_item("plot_area", children_only=True)
        dpg.add_text("❗ Please enter a stock symbol", parent="plot_area", color=[255, 0, 0])
        return

    # Clear previous plot
    dpg.delete_item("plot_area", children_only=True)

    # Call the correct indicator function from Indicator.py
    if indicator == "VMA":
        Indicator_VMA.VMA(symbol, plot_area="plot_area")
    elif indicator == "SMA":
        ind.SMA(symbol, plot_area="plot_area")
    elif indicator == "RSI":
        ind.RSI(symbol, plot_area="plot_area")
    else:
        dpg.add_text("⚠️ Unknown Indicator Selected", parent="plot_area", color=[255, 255, 0])
    
def go_to_welcome():
    from containers.container_content import show_page
    show_page("welcome")
