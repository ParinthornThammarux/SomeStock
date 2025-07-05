import dearpygui.dearpygui as dpg
from utils import constants
import random

stock_tags = []
focused_stock = None  # Track which stock is currently focused

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

def get_random_color_pair():
    """Get a random color pair [text_color, background_color]"""
    return random.choice(COLOR_PAIRS)

def get_color_pair_by_stock(symbol):
    """Get consistent color pair based on stock name hash"""
    hash_value = hash(symbol) % len(COLOR_PAIRS)
    return COLOR_PAIRS[hash_value]


class StockTag:
    def __init__(self, symbol, parent, company_name, on_favorite=None, on_remove=None):
        # Unfocus all existing tags BEFORE creating this one
        for tag in stock_tags:
            tag.set_focus(False)  # Use set_focus to update visuals properly
            
        self.symbol = symbol
        self.company_name = company_name # Store company name
        self.is_favorited = False
        self.is_focused = False  # Start as False, will be set to True after creation
        self.tag_id = f"tag_{symbol}"
        self.parent = parent
        self.on_favorite = on_favorite
        self.on_remove = on_remove
        self.create_box()
        # Auto-focus this new tag after creation
        self.set_focus(True)
        # NOTE: Don't call add_stock_to_table here - it should be called after the tag is added to stock_tags list
    
    def create_box(self):
        """Create the styled stock tag as a rectangular box"""
        text_color, bg_color = get_random_color_pair()
        
        # Create themes for normal and focused states
        self._create_themes(text_color, bg_color)
        
        with dpg.child_window(
            tag=self.tag_id,
            parent=self.parent,
            width=110,
            height=30,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            # Apply normal theme initially (will be changed to focused after creation)
            dpg.bind_item_theme(self.tag_id, f"normal_theme_{self.tag_id}")
            
            # Stock Name
            dpg.add_text(self.symbol, pos=[5, 5], color=text_color, tag=f"{self.tag_id}_font")

            # Chart button (push to chart)
            dpg.add_button(
                label=constants.ICON_CALCULATOR,
                tag=f"{self.tag_id}_chart",
                width=18,
                height=18,
                pos=[40, 6],
                callback=self.push_chart
            )
            if hasattr(constants, 'small_font_awesome_icon_font_id') and constants.small_font_awesome_icon_font_id:
                dpg.bind_item_font(f"{self.tag_id}_chart", constants.small_font_awesome_icon_font_id)

            # Heart button (favorite)
            dpg.add_button(
                label=constants.ICON_HEART,
                tag=f"{self.tag_id}_heart",
                width=18,
                height=18,
                pos=[62, 6],
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
                pos=[84, 6],
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
                    dpg.add_theme_color(dpg.mvThemeCol_Border, [255, 0, 0, 255])  # Red border
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 3)  # Thicker border
    
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
    
    def push_chart(self):
        """Push selected stock to graph"""
        print(f"🚀 Pushing {self.symbol} to chart...")
        
        self.set_focus(True)
        
        try:
            from utils.stockdex_layer import fetch_data_from_stockdx
            from components.graph_dpg import current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag
            
            fetch_data_from_stockdx(self.symbol, current_stock_line_tag, current_x_axis_tag, current_y_axis_tag, current_plot_tag)
            
        except ImportError as e:
            print(f"❌ Could not import required modules: {e}")
        except Exception as e:
            print(f"❌ Error pushing {self.symbol} to chart: {e}")
    
    def toggle_heart(self):
        """Toggle heart state between empty and filled"""
        self.is_favorited = not self.is_favorited
        if self.is_favorited:
            heart_label = constants.ICON_HEART  # Solid heart
        else:
            heart_label = constants.ICON_HEART_BROKEN  # Broken heart
        
        dpg.set_item_label(f"{self.tag_id}_heart", heart_label)
        
        print(f"{self.symbol} favorite status: {self.is_favorited}")
        if self.on_favorite:
            self.on_favorite(self.symbol, self.is_favorited)
    
    def remove_tag(self):
        """Remove the stock tag from UI"""
        global focused_stock
        
        # If this was the focused stock, clear the global reference
        if focused_stock == self:
            focused_stock = None
        
        dpg.delete_item(self.tag_id)
        print(f"Removed {self.symbol} tag")
        if self.on_remove:
            self.on_remove(self.symbol)
    
    def delete(self):
        """Manually delete the tag"""
        self.remove_tag()
    
    def set_favorite(self, favorited):
        """Programmatically set favorite state"""
        if self.is_favorited != favorited:
            self.toggle_heart()
    
    def get_favorite_status(self):
        """Get current favorite status"""
        return self.is_favorited
    
    def get_focus_status(self):
        """Get current focus status"""
        return self.is_focused
    
    def get_company_name(self):
        return self.company_name

# END OF CLASS DEF

def add_stock_tag(symbol, company_name, parent="tags_container"):
    """Add a new stock tag box"""
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
        print(f"✅ Added new stock tag: {symbol} (auto-focused)")
        add_stock_to_table(symbol)
        return tag
    else:
        # If stock already exists, just focus it
        existing_tag = find_tag_by_name(symbol)
        if existing_tag:
            existing_tag.set_focus(True)  # Focus the existing tag
            print(f"📊 Stock {symbol} already exists, focused it instead")
        return existing_tag

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
        tag.delete()
    stock_tags.clear()

def find_tag_by_name(symbol):
    """Find a tag by stock name"""
    for tag in stock_tags:
        if tag.symbol == symbol:
            print("TAG FOUND")
            return tag
    print("a")
    return None

def add_stock_to_table(symbol):
    """Add stock to the main graph table"""
    try:
        from components.graph_dpg import add_stock_to_portfolio_table
        add_stock_to_portfolio_table(symbol)
    except ImportError as e:
        print(f"Could not import graph_dpg: {e}")