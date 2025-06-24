import tkinter as tk
from tkinter import ttk
from Fetch import StockFetch
from Generator import report_generator
#funtion search stock
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
    result_str = result.tail(10).to_string()
    if result is not None:
        try:
            result_str = result.to_string()
        except AttributeError:
            result_str = str(result)
        result_text.insert(tk.END, result_str, "center")
    else:
        result_text.insert(tk.END, "ไม่สามารถดึงข้อมูลหุ้นได้", "center")
#function export
def exporttypepdf():
    text = result_text.get("1.0", tk.END).strip()
    success = report_generator.exportpdf(text)
    if success:
        return True
# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("📈 Daily Stock Reporter")
root.geometry("1000x800")
root.resizable(True, True)
#configure of main screen
root.configure(bg="#CCE5FF")
#confige ttk
Style = ttk.Style()

# ส่วนหัว
title_label = ttk.Label(root, text="📈 Daily Stock Report", font=("Helvetica", 16, "bold"))
title_label.pack(pady=20)

# ช่องกรอกชื่อหุ้น
ticker_label = ttk.Label(root, text="กรอกสัญลักษณ์หุ้น (เช่น AAPL):")
ticker_label.pack()
#dropdown
combo = ttk.Combobox(root, values=["rawdata","price","EMA"])
combo.pack(pady = 5, padx = 5)
#กล่องข้อความ
ticker_entry = ttk.Entry(root, width=20)
ticker_entry.pack(pady=5)
Style.configure("TEntry",fieldbackground = "#99CCFF")
#ปุ่มค้นหา
search_button = ttk.Button(root,text = "ค้นหา",command=search)
search_button.pack(pady =  10)
# กล่องแสดงผล
result_text = tk.Text(root, height=15, width=120, wrap="word")
result_text.pack(pady=5)
result_text.tag_configure("center", justify="center")
#export pdf
export_pdf = tk.Button(root,text="EXPORT PDF",command=exporttypepdf)
export_pdf.pack(pady = 5)

root.mainloop()