# components/stock_component.py

import dearpygui.dearpygui as dpg
from utils import constants
import random
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
import pandas as pd

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# Cache configuration
CACHE_DURATION = 60 * 10  # 10 minutes in seconds
MAX_CACHE_SIZE = 100  # Maximum number of stocks to cache

# Color pairs for stock tags
COLOR_PAIRS = [
    [[180, 40, 80], [255, 229, 235]],     # Dark Pink Red
    [[30, 100, 180], [214, 235, 255]],    # Dark Blue
    [[200, 150, 30], [255, 248, 220]],    # Dark Yellow/Gold
    [[40, 120, 120], [218, 245, 245]],    # Dark Turquoise
    [[100, 60, 180], [239, 230, 255]],    # Dark Purple
    [[200, 100, 30], [255, 238, 218]],    # Dark Orange
    [[80, 80, 80], [245, 245, 245]],      # Dark Grey
    [[50, 70, 180], [226, 230, 255]],     # Dark Light Blue
    [[180, 40, 180], [255, 229, 255]],    # Dark Magenta
    [[60, 150, 80], [229, 255, 235]],     # Dark Green
    [[180, 80, 50], [255, 235, 229]],     # Dark Coral
    [[80, 50, 180], [235, 229, 255]],     # Dark Lavender
    [[50, 150, 150], [229, 255, 255]],    # Dark Aqua
    [[180, 150, 40], [255, 255, 229]],    # Dark Yellow
    [[180, 50, 50], [255, 229, 229]],     # Dark Red
    [[60, 60, 180], [229, 229, 255]],     # Dark Periwinkle
    [[180, 120, 50], [255, 243, 229]],    # Dark Peach
    [[120, 180, 50], [243, 255, 229]],    # Dark Lime Green
    [[50, 120, 180], [229, 243, 255]],    # Dark Sky Blue
    [[180, 50, 120], [255, 229, 243]]     # Dark Hot Pink
]

# =============================================================================
# DATA MODEL
# =============================================================================

@dataclass
class StockData:
    """Comprehensive stock data container with caching and serialization"""
    symbol: str
    company_name: str
    
    # Price data
    current_price: Optional[float] = None
    previous_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    
    # Volume data
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    
    # Financial data
    revenue: Optional[str] = None
    net_income: Optional[str] = None
    cash_flow: Optional[str] = None
    
    # Market data
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    
    # Chart data
    price_history: Optional[pd.DataFrame] = None
    
    # Metadata
    last_updated: Optional[float] = None
    data_source: str = "api"
    
    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self.last_updated is None:
            return False
        return (time.time() - self.last_updated) < CACHE_DURATION
    
    def get_cache_status(self) -> str:
        """Get human-readable cache status"""
        if self.last_updated is None:
            return "No Data"
        elif self.is_cache_valid():
            minutes_old = int((time.time() - self.last_updated) / 60)
            return f"Fresh ({minutes_old}m ago)"
        else:
            return "Expired"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'current_price': self.current_price,
            'previous_price': self.previous_price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'avg_volume': self.avg_volume,
            'revenue': self.revenue,
            'net_income': self.net_income,
            'cash_flow': self.cash_flow,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'last_updated': self.last_updated,
            'data_source': self.data_source
        }
        
        # Handle price_history DataFrame
        if self.price_history is not None:
            data['price_history'] = self.price_history.to_dict('records')
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockData':
        """Create from dictionary (JSON deserialization)"""
        stock_data = cls(
            symbol=data['symbol'],
            company_name=data['company_name'],
            current_price=data.get('current_price'),
            previous_price=data.get('previous_price'),
            change=data.get('change'),
            change_percent=data.get('change_percent'),
            volume=data.get('volume'),
            avg_volume=data.get('avg_volume'),
            revenue=data.get('revenue'),
            net_income=data.get('net_income'),
            cash_flow=data.get('cash_flow'),
            market_cap=data.get('market_cap'),
            pe_ratio=data.get('pe_ratio'),
            last_updated=data.get('last_updated'),
            data_source=data.get('data_source', 'api')
        )
        
        # Handle price_history DataFrame
        if 'price_history' in data and data['price_history']:
            stock_data.price_history = pd.DataFrame(data['price_history'])
        
        return stock_data

