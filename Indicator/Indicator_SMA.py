import talib
import dearpygui.dearpygui as dpg
from components import start_dearpygui, window, add_plot, add_plot_legend, add_line_series, set_plot_xlimits_auto, set_plot_ylimits_auto
from Fetch_Indicator import fetch_data

def calculate_sma(symbol, period):
    data = fetch_data(symbol)
    data['SMA'] = talib.SMA(data['Close'], timeperiod=period)

    latest_sma = data['SMA'].iloc[-1]
    print(f"📈 {symbol} - Latest SMA ({period}): {latest_sma:.2f}")

   #create dpg graph


    return latest_sma