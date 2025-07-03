import dearpygui.dearpygui as dpg
from utils import constants
import random

# Define stock_tags globally in this module
stock_tags = []

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

def get_color_pair_by_stock(stock_name):
    """Get consistent color pair based on stock name hash"""
    hash_value = hash(stock_name) % len(COLOR_PAIRS)
    return COLOR_PAIRS[hash_value]


class StockTag:
    def __init__(self, stock_name, parent, on_favorite=None, on_remove=None):
        self.stock_name = stock_name
        self.is_favorited = False
        self.tag_id = f"tag_{stock_name}"
        self.parent = parent
        self.on_favorite = on_favorite
        self.on_remove = on_remove
        self.create_box()
    
    def create_box(self):
        """Create the styled stock tag as a rectangular box"""
        text_color, bg_color = get_color_pair_by_stock(self.stock_name)
        
        # Create a unique theme for this tag's background
        theme_tag = f"theme_{self.tag_id}"
        
        with dpg.theme() as theme_tag:
            with dpg.theme_component(dpg.mvAll):
                # Convert bg_color [r,g,b] to (r,g,b,255) tuple
                bg_tuple = tuple(bg_color + [255])
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, bg_tuple, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple, category=dpg.mvThemeCat_Core)
    

        with dpg.child_window(
            tag=self.tag_id,
            parent=self.parent,
            width=100,
            height=30,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            # Apply the theme to this specific child window
            dpg.bind_item_theme(self.tag_id, theme_tag)
            
            
            # Stock name
            dpg.add_text(self.stock_name, pos=[8, 5], color=text_color)

            # Heart button
            dpg.add_button(
                label=constants.ICON_HEART,
                tag=f"{self.tag_id}_heart",
                width=20,
                height=20,
                pos=[50, 5],
                callback=self.toggle_heart
            )
            
            # Remove button
            dpg.add_button(
                label="×",
                tag=f"{self.tag_id}_remove",
                width=20,
                height=20,
                pos=[72, 5],
                callback=self.remove_tag
            )
    
    def toggle_heart(self):
        """Toggle heart state between empty and filled"""
        self.is_favorited = not self.is_favorited
        heart_label = constants.ICON_HEART_FILLED if self.is_favorited else constants.ICON_HEART
        dpg.set_item_label(f"{self.tag_id}_heart", heart_label)
        
        print(f"{self.stock_name} favorite status: {self.is_favorited}")
        if self.on_favorite:
            self.on_favorite(self.stock_name, self.is_favorited)
    
    def remove_tag(self):
        """Remove the stock tag from UI"""
        dpg.delete_item(self.tag_id)
        print(f"Removed {self.stock_name} tag")
        if self.on_remove:
            self.on_remove(self.stock_name)
    
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

def add_stock_tag(stock_name, parent="tags_container"):
    """Add a new stock tag box"""
    stock_name = stock_name.strip().upper()
    
    # Check if stock already exists
    if stock_name and not any(tag.stock_name == stock_name for tag in stock_tags):
        tag = StockTag(
            stock_name, 
            parent,
            on_favorite=lambda name, favorited: print(f"Callback: {name} favorited: {favorited}"),
            on_remove=lambda name: remove_from_list(name)
        )
        stock_tags.append(tag)
        return tag
    return None

def remove_from_list(stock_name):
    """Remove tag from tracking list"""
    global stock_tags
    stock_tags = [tag for tag in stock_tags if tag.stock_name != stock_name]

def get_all_stock_tags():
    """Get all current stock tags"""
    return stock_tags

def get_favorited_stocks():
    """Get list of favorited stock names"""
    return [tag.stock_name for tag in stock_tags if tag.is_favorited]

def clear_all_tags():
    """Remove all stock tags"""
    for tag in stock_tags[:]:  # Create copy to avoid modification during iteration
        tag.delete()
    stock_tags.clear()

def find_tag_by_name(stock_name):
    """Find a tag by stock name"""
    for tag in stock_tags:
        if tag.stock_name == stock_name:
            return tag
    return None