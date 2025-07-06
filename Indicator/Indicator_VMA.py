import dearpygui.dearpygui as dpg
from Indicator.Fetch_Indicator import fetch_data
import numpy as np

def VMA(symbol, plot_area):
    try:
        # Clear and show loading
        dpg.delete_item(plot_area, children_only=True)
        dpg.add_text(f"🔄 Loading data for {symbol}...", parent=plot_area, color=[100, 255, 100])
        
        data = fetch_data(symbol)
        if data.empty:
            dpg.delete_item(plot_area, children_only=True)
            dpg.add_text(f"❌ No data available for {symbol}", parent=plot_area, color=[255, 100, 100])
            return
        
        # Calculate VMA
        data = data.copy()
        if 'Date' in data.columns:
            data.set_index('Date', inplace=True)
        
        window = 20
        dv = data['Close'] * data['Volume']
        data['VMA'] = dv.rolling(window=window).sum() / data['Volume'].rolling(window=window).sum()
        
        # Remove NaN values
        data = data.dropna()
        
        if len(data) < 2:
            dpg.delete_item(plot_area, children_only=True)
            dpg.add_text(f"❌ Not enough data for {symbol}", parent=plot_area, color=[255, 100, 100])
            return
        
        # Prepare data for plotting
        dates = list(range(len(data)))  # Use indices instead of dates for simplicity
        closes = data['Close'].values
        vmas = data['VMA'].values
        
        # Create plot data
        close_plot_data = []
        vma_plot_data = []
        
        for i, (close, vma) in enumerate(zip(closes, vmas)):
            close_plot_data.append([i, close])
            vma_plot_data.append([i, vma])
        
        # Clear plot area
        dpg.delete_item(plot_area, children_only=True)
        
        # Create plot
        with dpg.plot(label=f"{symbol} - Close Price vs VMA", height=350, width=-1, parent=plot_area):
            dpg.add_plot_legend()
            
            # Create axes
            dpg.add_plot_axis(dpg.mvXAxis, label="Time Period")
            dpg.add_plot_axis(dpg.mvYAxis, label="Price ($)", tag="y_axis")
            
            # Add data series
            dpg.add_line_series(close_plot_data, label="Close Price", parent="y_axis", tag="close_series")
            dpg.add_line_series(vma_plot_data, label=f"VMA ({window})", parent="y_axis", tag="vma_series")
        
        # Add statistics below the plot
        dpg.add_separator(parent=plot_area)
        
        with dpg.group(horizontal=True, parent=plot_area):
            dpg.add_text("📊 Latest Values:", color=[255, 255, 255])
        
        with dpg.group(horizontal=True, parent=plot_area):
            dpg.add_text(f"Close: ${closes[-1]:.2f}", color=[100, 200, 255])
            dpg.add_spacer(width=50)
            dpg.add_text(f"VMA: ${vmas[-1]:.2f}", color=[255, 150, 100])
        
        # Signal
        signal = "🟢 BULLISH" if closes[-1] > vmas[-1] else "🔴 BEARISH"
        signal_color = [100, 255, 100] if closes[-1] > vmas[-1] else [255, 100, 100]
        dpg.add_text(f"Signal: {signal}", parent=plot_area, color=signal_color)
        
        # Performance
        pct_change = ((closes[-1] - closes[0]) / closes[0]) * 100
        perf_color = [100, 255, 100] if pct_change > 0 else [255, 100, 100]
        dpg.add_text(f"Period Change: {pct_change:.2f}%", parent=plot_area, color=perf_color)
        
    except Exception as e:
        dpg.delete_item(plot_area, children_only=True)
        dpg.add_text(f"❌ Error calculating VMA: {str(e)}", parent=plot_area, color=[255, 100, 100])
        print(f"VMA Error: {e}")
