import dearpygui.dearpygui as dpg

class StockTag:
    def __init__(self, stock_name, parent=None):
        self.stock_name = stock_name
        self.is_favorited = False
        self.tag_id = f"stock_tag_{stock_name}"
        self.parent = parent
        
    def toggle_favorite(self):
        """Toggle the favorite status and update the button text"""
        self.is_favorited = not self.is_favorited
        heart_text = "♥" if self.is_favorited else "♡"
        dpg.set_item_label(f"{self.tag_id}_heart", heart_text)
        print(f"{self.stock_name} favorite status: {self.is_favorited}")
    
    def remove_tag(self):
        """Remove this tag from the UI"""
        dpg.delete_item(self.tag_id)
        print(f"Removed {self.stock_name} tag")
    
    def create_tag(self, parent):
        """Create the tag UI element as a rectangular box"""
        with dpg.child_window(
            tag=self.tag_id,
            parent=parent,
            width=120,
            height=35,
            border=True,
            horizontal_scrollbar=False,
            no_scrollbar=True
        ):
            with dpg.group(horizontal=True):
                # Stock name label (centered)
                dpg.add_text(self.stock_name, pos=[5, 8])
                
                # Heart button (favorite toggle)
                heart_text = "♥" if self.is_favorited else "♡"
                dpg.add_button(
                    label=heart_text,
                    tag=f"{self.tag_id}_heart",
                    callback=lambda: self.toggle_favorite(),
                    width=20,
                    height=20,
                    pos=[75, 5]
                )
                
                # Remove button (cross)
                dpg.add_button(
                    label="×",
                    tag=f"{self.tag_id}_remove",
                    callback=lambda: self.remove_tag(),
                    width=20,
                    height=20,
                    pos=[97, 5]
                )

# Example usage and demo
def create_demo():
    dpg.create_context()
    
    # Create viewport
    dpg.create_viewport(title="Stock Tags Demo", width=600, height=400)
    
    # Stock tags list
    stock_tags = []
    
    def add_stock_tag():
        """Add a new stock tag"""
        stock_name = dpg.get_value("stock_input")
        if stock_name and stock_name not in [tag.stock_name for tag in stock_tags]:
            new_tag = StockTag(stock_name)
            new_tag.create_tag("tags_container")
            stock_tags.append(new_tag)
            dpg.set_value("stock_input", "")
    
    with dpg.window(label="Stock Tags", tag="main_window"):
        dpg.add_text("Stock Tag Manager")
        dpg.add_separator()
        
        # Input section
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Stock Name",
                tag="stock_input",
                hint="Enter stock symbol (e.g., AAPL)",
                callback=lambda: add_stock_tag() if dpg.get_key_state(dpg.mvKey_Return) else None
            )
            dpg.add_button(label="Add Tag", callback=add_stock_tag)
        
        dpg.add_separator()
        dpg.add_text("Your Stock Tags:")
        
        # Container for tags - horizontal layout
        with dpg.group(horizontal=True, tag="tags_container"):
            pass
        
        # Pre-populate with some example tags
        example_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        for stock in example_stocks:
            tag = StockTag(stock)
            tag.create_tag("tags_container")
            stock_tags.append(tag)
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

# Alternative version with custom styling for rectangular boxes
def create_styled_tag_box(stock_name, parent, on_favorite=None, on_remove=None):
    """Create a styled stock tag as a rectangular box"""
    tag_id = f"styled_tag_{stock_name}"
    
    with dpg.child_window(
        tag=tag_id,
        parent=parent,
        width=130,
        height=40,
        border=True,
        horizontal_scrollbar=False,
        no_scrollbar=True
    ):
        with dpg.group(horizontal=True):
            # Stock name
            dpg.add_text(f" {stock_name}", pos=[5, 10])
            
            # Heart button
            heart_btn = dpg.add_button(
                label="♡",
                width=20,
                height=20,
                pos=[80, 8],
                callback=lambda: toggle_heart(heart_btn, stock_name, on_favorite)
            )
            
            # Remove button
            dpg.add_button(
                label="×",
                width=20,
                height=20,
                pos=[102, 8],
                callback=lambda: remove_tag(tag_id, stock_name, on_remove)
            )

def toggle_heart(button_id, stock_name, callback=None):
    """Toggle heart state"""
    current_label = dpg.get_item_label(button_id)
    new_label = "♥" if current_label == "♡" else "♡"
    dpg.set_item_label(button_id, new_label)
    if callback:
        callback(stock_name, new_label == "♥")

def remove_tag(tag_id, stock_name, callback=None):
    """Remove tag"""
    dpg.delete_item(tag_id)
    if callback:
        callback(stock_name)

# Advanced version with wrapping layout
def create_wrapping_demo():
    """Demo with wrapping layout for multiple rows of stock boxes"""
    dpg.create_context()
    dpg.create_viewport(title="Stock Tags - Rectangular Boxes", width=800, height=500)
    
    stock_tags = []
    
    def add_stock_tag():
        stock_name = dpg.get_value("stock_input")
        if stock_name and stock_name not in [tag.stock_name for tag in stock_tags]:
            new_tag = StockTag(stock_name)
            new_tag.create_tag("tags_container")
            stock_tags.append(new_tag)
            dpg.set_value("stock_input", "")
    
    with dpg.window(label="Stock Tags - Rectangular Layout", tag="main_window"):
        dpg.add_text("Stock Tag Manager with Rectangular Boxes")
        dpg.add_separator()
        
        # Input section
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                label="Stock Name",
                tag="stock_input",
                hint="Enter stock symbol (e.g., AAPL)",
                callback=lambda: add_stock_tag() if dpg.get_key_state(dpg.mvKey_Return) else None
            )
            dpg.add_button(label="Add Tag", callback=add_stock_tag)
        
        dpg.add_separator()
        dpg.add_text("Your Stock Tags:")
        
        # Scrollable container for tags
        with dpg.child_window(height=300, border=True):
            with dpg.group(horizontal=True, tag="tags_container"):
                pass
        
        # Pre-populate with example tags
        example_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NFLX"]
        for stock in example_stocks:
            tag = StockTag(stock)
            tag.create_tag("tags_container")
            stock_tags.append(tag)
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    # Run the wrapping demo instead of the basic one
    create_wrapping_demo()