# =============================================================================
# UI COMPONENT
# =============================================================================

class StockTag:
    """Visual stock tag component with integrated data caching"""
    
    def __init__(self, symbol: str, parent: str, company_name: str, 
                 on_favorite: Optional[Callable] = None, 
                 on_remove: Optional[Callable] = None,
                 on_chart_click: Optional[Callable] = None):
        """
        Initialize a new stock tag
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            parent: Parent DPG container tag
            company_name: Company name for display
            on_favorite: Callback when favorite status changes
            on_remove: Callback when tag is removed
            on_chart_click: Callback when chart button is clicked
        """
        # Unfocus all existing tags BEFORE creating this one
        for tag in _active_tags:
            tag.set_focus(False)
            
        self.symbol = symbol.upper().strip()
        self.company_name = company_name
        self.is_favorited = False
        self.is_focused = False
        self.tag_id = f"tag_{self.symbol}_{int(time.time() * 1000)}"  # Unique ID
        self.parent = parent
        self.on_favorite = on_favorite
        self.on_remove = on_remove
        self.on_chart_click = on_chart_click
        
        # Initialize or get cached data
        self.stock_data = get_cached_stock_data(self.symbol, self.company_name)
        
        # Create the visual component
        self.create_visual_component()
        self.set_focus(True)
        
        # Add to global tracking
        _active_tags.append(self)
    
    def create_visual_component(self):
        """Create the styled stock tag as a rectangular box"""
        text_color, bg_color = get_random_color_pair()
        
        # Create themes for normal and focused states
        self._create_themes(text_color, bg_color)
        
        # Calculate width based on symbol length
        symbol_len = len(self.symbol)
        width_adjustment = max(0, (symbol_len - 4) * 7)
        total_width = 110 + width_adjustment
        
        with dpg.child_window(
            tag=self.tag_id,
            parent=self.parent,
            width=total_width,
            height=30,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            # Apply normal theme initially
            dpg.bind_item_theme(self.tag_id, f"normal_theme_{self.tag_id}")
            
            # Stock symbol with cache indicator
            self._create_symbol_text(text_color)
            
            # Action buttons
            self._create_action_buttons(symbol_len, width_adjustment)
    
    def _create_symbol_text(self, text_color):
        """Create the stock symbol text with cache indicator"""
        cache_indicator = "Fresh" if self.stock_data.is_cache_valid() else "Stale"
        
        dpg.add_text( 
            pos=[5, 5], 
            color=text_color, 
            tag=f"{self.tag_id}_text"
        )
    
    def _create_action_buttons(self, symbol_len, width_adjustment):
        """Create the action buttons (chart, heart, remove)"""
        base_x = 40 + width_adjustment
        
        # Chart button
        chart_btn = dpg.add_button(
            label=constants.ICON_CHART_LINE,
            tag=f"{self.tag_id}_chart",
            width=18,
            height=18,
            pos=[base_x, 6],
            callback=self._on_chart_clicked
        )
        if constants.small_font_awesome_icon_font_id:
            dpg.bind_item_font(chart_btn, constants.small_font_awesome_icon_font_id)

        # Heart button
        heart_btn = dpg.add_button(
            label=constants.ICON_HEART,
            tag=f"{self.tag_id}_heart",
            width=18,
            height=18,
            pos=[base_x + 22, 6],
            callback=self._on_heart_clicked
        )
        if constants.small_font_awesome_icon_font_id:
            dpg.bind_item_font(heart_btn, constants.small_font_awesome_icon_font_id)

        # Remove button
        dpg.add_button(
            label="×",
            tag=f"{self.tag_id}_remove",
            width=18,
            height=18,
            pos=[base_x + 44, 6],
            callback=self._on_remove_clicked
        )
    
    def _create_themes(self, text_color, bg_color):
        """Create normal and focused themes for the stock tag"""
        # Normal theme
        normal_theme_tag = f"normal_theme_{self.tag_id}"
        with dpg.theme(tag=normal_theme_tag):
            with dpg.theme_component(dpg.mvChildWindow):
                bg_tuple = tuple(bg_color + [255])
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple)
                dpg.add_theme_color(dpg.mvThemeCol_Border, [100, 100, 100, 255])
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
        
        # Focused theme (red border)
        focused_theme_tag = f"focused_theme_{self.tag_id}"
        with dpg.theme(tag=focused_theme_tag):
            with dpg.theme_component(dpg.mvChildWindow):
                bg_tuple = tuple(bg_color + [255])
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple)
                dpg.add_theme_color(dpg.mvThemeCol_Border, [255, 0, 0, 255])
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 3)
    
    def set_focus(self, focused: bool):
        """Set the focus state and update visual appearance"""
        global _focused_tag
        
        if focused:
            if _focused_tag and _focused_tag != self:
                _focused_tag.set_focus(False)
            _focused_tag = self
        elif _focused_tag == self:
            _focused_tag = None
        
        self.is_focused = focused
        
        # Update visual theme
        if self.is_focused:
            dpg.bind_item_theme(self.tag_id, f"focused_theme_{self.tag_id}")
        else:
            dpg.bind_item_theme(self.tag_id, f"normal_theme_{self.tag_id}")
    
    def update_cache_indicator(self):
        """Update the cache indicator in the tag"""
        if dpg.does_item_exist(f"{self.tag_id}_text"):
            # cache_indicator = "Fresh" if self.stock_data.is_cache_valid() else "Stale"
            display_text = f"{self.symbol}"
            dpg.set_value(f"{self.tag_id}_text", display_text)
    
    def refresh_data(self):
        """Refresh stock data from API"""
        print(f"🔄 Refreshing data for {self.symbol}...")
        try:
            # Get current chart tags
            from components.graph.graph_dpg import current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
            
            if current_stock_line_tag and current_x_axis_tag and current_y_axis_tag and current_plot_tag:
                # Use existing stockdx layer function to fetch fresh data
                from utils.stock_fetch_layer import fetch_stock_data
                fetch_stock_data(
                    self.symbol,
                    current_stock_line_tag,
                    current_x_axis_tag,
                    current_y_axis_tag,
                    current_plot_tag
                )
            else:
                print(f"❌ Chart tags not available for {self.symbol}")
            
            # Update cache indicator after refresh
            self.update_cache_indicator()
            
        except Exception as e:
            print(f"❌ Error refreshing {self.symbol}: {e}")
    
    def load_chart_from_cache(self):
        """Load chart data from cached DataFrame"""
        try:
            if self.stock_data.price_history is None:
                print(f"❌ No cached chart data for {self.symbol}")
                return False
            
            # Import the chart update function
            from components.graph.graph_dpg import current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
            from utils.stock_fetch_layer import _update_chart_with_data
            
            # Convert DataFrame to data format expected by chart updater
            df = self.stock_data.price_history
            data = {
                'close': df['close'].tolist(),
                'open': df['open'].tolist() if 'open' in df.columns else [],
                'high': df['high'].tolist() if 'high' in df.columns else [],
                'low': df['low'].tolist() if 'low' in df.columns else [],
                'volume': df['volume'].tolist() if 'volume' in df.columns else [],
            }
            
            # Update the chart
            _update_chart_with_data(data, current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag)
            
            print(f"📊 Chart loaded from cache for {self.symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading chart from cache: {e}")
            return False
                
        except Exception as e:
            print(f"❌ Error loading chart from cache: {e}")
            return False
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        self.is_favorited = not self.is_favorited
        
        # Update heart icon
        heart_icon = constants.ICON_HEART if self.is_favorited else constants.ICON_HEART_BROKEN
        if dpg.does_item_exist(f"{self.tag_id}_heart"):
            dpg.set_item_label(f"{self.tag_id}_heart", heart_icon)
        
        print(f"{'⭐' if self.is_favorited else '💔'} {self.symbol} favorite: {self.is_favorited}")
        
        # Call callback if provided
        if self.on_favorite:
            self.on_favorite(self.symbol, self.is_favorited)
    
    def remove(self):
        """Remove the stock tag"""
        global _focused_tag
        
        if _focused_tag == self:
            _focused_tag = None
        
        # Remove from tracking
        if self in _active_tags:
            _active_tags.remove(self)
        
        # Remove DPG component
        if dpg.does_item_exist(self.tag_id):
            dpg.delete_item(self.tag_id)
        
        print(f"🗑️ Removed {self.symbol} tag")
        
        # Call callback if provided
        if self.on_remove:
            self.on_remove(self.symbol)
    
    # Event handlers
    def _on_chart_clicked(self):
        """Handle chart button click"""
        print(f"📈 Chart clicked for {self.symbol}")
        self.set_focus(True)

        if self.on_chart_click:
            self.on_chart_click(self)
        else:
            # Default behavior: try to load chart
            if not self.stock_data.is_cache_valid():
                print(f"🔄 Cache expired for {self.symbol}, fetching fresh data...")
                self.refresh_data()
            else:
                print(f"📦 Using cached data for {self.symbol}")
                self.load_chart_from_cache()

    def _on_heart_clicked(self):
        """Handle heart button click"""
        self.toggle_favorite()
    
    def _on_remove_clicked(self):
        """Handle remove button click"""
        self.remove()
    
    # Getters
    def get_symbol(self) -> str:
        return self.symbol
    
    def get_company_name(self) -> str:
        return self.company_name
    
    def get_stock_data(self) -> StockData:
        return self.stock_data
    
    def is_favorite(self) -> bool:
        return self.is_favorited
    
    def is_tag_focused(self) -> bool:
        return self.is_focused

