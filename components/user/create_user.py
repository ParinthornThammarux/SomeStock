# pages/user_management_page.py

import dearpygui.dearpygui as dpg
import hashlib
import random
import time
from utils import constants

def create_user_management_content(parent_tag):
    """
    Creates the user management page content directly in the parent container.
    Follows the same pattern as other pages in the app.
    """
    print(f"Creating user management content in parent: {parent_tag}")
    
    # Add some padding from the top
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Page title
    dpg.add_text("User Management", parent=parent_tag, color=[255, 255, 255])
    dpg.add_text("Create and manage user accounts", parent=parent_tag, color=[150, 150, 150])
    dpg.add_separator(parent=parent_tag)
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Create main content area with proper scrolling
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, border=False, no_scrollbar=False):
        
        # Create user section
        dpg.add_text("Create New User", color=[100, 200, 255])
        dpg.add_text("Set up new account credentials", color=[150, 150, 150])
        dpg.add_spacer(height=15)
        
        # Form container - centered layout
        with dpg.child_window(width=600, height=500, border=True):
            dpg.add_spacer(height=20)
            
            # Username section
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                with dpg.group(horizontal=False):
                    dpg.add_text("Username", color=[200, 200, 200])
                    dpg.add_input_text(hint="Enter username (3-20 characters)", width=400, tag="new_username",
                                     callback=validate_inputs)
                    dpg.add_text("", tag="username_status", color=[100, 255, 100])
            
            dpg.add_spacer(height=15)
            
            # Password section
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                with dpg.group(horizontal=False):
                    dpg.add_text("Password", color=[200, 200, 200])
                    dpg.add_input_text(hint="Enter password (minimum 6 characters)", width=400, tag="new_password",
                                     password=True, callback=validate_inputs)
                    dpg.add_text("", tag="password_status", color=[100, 255, 100])
            
            dpg.add_spacer(height=15)
            
            # Confirm Password section
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                with dpg.group(horizontal=False):
                    dpg.add_text("Confirm Password", color=[200, 200, 200])
                    dpg.add_input_text(hint="Re-enter password", width=400, tag="confirm_password",
                                     password=True, callback=validate_inputs)
                    dpg.add_text("", tag="confirm_status", color=[100, 255, 100])
            
            dpg.add_spacer(height=15)
            
            # PIN section
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                with dpg.group(horizontal=False):
                    dpg.add_text("Security PIN", color=[200, 200, 200])
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(hint="4-digit PIN", width=200, tag="new_pin",
                                         password=True, callback=validate_inputs)
                        dpg.add_spacer(width=10)
                        dpg.add_button(label="🎲 Random", callback=generate_pin, width=100, height=30)
                    dpg.add_text("", tag="pin_status", color=[100, 255, 100])
            
            dpg.add_spacer(height=25)
            
            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=100)
                dpg.add_button(label="CREATE USER", width=150, height=40, 
                             callback=create_user, tag="create_btn", enabled=False)
                dpg.add_spacer(width=20)
                dpg.add_button(label="CLEAR FORM", width=120, height=40,
                             callback=clear_form)
            
            dpg.add_spacer(height=20)
            
            # Status message
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                dpg.add_text("", tag="creation_message", wrap=500)
        
        dpg.add_spacer(height=20)
        
        # Requirements section
        dpg.add_text("Requirements & Guidelines", color=[255, 200, 100])
        dpg.add_spacer(height=10)
        
        with dpg.child_window(width=600, height=120, border=True):
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=20)
                with dpg.group(horizontal=False):
                    dpg.add_text("• Username: 3-20 characters, letters/numbers/underscore only", color=[180, 180, 180])
                    dpg.add_text("• Password: minimum 6 characters for security", color=[180, 180, 180])
                    dpg.add_text("• PIN: exactly 4 digits for additional security", color=[180, 180, 180])
                    dpg.add_text("• All fields are required to create an account", color=[180, 180, 180])
        
        dpg.add_spacer(height=30)
        
        # Navigation section
        dpg.add_text("Navigation", color=[200, 255, 200])
        dpg.add_spacer(height=10)
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Back to Welcome", callback=go_to_welcome, width=150, height=35)
            dpg.add_spacer(width=20)
            dpg.add_button(label="Go to Dashboard", callback=go_to_dashboard, width=150, height=35)

