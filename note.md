1. app.py – ตัวแอปหลัก (Streamlit UI)
สิ่งที่ต้องเขียน:
    st.title() แสดงหัวข้อ
    ฟอร์มรับ input จากผู้ใช้ (st.form)
        เรียกใช้:
            fetch_stock_data(ticker) → จาก stock_fetcher.py

            generate_summary(df, ticker) → จาก report_generator.py

            generate_plot(df, ticker) → จาก report_generator.py

แสดงข้อมูล, สรุป, กราฟ
2. stock_fetcher.py
        def fetch_raw_data(ticker: str, days: int = 30) -> pd.DataFrame:"""ดึงข้อมูลราคาหุ้นย้อนหลังจากyfinance"""
        def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:"""คำนวณ MA5, MA20, และ %Change จากข้อมูลราคา"""
        def fetch_stock_data(ticker: str) -> Optional[pd.DataFrame]:"""ฟังก์ชันรวม: fetch + calculate แล้ว return ข้อมูลพร้อมใช้"""

3. report_generator.py – สร้างสรุป + กราฟ matplotlib
        def generate_summary(df: pd.DataFrame, ticker: str) -> str:
    """สรุปข้อมูลล่าสุดเป็น Markdown เช่น ราคาปิด, เปอร์เซ็นต์เปลี่ยนแปลง"""
        def generate_plot(df: pd.DataFrame, ticker: str):
    """วาดกราฟราคาหุ้นย้อนหลัง + เส้น MA5/MA20 ด้วย matplotlib"""

requir lib
1. streamlit
2. yfinance
3. pandas
4. matplotlib