# =============================================================================
# CACHE MANAGEMENT
# =============================================================================

# Global cache and tracking
_stock_data_cache: Dict[str, StockData] = {}
_active_tags = []
_focused_tag: Optional[StockTag] = None

def get_cached_stock_data(symbol: str, company_name: str) -> StockData:
    """Get cached stock data or create new entry"""
    if symbol in _stock_data_cache:
        cached_data = _stock_data_cache[symbol]
        if cached_data.is_cache_valid():
            print(f"📦 Using cached data for {symbol}")
            return cached_data
        else:
            print(f"⏰ Cache expired for {symbol}")
    
    # Create new stock data entry
    stock_data = StockData(symbol=symbol, company_name=company_name)
    _stock_data_cache[symbol] = stock_data
    
    return stock_data

def update_stock_data_cache(symbol: str, stock_data: StockData):
    """Update the cache with fresh stock data"""
    _stock_data_cache[symbol] = stock_data
    
    # Update any active tags for this symbol
    for tag in _active_tags:
        if tag.symbol == symbol:
            tag.stock_data = stock_data
            tag.update_cache_indicator()

def get_stock_data_for_table(symbol: str) -> Dict[str, Any]:
    """Get formatted stock data for table display"""
    if symbol not in _stock_data_cache:
        return {}
    
    data = _stock_data_cache[symbol]
    
    # Format volume
    volume_str = "N/A"
    if data.volume and data.volume > 0:
        if data.volume >= 1_000_000_000:
            volume_str = f"{data.volume/1_000_000_000:.1f}B"
        elif data.volume >= 1_000_000:
            volume_str = f"{data.volume/1_000_000:.1f}M"
        elif data.volume >= 1_000:
            volume_str = f"{data.volume/1_000:.1f}K"
        else:
            volume_str = f"{data.volume:,}"
    
    # Format change
    change_str = "N/A"
    change_color = [255, 255, 255]
    if data.change is not None:
        change_str = f"+${data.change:.2f}" if data.change >= 0 else f"${data.change:.2f}"
        change_color = [0, 255, 0] if data.change >= 0 else [255, 0, 0]
    
    return {
        'symbol': data.symbol,
        'company_name': data.company_name,
        'current_price': f"${data.current_price:.2f}" if data.current_price else "N/A",
        'change': change_str,
        'change_color': change_color,
        'volume': volume_str,
        'revenue': data.revenue or "N/A",
        'net_income': data.net_income or "N/A",
        'cash_flow': data.cash_flow or "N/A",
        'is_cached': data.is_cache_valid(),
        'cache_status': data.get_cache_status()
    }

