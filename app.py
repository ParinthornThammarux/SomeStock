import tkinter as tk
from tkinter import ttk
from Fetch import StockFetch
from Generator import report_generator

# function search stock
def search():
    name = ticker_entry.get().strip()
    select_option = combo.get()
    result_text.delete("1.0", tk.END)
    if not name:
        result_text.insert(tk.END, "กรุณากรอกชื่อหุ้น", "center")
        return
    if select_option == "rawdata":
        result = StockFetch.fetch_stock_data(name)
    elif select_option == "price":
        result = StockFetch.fetch_rawdata(name)
    elif select_option == "EMA":
        result = StockFetch.calculate_MA(name)
    if result is not None:
        try:
            result_str = result.tail(10).to_string()
        except AttributeError:
            result_str = str(result)
        result_text.insert(tk.END, result_str, "center")
    else:
        result_text.insert(tk.END, "ไม่สามารถดึงข้อมูลหุ้นได้", "center")

# function export
def exporttypepdf():
    text = result_text.get("1.0", tk.END).strip()
    success = report_generator.exportpdf(text)
    if success:
        return True

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("📈 Daily Stock Reporter")
root.geometry("900x700")
root.configure(bg="#F7FAFC")

# Configure style
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#F7FAFC")
style.configure("TLabel", background="#F7FAFC", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TEntry", font=("Segoe UI", 10))
style.configure("TCombobox", font=("Segoe UI", 10))

# สร้าง Frame หลัก
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = ttk.Label(main_frame, text="📈 Daily Stock Reporter", font=("Segoe UI", 20, "bold"), anchor="center")
title_label.pack(pady=(0, 20))

# Input section
input_frame = ttk.Frame(main_frame)
input_frame.pack(pady=10)

ticker_label = ttk.Label(input_frame, text="สัญลักษณ์หุ้น:")
ticker_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)

ticker_entry = ttk.Entry(input_frame, width=20)
ticker_entry.grid(row=0, column=1, padx=5, pady=5)

combo = ttk.Combobox(input_frame, values=["rawdata", "price", "EMA"], state="readonly")
combo.current(0)
combo.grid(row=0, column=2, padx=5, pady=5)

search_button = ttk.Button(input_frame, text="ค้นหา", command=search)
search_button.grid(row=0, column=3, padx=5, pady=5)

# Result box
result_label = ttk.Label(main_frame, text="ผลลัพธ์:")
result_label.pack(pady=(20, 5))

result_text = tk.Text(main_frame, height=20, width=100, wrap="word", font=("Consolas", 10), bd=1, relief="solid")
result_text.pack(pady=5)
result_text.tag_configure("center", justify="center")

# Export button
export_pdf = ttk.Button(main_frame, text="📤 ส่งออก PDF", command=exporttypepdf)
export_pdf.pack(pady=15)

# Run the app
root.mainloop()
