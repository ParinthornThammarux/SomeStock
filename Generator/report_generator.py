import fpdf
import os
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
def exportpdf(text , filename = "StockReport"):
    if not text.strip():
        return False
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(0,10,txt=line,ln = True)
    pdf.output(filename)
    print("PDF saved at:", os.path.abspath(filename))
    return True

def exportgraph(Name ,period  = '1y',show_ma = True, ma_window = 20):
    df = yf.download(Name,period=period)

    plt.figure(figsize=(14,7))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')

    # if show_ma:
    #     plt.plot(df.index, df['MA'], label=f'{ma_window}-Day MA', color='orange', linestyle='--')


    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.title(f'{Name} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()