# =============================================================================
# PERSISTENCE
# =============================================================================

def save_cache_to_file():
    """Save cache to file for persistence"""
    try:
        cache_data = {}
        for symbol, stock_data in _stock_data_cache.items():
            cache_data[symbol] = stock_data.to_dict()
        
        with open('stock_cache.json', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"💾 Saved cache for {len(cache_data)} stocks")
        
    except Exception as e:
        print(f"❌ Error saving cache: {e}")

def load_cache_from_file():
    """Load cache from file"""
    try:
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        global _stock_data_cache
        for symbol, data in cache_data.items():
            _stock_data_cache[symbol] = StockData.from_dict(data)
        
        print(f"📂 Loaded cache for {len(cache_data)} stocks")
        
    except FileNotFoundError:
        print("📂 No cache file found, starting fresh")
    except Exception as e:
        print(f"❌ Error loading cache: {e}")

def cleanup_cache():
    """Clean up old cache entries"""
    global _stock_data_cache
    
    # Remove expired entries
    expired_keys = [
        symbol for symbol, data in _stock_data_cache.items()
        if not data.is_cache_valid()
    ]
    
    for key in expired_keys:
        del _stock_data_cache[key]
    
    # Limit cache size
    if len(_stock_data_cache) > MAX_CACHE_SIZE:
        # Remove oldest entries
        sorted_items = sorted(
            _stock_data_cache.items(),
            key=lambda x: x[1].last_updated or 0
        )
        
        items_to_remove = len(_stock_data_cache) - MAX_CACHE_SIZE
        for i in range(items_to_remove):
            del _stock_data_cache[sorted_items[i][0]]
    
    print(f"🧹 Cache cleanup complete, {len(_stock_data_cache)} entries remaining")

