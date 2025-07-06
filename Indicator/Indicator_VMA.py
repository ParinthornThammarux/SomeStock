import talib
from Fetch_Indicator import fetch_data
import dearpygui.dearpygui as dpg
import numpy as np

def VMA(symbol, plot_area):
    data = fetch_data(symbol)
    data.set_index('Date', inplace=True)

    dv = data['Close'] * data['Volume']
    data['VMA'] = dv.rolling(window=20).sum() / data['Volume'].rolling(window=20).sum()

    close_prices = data['Close'].values.tolist()
    vma_values = data['VMA'].values.tolist()
    timestamps = list(range(len(data)))

    # Clear plot area
    dpg.delete_item(plot_area, children_only=True)

    # Plot inside provided container
    with dpg.plot(label=f"{symbol} - VMA", height=400, width=-1, parent=plot_area):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="Time")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Price")

        dpg.add_line_series(timestamps, close_prices, label="Close Price", parent=y_axis, weight=2, color=[0, 0, 255, 255])
        dpg.add_line_series(timestamps, vma_values, label="VMA", parent=y_axis, weight=2, color=[255, 165, 0, 255])

    latest_vma = data['VMA'].iloc[-1]
    print(f"📈 {symbol} - Latest VMA: {latest_vma:.2f}")
    return latest_vma
