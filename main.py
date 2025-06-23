import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

ticker = "AAPL"
stock = yf.Ticker(ticker)
info = stock.info

# เตรียมข้อความสรุป
summary = f"""
📊 ข้อมูลหุ้น: {info.get('longName', 'N/A')}
📌 สัญลักษณ์: {ticker}
🏭 กลุ่มธุรกิจ: {info.get('sector', 'N/A')}
💰 Market Cap: {info.get('marketCap', 0):,}
📈 ราคาปัจจุบัน: {info.get('currentPrice', 'N/A')} USD
🧮 EPS: {info.get('trailingEps', 'N/A')}
💸 ปันผล: {info.get('dividendYield', 0)*100:.2f}%
"""

# สร้างหน้าต่างแสดงผล
root = tk.Tk()
root.title("ข้อมูลหุ้น")

label = tk.Label(root, text=summary, justify="left", font=("TH Sarabun New", 16))
label.pack(padx=20, pady=20)

root.mainloop()
