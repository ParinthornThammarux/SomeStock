# pages/user_management_page.py

from datetime import datetime as dt
import json
import os
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
    dpg.add_text("User Management", parent=parent_tag, color=[255, 255, 255],indent=10)
    dpg.add_text("Create and manage user accounts", parent=parent_tag, color=[150, 150, 150],indent=10)
    dpg.add_separator(parent=parent_tag)
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Create main content area with proper scrolling
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, border=False, no_scrollbar=False,tag="main_create_user_box"):
        
        # Create user section
        dpg.add_text("Create New User", color=[100, 200, 255],indent = 70)
        dpg.add_text("Set up new account credentials", color=[150, 150, 150],indent = 70)
        dpg.add_separator(parent="main_create_user_box")

        dpg.add_spacer(height=15)
        
        # Form container - centered layout
        with dpg.child_window(width=-1, height=-1, border=False):
            with dpg.group(horizontal=True, indent=10):
                with dpg.group(horizontal= False):
                    dpg.add_spacer(height=20)
                    
                    # Username section
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Username", color=[200, 200, 200])
                            dpg.add_input_text(hint="Enter username (3-20 characters)", width=400, tag="new_username",
                                            callback=validate_inputs)
                            with dpg.group(horizontal=True):
                                dpg.add_text("", tag="username_icon", color=[100, 255, 100])
                                dpg.add_text("", tag="username_text", color=[100, 255, 100])

                    dpg.add_spacer(height=5)
                    
                    # Password section
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Password", color=[200, 200, 200])
                            dpg.add_input_text(hint="Enter password (minimum 6 characters)", width=400, tag="new_password",
                                            password=True, callback=validate_inputs)
                            with dpg.group(horizontal=True):
                                dpg.add_text("", tag="password_icon", color=[100, 255, 100])
                                dpg.add_text("", tag="password_text", color=[100, 255, 100])
                    
                    dpg.add_spacer(height=5)
                    
                    # Confirm Password section
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Confirm Password", color=[200, 200, 200])
                            dpg.add_input_text(hint="Re-enter password", width=400, tag="confirm_password",
                                            password=True, callback=validate_inputs)
                            with dpg.group(horizontal=True):
                                dpg.add_text("", tag="confirm_icon", color=[100, 255, 100])
                                dpg.add_text("", tag="confirm_text", color=[100, 255, 100])
                    
                    dpg.add_spacer(height=5)
                    
                    # PIN section
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Security PIN", color=[200, 200, 200])
                            with dpg.group(horizontal=True):
                                dpg.add_input_text(hint="4-digit PIN", width=400, tag="new_pin",
                                                password=True, callback=validate_inputs)
                                dpg.add_spacer(width=10)
                            with dpg.group(horizontal=True):
                                dpg.add_text("", tag="pin_icon", color=[100, 255, 100])
                                dpg.add_text("", tag="pin_text", color=[100, 255, 100])
                    
                    dpg.add_spacer(height=5)
                    
                    # Action buttons
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=100)
                        dpg.add_button(label="CREATE USER", width=150, height=40, 
                                    callback=create_user, tag="create_btn", enabled=False)
                        dpg.add_spacer(width=20)
                        dpg.add_button(label="CLEAR FORM", width=120, height=40,
                                    callback=clear_form)
                    
                    dpg.add_spacer(height=5)
                    
                    # Status message
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        dpg.add_text("", tag="creation_message", wrap=500)
                
                # Vertical Seperator
                dpg.add_spacer(width=20)
                
                with dpg.group():
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
        dpg.set_value("username_icon", "")
        dpg.set_value("username_text", "")
        all_valid = False
    elif len(username) < 3:
        dpg.set_value("username_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("username_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("username_icon", color=[255, 100, 100])
        
        dpg.set_value("username_text", " Too short (minimum 3 characters)")
        dpg.configure_item("username_text", color=[255, 100, 100])
        all_valid = False
    elif len(username) > 20:
        dpg.set_value("username_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("username_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("username_icon", color=[255, 100, 100])
        
        dpg.set_value("username_text", " Too long (maximum 20 characters)")
        dpg.configure_item("username_text", color=[255, 100, 100])
        all_valid = False
    elif not username.replace('_', '').isalnum():
        dpg.set_value("username_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("username_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("username_icon", color=[255, 100, 100])
        
        dpg.set_value("username_text", " Letters, numbers, and underscore only")
        dpg.configure_item("username_text", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("username_icon", constants.ICON_CHECK)
        dpg.bind_item_font("username_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("username_icon", color=[100, 255, 100])
        
        dpg.set_value("username_text", " Valid username")
        dpg.configure_item("username_text", color=[100, 255, 100])
    
    # Validate password
    if not password:
        dpg.set_value("password_icon", "")
        dpg.set_value("password_text", "")
        all_valid = False
    elif len(password) < 6:
        dpg.set_value("password_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("password_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("password_icon", color=[255, 100, 100])
        
        dpg.set_value("password_text", " Too short (minimum 6 characters)")
        dpg.configure_item("password_text", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("password_icon", constants.ICON_CHECK)
        dpg.bind_item_font("password_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("password_icon", color=[100, 255, 100])
        
        dpg.set_value("password_text", " Valid password")
        dpg.configure_item("password_text", color=[100, 255, 100])
    
    # Validate password confirmation
    if not confirm:
        dpg.set_value("confirm_icon", "")
        dpg.set_value("confirm_text", "")
        all_valid = False
    elif password != confirm:
        dpg.set_value("confirm_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("confirm_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("confirm_icon", color=[255, 100, 100])
        
        dpg.set_value("confirm_text", " Passwords don't match")
        dpg.configure_item("confirm_text", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("confirm_icon", constants.ICON_CHECK)
        dpg.bind_item_font("confirm_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("confirm_icon", color=[100, 255, 100])
        
        dpg.set_value("confirm_text", " Passwords match")
        dpg.configure_item("confirm_text", color=[100, 255, 100])

    # Validate PIN
    if not pin or pin == "0":
        dpg.set_value("pin_icon", "")
        dpg.set_value("pin_text", "")
        all_valid = False
    elif len(pin) != 4 or not pin.isdigit():
        dpg.set_value("pin_icon", constants.ICON_TIMES_CIRCLE)
        dpg.bind_item_font("pin_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("pin_icon", color=[255, 100, 100])
        
        dpg.set_value("pin_text", " Must be exactly 4 digits")
        dpg.configure_item("pin_text", color=[255, 100, 100])
        all_valid = False
    else:
        dpg.set_value("pin_icon", constants.ICON_CHECK)
        dpg.bind_item_font("pin_icon", constants.small_font_awesome_icon_font_id)
        dpg.configure_item("pin_icon", color=[100, 255, 100])
        
        dpg.set_value("pin_text", " Valid PIN")
        dpg.configure_item("pin_text", color=[100, 255, 100])
    
    # Enable/disable create button based on all validations
    if all_valid and username and password and confirm and len(pin) == 4:
        dpg.configure_item("create_btn", enabled=True)
    else:
        dpg.configure_item("create_btn", enabled=False)


def create_registration_form():
    """Create the registration form with separate icon and text containers"""
    
    # Username field
    dpg.add_text("Username")
    dpg.add_input_text(tag="new_username", callback=validate_inputs, hint="Enter username")
    with dpg.group(horizontal=True):
        dpg.add_text("", tag="username_icon")  # Icon container - Font Awesome font will be bound to this
        dpg.add_text("", tag="username_text")  # Text container - uses default font
    
    dpg.add_spacer(height=10)
    
    # Password field
    dpg.add_text("Password")
    dpg.add_input_text(tag="new_password", password=True, callback=validate_inputs, hint="Enter password (minimum 6 characters)")
    with dpg.group(horizontal=True):
        dpg.add_text("", tag="password_icon")  # Icon container
        dpg.add_text("", tag="password_text")  # Text container
    
    dpg.add_spacer(height=10)
    
    # Confirm password field
    dpg.add_text("Confirm Password")
    dpg.add_input_text(tag="confirm_password", password=True, callback=validate_inputs, hint="Re-enter password")
    with dpg.group(horizontal=True):
        dpg.add_text("", tag="confirm_icon")  # Icon container
        dpg.add_text("", tag="confirm_text")  # Text container
    
    dpg.add_spacer(height=10)
    
    # PIN field
    dpg.add_text("Security PIN")
    dpg.add_input_text(tag="new_pin", callback=validate_inputs, hint="4-digit PIN")
    with dpg.group(horizontal=True):
        dpg.add_text("", tag="pin_icon")  # Icon container
        dpg.add_text("", tag="pin_text")  # Text container
    
    dpg.add_spacer(height=20)
    
    # Create button
    dpg.add_button(label="Create Account", tag="create_btn", enabled=False, width=200)

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
        save_user_registration(username,password_hash,pin_hash)
        

        
        # Disable the create button to prevent duplicate creation
        dpg.configure_item("create_btn", enabled=False)
        
        # Auto-clear form after 3 seconds (optional)
        # You could implement a timer here if desired
        
    except Exception as e:
        error_msg = f"Error creating user: {str(e)}"
        dpg.set_value("creation_message", error_msg)
        dpg.configure_item("creation_message", color=[255, 100, 100])
        print(f"Error creating user: {e}")

def clear_form():
    """Clear all form fields after successful registration"""
    dpg.set_value("new_username", "")
    dpg.set_value("new_password", "")
    dpg.set_value("confirm_password", "")
    dpg.set_value("new_pin", "")
    
    # Clear status messages
    dpg.set_value("username_icon", "")
    dpg.set_value("username_text", "")
    dpg.set_value("password_icon", "")
    dpg.set_value("password_text", "")
    dpg.set_value("confirm_icon", "")
    dpg.set_value("confirm_text", "")
    dpg.set_value("pin_icon", "")
    dpg.set_value("pin_text", "")
    global success_msg
    success_msg = ""
    print("Form cleared")

def save_user_registration(username, password_hash, pin_hash):
    """Save user registration details to JSON file"""
    try:
        # Create user data
        user_data = {
            "username": username,
            "password_hash": password_hash,  # Store hashed password
            "pin_hash": pin_hash,  # Store hashed PIN
            "created_date": dt.now().isoformat(),
        }
        
        # Create registered_users directory if it doesn't exist
        users_dir = "registered_users"
        if not os.path.exists(users_dir):
            os.makedirs(users_dir)
            print(f"✅ Created directory: {users_dir}")
        
        # Load existing users or create new list
        users_file = os.path.join(users_dir, "users.json")
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
        else:
            users_data = {
                "users": [],
                "metadata": {
                    "total_users": 0,
                    "created_date": dt.now().isoformat(),
                }
            }
        
        # Check if username already exists
        existing_usernames = [user["username"] for user in users_data["users"]]
        if username in existing_usernames:
            # Show error message
            show_registration_result(False, username, "Username already exists!")
            return
        
        # Add new user
        users_data["users"].append(user_data)
        users_data["metadata"]["total_users"] = len(users_data["users"])
        
        # Save to file
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ User '{username}' registered successfully!")
        print(f"📁 Saved to: {os.path.abspath(users_file)}")
        
        # Also save individual user file for quick access
        individual_file = os.path.join(users_dir, f"{username}.json")
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)
        
        # Show success message and clear form
        show_registration_result(True, f"Account created successfully for {username}!")
        clear_form()
        
    except Exception as e:
        print(f"❌ Error saving user registration: {e}")
        import traceback
        traceback.print_exc()
        show_registration_result(False, f"Error creating account: {str(e)}")

def show_registration_result(success,username, message):
    """Show registration result message in a small centered window"""
    
    # Delete existing result window if it exists
    if dpg.does_item_exist("registration_result_window"):
        dpg.delete_item("registration_result_window")
    
    # Get viewport size for centering
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    
    # Window dimensions
    window_width = 400
    window_height = 120
    
    # Calculate center position
    pos_x = (viewport_width - window_width) // 2
    pos_y = (viewport_height - window_height) // 2
    
    # Create centered popup window
    with dpg.window(
        label="Registration Result",
        tag="registration_result_window",
        width=window_width,
        height=window_height,
        pos=[pos_x, pos_y],
        modal=True,
        no_resize=True,
        no_collapse=True,
        no_move=True
    ):
        dpg.add_spacer(height=10)
        
        # Center the content
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=20)  # Left padding
            
            if success:
                # Show success message
                success_msg = f"User '{username}' created successfully!\nAccount is ready to use."
                dpg.set_value("creation_message", success_msg)
                dpg.configure_item("creation_message", color=[100, 255, 100])
                
                # Success message
                with dpg.group(horizontal=True):
                    dpg.add_text(constants.ICON_CHECK_CIRCLE, color=[0, 255, 0], tag="result_popup_icon")
                    dpg.bind_item_font("result_popup_icon", constants.small_font_awesome_icon_font_id)
                    dpg.add_text(f" {message}", color=[0, 255, 0])
            else:
                # Error message
                with dpg.group(horizontal=True):
                    dpg.add_text(constants.ICON_TIMES_CIRCLE, color=[255, 100, 100], tag="result_popup_icon")
                    dpg.bind_item_font("result_popup_icon", constants.small_font_awesome_icon_font_id)
                    dpg.add_text(f" {message}", color=[255, 100, 100])
        
        dpg.add_spacer(height=15)
        
        # Center the OK button
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=(window_width - 80) // 2)  # Center button
            dpg.add_button(
                label="OK", 
                width=80, 
                height=30,
                callback=lambda: dpg.delete_item("registration_result_window")
            )


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
    
