import talib
from Fetch_Indicator import fetch_data
import dearpygui.dearpygui as dpg
import numpy as np

def VMA(symbol):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    dv = data['Close'] * data['Volume']
    data['VMA'] = dv.rolling(window=20).sum() / data['Volume'].rolling(window=20).sum()

    close_prices = data['Close'].values.tolist()
    vma_values = data['VMA'].values.tolist()
    timestamps = [i for i in range(len(data))]  # Use index positions as x-axis

    # Create the DearPyGui plot
    with dpg.window(f"{symbol} - Volume Moving Average", width=800, height=500):
        dpg.add_plot(f"{symbol} Plot", height=400)
        dpg.add_plot_legend()

        dpg.add_line_series(f"{symbol} Plot", "Close Price", timestamps, close_prices, weight=2, color=[0, 0, 255, 255])
        dpg.add_line_series(f"{symbol} Plot", "VMA", timestamps, vma_values, weight=2, color=[255, 165, 0, 255])

        dpg.set_plot_xlimits_auto(f"{symbol} Plot")
        dpg.set_plot_ylimits_auto(f"{symbol} Plot")

    latest_vma = data['VMA'].iloc[-1]
    print(f"📈 {symbol} - Latest VMA: {latest_vma:.2f}")

    dpg.start_dearpygui()
    return latest_vma
