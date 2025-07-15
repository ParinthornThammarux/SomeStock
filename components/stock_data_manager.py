import dearpygui.dearpygui as dpg
from utils import constants
import random
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd

# Cache configuration
CACHE_DURATION = 60 * 10  # 2 minutes in seconds
MAX_CACHE_SIZE = 100  # Maximum number of stocks to cache

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

@dataclass
class StockData:
    """Comprehensive stock data container"""
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

class StockTag:
    """Visual stock tag with integrated data caching"""
    
    def __init__(self, symbol, parent, company_name, on_favorite=None, on_remove=None):
        # Unfocus all existing tags BEFORE creating this one
        for tag in stock_tags:
            tag.set_focus(False)
            
        self.symbol = symbol
        self.company_name = company_name
        self.is_favorited = False
        self.is_focused = False
        self.tag_id = f"tag_{symbol}"
        self.parent = parent
        self.on_favorite = on_favorite
        self.on_remove = on_remove
        
        # Initialize or get cached data
        self.stock_data = get_cached_stock_data(symbol, company_name)
        
        self.create_box()
        self.set_focus(True)
    
    def create_box(self):
        """Create the styled stock tag as a rectangular box"""
        text_color, bg_color = get_random_color_pair()
        
        # Create themes for normal and focused states
        self._create_themes(text_color, bg_color)
        symbol_len = len(self.symbol)
        shift = 7
        
        with dpg.child_window(
            tag=self.tag_id,
            parent=self.parent,
            width=110 + max(0,((symbol_len - 4) * shift)),
            height=30,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            # Apply normal theme initially
            dpg.bind_item_theme(self.tag_id, f"normal_theme_{self.tag_id}")
            
            # Stock Name
            dpg.add_text(f"{self.symbol}", pos=[5, 5], color=text_color, tag=f"{self.tag_id}_font")

            # Chart button
            dpg.add_button(
                label=constants.ICON_ARROW_UP,
                tag=f"{self.tag_id}_chart",
                width=18,
                height=18,
                pos=[40 + max(0,((symbol_len - 4) * shift)), 6],
                callback=self.push_chart
            )
            if hasattr(constants, 'small_font_awesome_icon_font_id') and constants.small_font_awesome_icon_font_id:
                dpg.bind_item_font(f"{self.tag_id}_chart", constants.small_font_awesome_icon_font_id)

            # Heart button
            dpg.add_button(
                label=constants.ICON_HEART,
                tag=f"{self.tag_id}_heart",
                width=18,
                height=18,
                pos=[62 + max(0,((symbol_len - 4) * shift)), 6],
                callback=self.toggle_heart
            )
            if hasattr(constants, 'small_font_awesome_icon_font_id') and constants.small_font_awesome_icon_font_id:
                dpg.bind_item_font(f"{self.tag_id}_heart", constants.small_font_awesome_icon_font_id)

            # Remove button
            dpg.add_button(
                label="×",
                tag=f"{self.tag_id}_remove",
                width=18,
                height=18,
                pos=[84 + max(0,((symbol_len - 4) * shift)), 6],
                callback=self.remove_tag
            )
    
    def _create_themes(self, text_color, bg_color):
        """Create normal and focused themes for the stock tag"""
        # Normal theme
        normal_theme_tag = f"normal_theme_{self.tag_id}"
        if not dpg.does_item_exist(normal_theme_tag):
            with dpg.theme(tag=normal_theme_tag):
                with dpg.theme_component(dpg.mvChildWindow):
                    bg_tuple = tuple(bg_color + [255])
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple)
                    dpg.add_theme_color(dpg.mvThemeCol_Border, [100, 100, 100, 255])
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
        
        # Focused theme (red border)
        focused_theme_tag = f"focused_theme_{self.tag_id}"
        if not dpg.does_item_exist(focused_theme_tag):
            with dpg.theme(tag=focused_theme_tag):
                with dpg.theme_component(dpg.mvChildWindow):
                    bg_tuple = tuple(bg_color + [255])
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple)
                    dpg.add_theme_color(dpg.mvThemeCol_Border, [255, 0, 0, 255])
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 3)
    
    def set_focus(self, focused):
        """Set the focus state and update visual appearance"""
        global focused_stock
        
        if focused:
            if focused_stock and focused_stock != self:
                focused_stock.set_focus(False)
            focused_stock = self
        elif focused_stock == self:
            focused_stock = None
        
        self.is_focused = focused
        
        if self.is_focused:
            dpg.bind_item_theme(self.tag_id, f"focused_theme_{self.tag_id}")
        else:
            dpg.bind_item_theme(self.tag_id, f"normal_theme_{self.tag_id}")
    
    def update_cache_indicator(self):
        """Update the cache indicator in the tag"""
        if dpg.does_item_exist(f"{self.tag_id}_font"):
            cache_indicator = "📶" if self.stock_data.is_cache_valid() else "🔄"
            dpg.set_value(f"{self.tag_id}_font", f"{cache_indicator} {self.symbol}")
    
    def push_chart(self):
        """Push selected stock to graph - SIMPLIFIED"""
        print(f"🚀 Pushing {self.symbol} to chart...")
        
        self.set_focus(True)
        
        try:
            # Check if we need to refresh data
            if not self.stock_data.is_cache_valid():
                print(f"📊 Cache expired for {self.symbol}, fetching fresh data...")
                # Use existing stockdx_layer function - it handles everything
                from utils.stockdex_layer import fetch_data_from_stockdx
                from components.graph_dpg import current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
                
                fetch_data_from_stockdx(self.symbol, current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag)
            else:
                print(f"📶 Using cached data for {self.symbol}")
                # Load from cache
                self.load_chart_from_cache()
            
        except Exception as e:
            print(f"❌ Error pushing {self.symbol} to chart: {e}")

    
    def load_chart_from_cache(self):
        """Load chart data from cached DataFrame"""
        try:
            if self.stock_data.price_history is None:
                print(f"❌ No cached chart data for {self.symbol}")
                return
            
            from components.graph_dpg import current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
            
            df = self.stock_data.price_history
            
            # Convert to DPG format
            x_data = list(range(len(df)))
            y_data = df['close'].tolist()
            
            # Update DPG chart
            if current_stock_line_tag and dpg.does_item_exist(current_stock_line_tag):
                dpg.set_value(current_stock_line_tag, [x_data, y_data])
                
                # Update axis limits
                if current_x_axis_tag and dpg.does_item_exist(current_x_axis_tag):
                    dpg.set_axis_limits(current_x_axis_tag, 0, len(x_data))
                
                if current_y_axis_tag and dpg.does_item_exist(current_y_axis_tag):
                    min_price = min(y_data) * 0.995
                    max_price = max(y_data) * 1.005
                    dpg.set_axis_limits(current_y_axis_tag, min_price, max_price)
                
                print(f"✅ Loaded chart from cache for {self.symbol}")
            
        except Exception as e:
            print(f"❌ Error loading chart from cache: {e}")
    
    def toggle_heart(self):
        """Toggle heart state"""
        self.is_favorited = not self.is_favorited
        if self.is_favorited:
            heart_label = constants.ICON_HEART
        else:
            heart_label = constants.ICON_HEART_BROKEN
        
        dpg.set_item_label(f"{self.tag_id}_heart", heart_label)
        
        print(f"{self.symbol} favorite status: {self.is_favorited}")
        if self.on_favorite:
            self.on_favorite(self.symbol, self.is_favorited)
    
    def remove_tag(self):
        """Remove the stock tag"""
        global focused_stock
        
        if focused_stock == self:
            focused_stock = None
        
        dpg.delete_item(self.tag_id)
        print(f"Removed {self.symbol} tag")
        if self.on_remove:
            self.on_remove(self.symbol)
    
    def get_stock_data(self) -> StockData:
        """Get the cached stock data"""
        return self.stock_data
    
    def get_company_name(self):
        return self.company_name
    
    def get_favorite_status(self):
        return self.is_favorited
    
    def get_focus_status(self):
        return self.is_focused

