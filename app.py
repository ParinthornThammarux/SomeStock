import tkinter as tk
from tkinter import ttk
from Fetch import StockFetch
#funtion
def search():
    name = ticker_entry.get().strip()
    if name:
        result = StockFetch.fetch_stock_data(name)
        result_text.delete("1.0", tk.END)
        if result is not None:
            # แปลง DataFrame เป็น string แบบตาราง (text) พร้อมตัดบรรทัดยาวเกิน
            result_str = result.tail(10).to_string()  # แสดงแค่ 10 แถวท้าย
            result_text.insert(tk.END, result_str,"center")
        else:
            result_text.insert(tk.END, "ไม่สามารถดึงข้อมูลหุ้นได้","center")
    else:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "กรุณากรอกชื่อหุ้น")
#
# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("📈 Daily Stock Reporter")
root.geometry("800x450")
root.resizable(True, True)

# ส่วนหัว
title_label = ttk.Label(root, text="📈 Daily Stock Report", font=("Helvetica", 16, "bold"))
title_label.pack(pady=20)

# ช่องกรอกชื่อหุ้น
ticker_label = ttk.Label(root, text="กรอกสัญลักษณ์หุ้น (เช่น AAPL):")
ticker_label.pack()
#
ticker_entry = ttk.Entry(root, width=20)
ticker_entry.pack(pady=5)
#ปุ่มค้นหา
search_button = ttk.Button(root,text = "ค้นหา",command=search)
search_button.pack(pady =  10)
# กล่องแสดงผล
result_text = tk.Text(root, height=15, width=150, wrap="word")
result_text.pack(pady=5)
result_text.tag_configure("center", justify="center")
# เริ่มแอป
root.mainloop()
