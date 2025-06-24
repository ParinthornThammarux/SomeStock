import fpdf as FPDF
def exportpdf(text , filename = "StockReport"):
    if not text.strip():
        return False
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(0,10,txt=line,ln = True)
    pdf.output(filename)
    return True
