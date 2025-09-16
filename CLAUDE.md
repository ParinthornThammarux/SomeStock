# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main_app.py
```

### Testing
No automated testing framework is currently configured. Manual testing is done by running the application and interacting with the UI.

## Code Architecture

### Framework and GUI
- **Primary GUI Framework**: DearPyGUI (dearpygui) - Desktop application with immediate mode GUI
- **Data Visualization**: Matplotlib integration for charting and Plotly for interactive charts
- **Stock Data Sources**: Multiple data providers (stockdex, yahooquery) with fallback mechanisms

### Project Structure

#### Core Application (`main_app.py`)
- Main entry point with window setup and animation system
- Handles sidebar collapse/expand animations with timing controls
- Window configuration: 1400x900 resolution, vsync enabled

#### Components Architecture
- **Sidebar** (`components/sidebar.py`): Collapsible navigation with Font Awesome icons
- **Top Bar** (`components/topbar_stuff.py`): Menu and controls
- **Stock Search** (`components/stock_search.py`): Stock data loading and search functionality
- **User System** (`components/user/`): User creation and login components

#### Page System (`containers/container_content.py`)
- Dynamic page switching mechanism using `show_page()` function
- Single content container that gets cleared and repopulated
- Page routing with match-case statements

#### Available Pages
- `"welcome"`: Welcome/portfolio page
- `"page_b"`: Search functionality
- `"enhanced"`: Dashboard view
- `"indicator"`: Technical indicator analysis
- `"create_hailun_content"`: Custom content creation

#### Technical Indicators (`Indicator/` directory)
Each indicator is implemented as a separate module:
- `Indicator_RSI.py`: Relative Strength Index (14-period default)
- `Indicator_SMA.py`, `Indicator_EMA.py`: Moving averages
- `Indicator_MOM.py`: Momentum indicator
- `Indicator_Hammer.py`, `Indicator_Doji.py`: Candlestick patterns
- `Indicator_Peg.py`: PEG ratio calculations
- `Indicator_VMA.py`: Volume Moving Average
- `linear_regression_model.py`: Prediction capabilities

#### Stock Data Layer (`utils/stock_fetch_layer.py`)
- Unified fetch system with rate limiting (5-second delays)
- Multi-source data fetching with retry logic (3 attempts max)
- Thread-safe operations with stop flags for concurrent requests
- 30-second request timeout

#### Constants and Configuration (`utils/constants.py`)
- Comprehensive Font Awesome icon definitions (150+ icons)
- Animation parameters: 0.2s duration, 50px collapsed / 200px expanded sidebar
- Font management for Windows (segoeui.ttf + fa-solid-900.ttf)
- Global state variables for user session and favorites

### Key Patterns

#### Font System
The application uses a dual-font system:
- Default system font (Segoe UI on Windows) for text
- Font Awesome for icons with multiple size variants (10px, 20px)
- Font loading with fallback to DearPyGUI defaults

#### State Management
- Global variables in `constants.py` for application state
- User session management with `Cur_User` and `favorite_stocks`
- Active indicator button tracking with sets

#### Data Fetching Strategy
- Rate-limited requests to prevent API throttling
- Multi-source fallback (stockdex → yahooquery)
- Concurrent request management with threading
- Graceful degradation when data sources fail

#### UI Animation
- Time-based sidebar animations with progress calculations
- Frame callback system for smooth transitions
- State machine for animation direction (expand/collapse)

### Development Notes

#### Stock Data Integration
- Stock data is cached in `utils/stock_data.json`
- Multiple data provider support with automatic failover
- Real-time data fetching with configurable intervals

#### User System
- JSON-based user storage in `registered_users/` directory
- Base user template system
- Session persistence across application runs

#### Chart Integration
- Matplotlib backend for static charts
- Plotly integration for interactive visualizations
- Chart data binding to DearPyGUI plot components

### Technical Requirements

#### Dependencies
- Python 3.11+ (ta-lib wheel provided for Windows)
- DearPyGUI 1.11.1+ for GUI framework
- pandas, numpy for data manipulation
- matplotlib, plotly for visualization
- requests, beautifulsoup4 for web scraping
- stockdex, yahooquery for financial data

#### Font Requirements
- `fa-solid-900.ttf` must be placed in root directory
- Windows system fonts expected (segoeui.ttf)

#### Performance Considerations
- Rate limiting prevents API throttling
- Thread-based data fetching for responsiveness
- Memory management for large datasets
- Font caching and reuse across components