# Global variables
stock_tags = []
focused_stock = None
stock_data_cache: Dict[str, StockData] = {}

def get_random_color_pair():
    """Get a random color pair"""
    return random.choice(COLOR_PAIRS)

def get_cached_stock_data(symbol: str, company_name: str) -> StockData:
    """Get cached stock data or create new entry"""
    if symbol in stock_data_cache:
        cached_data = stock_data_cache[symbol]
        if cached_data.is_cache_valid():
            print(f"📶 Using cached data for {symbol}")
            return cached_data
        else:
            print(f"🔄 Cache expired for {symbol}, will fetch fresh data")
    
    # Create new stock data entry
    stock_data = StockData(symbol=symbol, company_name=company_name)
    stock_data_cache[symbol] = stock_data
    
    return stock_data

def add_stock_tag(symbol, company_name, parent="tags_container"):
    """Add a new stock tag - SIMPLIFIED"""
    symbol = symbol.strip().upper()
    
    # Check if stock already exists
    if symbol and not any(tag.symbol == symbol for tag in stock_tags):
        tag = StockTag(
            symbol, 
            parent,
            company_name,
            on_favorite=lambda name, favorited: print(f"Callback: {name} favorited: {favorited}"),
            on_remove=lambda name: remove_from_list(name)
        )
        stock_tags.append(tag)
        print(f"✅ Added new stock tag: {symbol}")
        
        # NOTE: Data fetching is handled by stockdx_layer when needed
        # No background fetching needed here
        
        return tag
    else:
        # If stock exists, focus it
        existing_tag = find_tag_by_name(symbol)
        if existing_tag:
            existing_tag.set_focus(True)
            print(f"📊 Focused existing stock: {symbol}")
        return existing_tag

