import dearpygui.dearpygui as dpg
from utils import constants
import random

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
        self.is_visible = True  # Add this line
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
            width=110,
            height=30,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
            ):

            dpg.bind_item_theme(self.tag_id, theme_tag)
            
            # Stock Name
            dpg.add_text(self.stock_name, pos=[5, 5], color=text_color,tag=f"{self.tag_id}_font")

            # Eye button (show/hide)
            dpg.add_button(
                label=constants.ICON_EYE,
                tag=f"{self.tag_id}_eye",
                width=18,
                height=18,
                pos=[40, 6],  # First button position
                callback=self.toggle_eye
            )
            if hasattr(constants, 'font_awesome_icon_font_id') and constants.small_font_awesome_icon_font_id:
                dpg.bind_item_font(f"{self.tag_id}_eye", constants.small_font_awesome_icon_font_id)

            # Heart button (favorite)
            dpg.add_button(
                label=constants.ICON_HEART,
                tag=f"{self.tag_id}_heart",
                width=18,
                height=18,
                pos=[62, 6],  # Second button position
                callback=self.toggle_heart
            )
            if hasattr(constants, 'font_awesome_icon_font_id') and constants.small_font_awesome_icon_font_id:
                dpg.bind_item_font(f"{self.tag_id}_heart", constants.small_font_awesome_icon_font_id)

            # Remove button
            dpg.add_button(
                label="×",
                tag=f"{self.tag_id}_remove",
                width=18,
                height=18,
                pos=[114-30, 6],  # Third button position
                callback=self.remove_tag
            )
    
    def toggle_heart(self):
        """Toggle heart state between empty and filled"""
        self.is_favorited = not self.is_favorited
        if self.is_favorited:
            heart_label = constants.ICON_HEART  # Solid heart
        else:
            heart_label = constants.ICON_HEART_BROKEN  # Broken heart
        
        dpg.set_item_label(f"{self.tag_id}_heart", heart_label)
        
        print(f"{self.stock_name} favorite status: {self.is_favorited}")
        if self.on_favorite:
            self.on_favorite(self.stock_name, self.is_favorited)
    
    def toggle_eye(self):
        """Toggle eye state between visible and hidden"""
        
        # Toggle the visibility state
        self.is_visible = not getattr(self, 'is_visible', True)
        
        # Update the eye icon based on visibility state
        if self.is_visible:
            eye_label = constants.ICON_EYE
            print(f"{self.stock_name} is now visible")
        else:
            eye_label = constants.ICON_EYE_SLASH
            print(f"{self.stock_name} is now hidden")
        
        # Update the button label
        dpg.set_item_label(f"{self.tag_id}_eye", eye_label)
        
        # Optional: Change the appearance of the entire tag when hidden
        if hasattr(self, 'on_visibility_change') and self.on_visibility_change:
            self.on_visibility_change(self.stock_name, self.is_visible)
        
        # Optional: Fade out the tag when hidden
        if not self.is_visible:
            # Make the tag appear dimmed/faded
            dpg.set_item_theme(self.tag_id, self._get_dimmed_theme())
            dpg.configure_item(f"{self.tag_id}_text", color=[255, 255, 255])
        else:
            # Restore normal appearance
            dpg.set_item_theme(self.tag_id, self._get_normal_theme())

    def _get_dimmed_theme(self):
        """Create a dimmed theme for hidden stocks"""
        dimmed_theme_tag = f"dimmed_theme_{self.tag_id}"
        
        if not dpg.does_item_exist(dimmed_theme_tag):
            with dpg.theme(tag=dimmed_theme_tag):
                with dpg.theme_component(dpg.mvAll):
                    # Get original colors but make them dimmer
                    text_color, bg_color = get_color_pair_by_stock(self.stock_name)
                    
                    # Make colors more transparent/dimmed
                    dimmed_bg = [int(c * 0.5) for c in bg_color] + [128]  # 50% opacity
                    
                    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, dimmed_bg, category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, dimmed_bg, category=dpg.mvThemeCat_Core)
        
        return dimmed_theme_tag

    def _get_normal_theme(self):
        """Get the normal theme for the stock tag"""
        normal_theme_tag = f"normal_theme_{self.tag_id}"
        
        if not dpg.does_item_exist(normal_theme_tag):
            with dpg.theme(tag=normal_theme_tag):
                with dpg.theme_component(dpg.mvAll):
                    text_color, bg_color = get_color_pair_by_stock(self.stock_name)
                    bg_tuple = tuple(bg_color + [255])
                    
                    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, bg_tuple, category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_tuple, category=dpg.mvThemeCat_Core)
        
        return normal_theme_tag

    def get_visibility_status(self):
        """Get current visibility status"""
        return getattr(self, 'is_visible', True)

    def set_visibility(self, visible):
        """Programmatically set visibility state"""
        if self.get_visibility_status() != visible:
            self.toggle_eye()
        
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
    
# END OF CLASS DEF

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