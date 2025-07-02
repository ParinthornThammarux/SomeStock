# components/example_page_b.py - Updated for new system

import dearpygui.dearpygui as dpg

def create_example_page_b_content(parent_tag):
    """
    Creates Page B content directly in the parent container.
    No child windows - just content.
    """
    print(f"Creating Page B content in parent: {parent_tag}")
    
    # Add some padding from the top
    dpg.add_spacer(height=50, parent=parent_tag)
    
    # Page B content
    with dpg.group(horizontal=False, parent=parent_tag):
        dpg.add_text("This is Example Page B", color=[255, 255, 255])
        dpg.add_separator()
        
        dpg.add_text("SUCCESS! Page B is now loaded and visible!", color=[0, 255, 0])
        dpg.add_separator()
        
        dpg.add_spacer(height=20)
        
        # Some interactive elements
        dpg.add_input_text(label="Page B Input", default_value="Type something here...")
        dpg.add_spacer(height=10)
        
        dpg.add_button(label="Page B Action", callback=lambda: print("Page B button clicked!"))
        dpg.add_spacer(height=20)
        
        dpg.add_text("More Page B content:", color=[200, 200, 200])
        dpg.add_text("• Feature 1", color=[150, 150, 255])
        dpg.add_text("• Feature 2", color=[150, 150, 255])
        dpg.add_text("• Feature 3", color=[150, 150, 255])
        
        dpg.add_spacer(height=30)
        
        # Button to go back to welcome
        dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150)

def go_to_welcome():
    """Go back to welcome page"""
    print("Going back to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

# Keep the old function for backward compatibility
def create_example_page_b(parent_tag):
    """Legacy function - redirects to new system"""
    return create_example_page_b_content(parent_tag)