def get_stock_data_for_table(symbol: str) -> Dict[str, Any]:
    """Get formatted stock data for table display"""
    if symbol not in stock_data_cache:
        return {}
    
    data = stock_data_cache[symbol]
    
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
        'is_cached': data.is_cache_valid()
    }

def add_stock_to_table(symbol):
    """Add stock to the main graph table"""
    try:
        from components.graph_dpg import add_stock_to_portfolio_table
        add_stock_to_portfolio_table(symbol)
    except ImportError as e:
        print(f"Could not import graph_dpg: {e}")

def save_cache_to_file():
    """Save cache to file for persistence"""
    try:
        cache_data = {}
        for symbol, stock_data in stock_data_cache.items():
            cache_data[symbol] = stock_data.to_dict()
        
        with open('stock_cache.json', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"✅ Saved cache for {len(cache_data)} stocks")
        
    except Exception as e:
        print(f"❌ Error saving cache: {e}")

def load_cache_from_file():
    """Load cache from file"""
    try:
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        global stock_data_cache
        for symbol, data in cache_data.items():
            stock_data_cache[symbol] = StockData.from_dict(data)
        
        print(f"✅ Loaded cache for {len(cache_data)} stocks")
        
    except FileNotFoundError:
        print("📋 No cache file found, starting fresh")
    except Exception as e:
        print(f"❌ Error loading cache: {e}")

def cleanup_cache():
    """Clean up old cache entries"""
    global stock_data_cache
    
    # Remove expired entries
    expired_keys = [
        symbol for symbol, data in stock_data_cache.items()
        if not data.is_cache_valid()
    ]
    
    for key in expired_keys:
        del stock_data_cache[key]
    
    # Limit cache size
    if len(stock_data_cache) > MAX_CACHE_SIZE:
        # Remove oldest entries
        sorted_items = sorted(
            stock_data_cache.items(),
            key=lambda x: x[1].last_updated or 0
        )
        
        items_to_remove = len(stock_data_cache) - MAX_CACHE_SIZE
        for i in range(items_to_remove):
            del stock_data_cache[sorted_items[i][0]]
    
    print(f"🧹 Cache cleanup complete, {len(stock_data_cache)} entries remaining")

# Helper functions (keeping original interface)
def remove_from_list(symbol):
    """Remove tag from tracking list"""
    global stock_tags
    stock_tags = [tag for tag in stock_tags if tag.symbol != symbol]

def get_all_stock_tags():
    """Get all current stock tags"""
    return stock_tags

def get_favorited_stocks():
    """Get list of favorited stock names"""
    return [tag.symbol for tag in stock_tags if tag.is_favorited]

def get_focused_stock():
    """Get the currently focused stock name"""
    global focused_stock
    return focused_stock.symbol if focused_stock else None

def clear_all_tags():
    """Remove all stock tags"""
    global focused_stock
    focused_stock = None
    
    for tag in stock_tags[:]:
        tag.remove_tag()
    stock_tags.clear()

def find_tag_by_name(symbol):
    """Find a tag by stock symbol"""
    for tag in stock_tags:
        if tag.symbol == symbol:
            return tag
    return None

# Initialize cache on module load
load_cache_from_file()