def validate_inputs():
    """Validate all form inputs and enable/disable create button"""
    username = dpg.get_value("new_username").strip()
    password = dpg.get_value("new_password")
    confirm = dpg.get_value("confirm_password")
    pin = str(dpg.get_value("new_pin")).strip()
    
    all_valid = True
    
    # Validate username
    if not username:
        dpg.set_value("username_status", "")
        all_valid = False
    elif len(username) < 3:
        dpg.set_value("username_status", "❌ Too short (minimum 3 characters)")
        dpg.configure_item("username_status", color=[255, 100, 100])
        all_valid = False
    elif len(username) > 20:
        dpg.set_value("username_status", "❌ Too long (maximum 20 characters)")
        dpg.configure_item("username_status", color=[255, 100, 100])
        all_valid = False
    elif not username.replace('_', '').isalnum():
        dpg.set_value("username_status", "❌ Letters, numbers, and underscore only")
        dpg.configure_item("username_status", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("username_status", "✅ Valid username")
        dpg.configure_item("username_status", color=[100, 255, 100])
    
    # Validate password
    if not password:
        dpg.set_value("password_status", "")
        all_valid = False
    elif len(password) < 6:
        dpg.set_value("password_status", "❌ Too short (minimum 6 characters)")
        dpg.configure_item("password_status", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("password_status", "✅ Valid password")
        dpg.configure_item("password_status", color=[100, 255, 100])
    
    # Validate password confirmation
    if not confirm:
        dpg.set_value("confirm_status", "")
        all_valid = False
    elif password != confirm:
        dpg.set_value("confirm_status", "❌ Passwords don't match")
        dpg.configure_item("confirm_status", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("confirm_status", "✅ Passwords match")
        dpg.configure_item("confirm_status", color=[100, 255, 100])
    
    # Validate PIN
    if not pin or pin == "0":
        dpg.set_value("pin_status", "")
        all_valid = False
    elif len(pin) != 4 or not pin.isdigit():
        dpg.set_value("pin_status", "❌ Must be exactly 4 digits")
        dpg.configure_item("pin_status", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("pin_status", "✅ Valid PIN")
        dpg.configure_item("pin_status", color=[100, 255, 100])
    
    # Enable/disable create button based on all validations
    if all_valid and username and password and confirm and len(pin) == 4:
        dpg.configure_item("create_btn", enabled=True)
    else:
        dpg.configure_item("create_btn", enabled=False)

def generate_pin():
    """Generate random 4-digit PIN"""
    pin = random.randint(1000, 9999)
    dpg.set_value("new_pin", str(pin))
    validate_inputs()
    print(f"Generated random PIN: {pin}")

def create_user():
    """Create the user account"""
    username = dpg.get_value("new_username").strip()
    password = dpg.get_value("new_password")
    pin = str(dpg.get_value("new_pin")).strip()
    
    try:
        # Hash passwords for security (you might want to use a more secure method)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        # Here you would save to your database/file
        # For demonstration, we'll just print and show success
        print(f"User created successfully:")
        print(f"  Username: {username}")
        print(f"  Password Hash: {password_hash[:20]}...")
        print(f"  PIN Hash: {pin_hash[:20]}...")
        
        # Show success message
        success_msg = f"✅ User '{username}' created successfully!\nAccount is ready to use."
        dpg.set_value("creation_message", success_msg)
        dpg.configure_item("creation_message", color=[100, 255, 100])
        
        # Disable the create button to prevent duplicate creation
        dpg.configure_item("create_btn", enabled=False)
        
        # Auto-clear form after 3 seconds (optional)
        # You could implement a timer here if desired
        
    except Exception as e:
        error_msg = f"❌ Error creating user: {str(e)}"
        dpg.set_value("creation_message", error_msg)
        dpg.configure_item("creation_message", color=[255, 100, 100])
        print(f"Error creating user: {e}")

def clear_form():
    """Clear all form fields"""
    dpg.set_value("new_username", "")
    dpg.set_value("new_password", "")
    dpg.set_value("confirm_password", "")
    dpg.set_value("new_pin", "")
    dpg.set_value("username_status", "")
    dpg.set_value("password_status", "")
    dpg.set_value("confirm_status", "")
    dpg.set_value("pin_status", "")
    dpg.set_value("creation_message", "")
    dpg.configure_item("create_btn", enabled=False)
    print("Form cleared")

def go_to_welcome():
    """Navigate back to welcome page"""
    print("Navigating to welcome page")
    from containers.container_content import show_page
    show_page("welcome")

def go_to_dashboard():
    """Navigate to dashboard/enhanced page"""
    print("Navigating to dashboard")
    from containers.container_content import show_page
    show_page("enhanced")