# =============================================================================
# PUBLIC API FUNCTIONS
# =============================================================================

def get_random_color_pair():
    """Get a random color pair for tag styling"""
    return random.choice(COLOR_PAIRS)

def create_stock_tag(symbol: str, company_name: str, parent: str = "tags_container") -> Optional[StockTag]:
    """
    Create a new stock tag or focus existing one
    
    Args:
        symbol: Stock symbol
        company_name: Company name
        parent: Parent container tag
        
    Returns:
        StockTag instance or None if creation failed
    """
    symbol = symbol.strip().upper()
    
    # Check if stock already exists
    existing_tag = find_tag_by_symbol(symbol)
    if existing_tag:
        existing_tag.set_focus(True)
        print(f"📊 Focused existing tag: {symbol}")
        return existing_tag
    
    # Create new tag
    try:
        tag = StockTag(
            symbol=symbol,
            parent=parent,
            company_name=company_name,
            on_favorite=lambda sym, fav: print(f"⭐ {sym} favorited: {fav}"),
            on_remove=lambda sym: print(f"🗑️ {sym} removed")
        )
        print(f"✅ Created new stock tag: {symbol}")
        return tag
        
    except Exception as e:
        print(f"❌ Error creating tag for {symbol}: {e}")
        return None

def get_all_active_tags() -> list:
    """Get all currently active stock tags"""
    return _active_tags.copy()

def get_focused_tag() -> Optional[StockTag]:
    """Get the currently focused stock tag"""
    return _focused_tag

def find_tag_by_symbol(symbol: str) -> Optional[StockTag]:
    """Find a tag by stock symbol"""
    symbol = symbol.upper().strip()
    for tag in _active_tags:
        if tag.symbol == symbol:
            return tag
    return None

def get_favorited_stocks() -> list:
    """Get list of favorited stock symbols"""
    return [tag.symbol for tag in _active_tags if tag.is_favorited]

def clear_all_tags():
    """Remove all stock tags"""
    global _focused_tag
    _focused_tag = None
    
    for tag in _active_tags[:]:  # Copy list to avoid modification during iteration
        tag.remove()
    
    _active_tags.clear()
    print("🧹 Cleared all stock tags")

def refresh_all_tags():
    """Refresh data for all active tags"""
    print(f"🔄 Refreshing {len(_active_tags)} stock tags...")
    for tag in _active_tags:
        tag.refresh_data()

# Initialize cache on module load
load_cache_from_file()