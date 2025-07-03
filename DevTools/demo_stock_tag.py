import dearpygui.dearpygui as dpg

class StockTagBox:
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
        with dpg.child_window(
            tag=self.tag_id,
            parent=self.parent,
            width=130,
            height=40,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            # Stock name
            dpg.add_text(self.stock_name, pos=[8, 12])
            
            # Heart button
            dpg.add_button(
                label="♡",
                tag=f"{self.tag_id}_heart",
                width=20,
                height=20,
                pos=[80, 8],
                callback=self.toggle_heart
            )
            
            # Remove button
            dpg.add_button(
                label="×",
                tag=f"{self.tag_id}_remove",
                width=20,
                height=20,
                pos=[102, 8],
                callback=self.remove_tag
            )
    
    def toggle_heart(self):
        """Toggle heart state between empty and filled"""
        self.is_favorited = not self.is_favorited
        heart_label = "♥" if self.is_favorited else "♡"
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

def create_demo():
    """Demo application with stock tag boxes"""
    dpg.create_context()
    dpg.create_viewport(title="Stock Tags - Simple Class Demo", width=800, height=500)
    
    # Simple list to track tags
    stock_tags = []
    
    def add_stock_tag():
        """Add a new stock tag box"""
        stock_name = dpg.get_value("stock_input").strip().upper()
        
        # Check if stock already exists
        if stock_name and not any(tag.stock_name == stock_name for tag in stock_tags):
            tag = StockTagBox(
                stock_name, 
                "tags_container",
                on_favorite=lambda name, favorited: print(f"Callback: {name} favorited: {favorited}"),
                on_remove=lambda name: remove_from_list(name)
            )
            stock_tags.append(tag)
            dpg.set_value("stock_input", "")
    
    def remove_from_list(stock_name):
        """Remove tag from tracking list"""
        global stock_tags
        stock_tags = [tag for tag in stock_tags if tag.stock_name != stock_name]
    
    def show_favorites():
        """Show all favorited stocks"""
        favorites = [tag.stock_name for tag in stock_tags if tag.is_favorited]
        print(f"Favorited stocks: {favorites}")
    
    def remove_all_tags():
        """Remove all stock tags"""
        for tag in stock_tags[:]:  # Create copy to avoid modification during iteration
            tag.delete()
        stock_tags.clear()
    
    def on_enter_key():
        """Handle Enter key press in input field"""
        if dpg.get_key_state(dpg.mvKey_Return):
            add_stock_tag()
    
    with dpg.window(label="Stock Tags Manager", tag="main_window"):
        dpg.add_text("Stock Tag Manager - Simple Class")
        dpg.add_separator()
        
        # Input section
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Stock Symbol",
                tag="stock_input",
                hint="Enter stock symbol (e.g., AAPL)",
                callback=on_enter_key,
                width=200
            )
            dpg.add_button(label="Add Tag", callback=add_stock_tag)
        
        # Control buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Show Favorites", callback=show_favorites)
            dpg.add_button(label="Remove All", callback=remove_all_tags)
        
        dpg.add_separator()
        dpg.add_text("Your Stock Tags:")
        
        # Scrollable container for horizontal tag layout
        with dpg.child_window(height=300, border=True):
            with dpg.group(horizontal=True, tag="tags_container"):
                pass
        
        # Pre-populate with example stocks
        example_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        for stock in example_stocks:
            tag = StockTagBox(
                stock, 
                "tags_container",
                on_favorite=lambda name, favorited: print(f"Callback: {name} favorited: {favorited}"),
                on_remove=lambda name: remove_from_list(name)
            )
            stock_tags.append(tag)
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    create_demo()