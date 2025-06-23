import tkinter as tk
from tkinter import ttk
import StockFetch  # สมมติว่าคุณมีโมดูลนี้สำหรับดึงข้อมูลหุ้น

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("📈 Daily Stock Reporter")
root.geometry("400x300")
root.resizable(False, False)

# ส่วนหัว
title_label = ttk.Label(root, text="📈 Daily Stock Report", font=("Helvetica", 16, "bold"))
title_label.pack(pady=20)

# ช่องกรอกชื่อหุ้น
ticker_label = ttk.Label(root, text="กรอกสัญลักษณ์หุ้น (เช่น AAPL):")
ticker_label.pack()

ticker_entry = ttk.Entry(root, width=20)
ticker_entry.pack(pady=5)

# กล่องแสดงผล
result_text = tk.Text(root, height=10, width=40, wrap="word")
result_text.pack(pady=10)

# ปุ่มดึงข้อมูล
def fetch_data():
    ticker = ticker_entry.get().strip()
    if not ticker:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "⚠️ กรุณากรอกสัญลักษณ์หุ้น")
        return
    try:
        summary = StockFetch.get_summary(ticker)  # สมมติว่าคุณมีฟังก์ชันนี้ใน StockFetch
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, summary)
    except Exception as e:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"❌ เกิดข้อผิดพลาด: {e}")

fetch_button = ttk.Button(root, text="ดึงข้อมูล", command=fetch_data)
fetch_button.pack(pady=5)

# เริ่มแอป
root.mainloop()
