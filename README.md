# Personal Stock Analyzer

A Python stock analysis application with technical indicators, real-time data fetching, and interactive charting.

## Features

- Real-time stock data from Yahoo Finance & StockDex
- Technical indicators: RSI, SMA, EMA, Momentum, Candlestick patterns, etc.
- Interactive charts with Matplotlib & Plotly
- Stock search functionality
- Multi-page dashboard interface

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app/streamlit_app.py
```

## Project Structure

```
├── app/              # Streamlit web application
├── pages/            # Analysis pages (search, dashboard, indicators)
├── core/             # Core logic (data fetch, indicators)
├── components/       # UI components
├── utils/            # Utilities & constants
└── Indicator/        # Technical indicator implementations
```

## Dependencies

- Streamlit - Web framework
- Pandas, NumPy - Data analysis
- Matplotlib, Plotly - Visualization
- TA-Lib - Technical analysis
- YahooQuery, StockDex - Stock data sources

See `requirements.txt` for details.

## Key Features

- **Data Fetching**: Multi-source with fallback, rate limiting, 30s timeout
- **Indicators**: RSI, SMA, EMA, MOM, VMA, Hammer, Doji, PEG, Linear Regression
- **Caching**: JSON-based stock data caching
- **Multi-page UI**: Welcome, Search, Dashboard, Indicators, Custom content

## Usage

1. Search for a stock ticker
2. View real-time price data
3. Apply technical indicators
4. Analyze trends with interactive charts
5. Customize analysis views

## Notes

- Windows-optimized (includes TA-Lib wheel)
- Streamlit version is recommended for latest features
- See `guideline.md` for migration details
- See `CLAUDE.md` for development notes
