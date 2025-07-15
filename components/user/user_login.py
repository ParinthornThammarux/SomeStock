# components/user/user_login.py

from datetime import datetime as dt
import json
import os
import dearpygui.dearpygui as dpg
import hashlib
from utils import constants

# Global variable to track login mode
login_mode = "pin"  # Can be "pin" or "password"

def create_user_login_content(parent_tag):
    """Creates the user login page with PIN/Password switcher"""
    global login_mode
    
    print(f"Creating user login content in parent: {parent_tag}")
    
    # Add some padding from the top
    dpg.add_spacer(height=20, parent=parent_tag)

    # Page title
    with dpg.group(horizontal=True, parent=parent_tag):
        with dpg.group():
            dpg.add_text("User Login", color=[255, 255, 255], indent=10)
            dpg.add_text("Sign in to your account", color=[150, 150, 150], indent=10)
        with dpg.group():
            dpg.add_spacer(height=20)
            if constants.Cur_User != "":
                with dpg.group(horizontal=True):
                    dpg.add_text("Currently logged in as ", indent=280)
                    dpg.add_text(f"{constants.Cur_User}", color=[255, 200, 100])
            else:
                dpg.add_text("Currently not logged in", indent=280)

    dpg.add_separator(parent=parent_tag)
    dpg.add_spacer(height=20, parent=parent_tag)
    
    # Create main content area
    with dpg.child_window(width=-1, height=-1, parent=parent_tag, border=False, no_scrollbar=False, tag="main_login_box"):
        
        # Login section header
        dpg.add_text("Login to Account", color=[100, 200, 255], indent=70)
        dpg.add_text("Enter your credentials to access your account", color=[150, 150, 150], indent=70)
        dpg.add_separator(parent="main_login_box")
        dpg.add_spacer(height=15)
        
        # Form container - centered layout
        with dpg.child_window(width=-1, height=-1, border=False):
            with dpg.group(horizontal=True, indent=10):
                with dpg.group(horizontal=False):
                    dpg.add_spacer(height=20)
                    
                    # Username section
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Username", color=[200, 200, 200])
                            dpg.add_input_text(hint="Enter your username", width=400, tag="login_username",callback=validate_login_inputs, on_enter=False)
                            with dpg.group(horizontal=True):
                                dpg.add_text("", tag="login_username_status", color=[150, 150, 150])

                    dpg.add_spacer(height=15)
                    
                    # Login mode switcher
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Login Method", color=[200, 200, 200])
                            with dpg.group(horizontal=True):
                                dpg.add_radio_button(["PIN (4 digits)", "Password"], 
                                                    default_value=0, tag="login_mode_selector",
                                                    callback=switch_login_mode, horizontal=True)
                    
                    dpg.add_spacer(height=10)
                    
                    # Dynamic login field (PIN or Password)
                    with dpg.group(horizontal=True, tag="login_field_container"):
                        dpg.add_spacer(width=50)
                        with dpg.group(horizontal=False, tag="login_field_group"):
                            create_login_field()
                    
                    dpg.add_spacer(height=20)
                    
                    # Action buttons
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=100)
                        dpg.add_button(label="LOGIN", width=150, height=40, 
                                     callback=attempt_login, tag="login_btn", enabled=False)
                        dpg.add_spacer(width=20)
                        dpg.add_button(label="CLEAR", width=120, height=40,
                                     callback=clear_login_form)
                    
                    dpg.add_spacer(height=10)
                    
                    # Status message
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=50)
                        dpg.add_text("", tag="login_message", wrap=500)
                
                # Vertical separator
                dpg.add_spacer(width=40)
                
                # Right side - User list
                with dpg.group():
                    # Available users section
                    dpg.add_text("Available Users", color=[255, 200, 100])
                    dpg.add_spacer(height=10)
                    
                    with dpg.child_window(width=300, height=200, border=True, tag="users_list_container"):
                        populate_users_list()
                    
                    dpg.add_spacer(height=20)
                    
                    # Quick actions
                    dpg.add_text("Quick Actions", color=[200, 255, 200])
                    dpg.add_spacer(height=10)
                    
                    with dpg.group(horizontal=False):
                        dpg.add_button(label="Refresh User List", callback=refresh_users_list, width=200, height=30)
                        dpg.add_spacer(height=5)
                        if constants.Cur_User != "":
                            dpg.add_button(label="Logout Current User", callback=logout_user, width=200, height=30)
                            dpg.add_spacer(height=5)
                    
                    dpg.add_spacer(height=20)

def create_login_field():
    """Create the appropriate login field based on current mode with unique tags"""
    global login_mode
    
    if login_mode == "pin":
        dpg.add_text("Security PIN", color=[200, 200, 200])
        dpg.add_input_text(hint="Enter your 4-digit PIN", width=400, tag="login_credential",
                          password=True, callback=validate_login_inputs)
        dpg.add_text("Enter your 4-digit security PIN", tag="login_credential_hint", 
                    color=[150, 150, 150])
    else:  # password mode
        dpg.add_text("Password", color=[200, 200, 200])
        dpg.add_input_text(hint="Enter your password", width=400, tag="login_credential",
                          password=True, callback=validate_login_inputs)
        dpg.add_text("Enter your account password", tag="login_credential_hint", 
                    color=[150, 150, 150])
    
    # Trigger validation after creating the field
    validate_login_inputs()

def switch_login_mode():
    """Switch between PIN and password login modes with proper cleanup"""
    global login_mode
    
    mode_value = dpg.get_value("login_mode_selector")
    old_mode = login_mode
    login_mode = "pin" if mode_value == 0 else "password"
    
    if old_mode != login_mode:
        print(f"Switching login mode from {old_mode} to {login_mode}")
        
        # Store current credential value to clear it after switching
        current_credential = ""
        if dpg.does_item_exist("login_credential"):
            current_credential = dpg.get_value("login_credential")
        
        # Clear and recreate the login field
        if dpg.does_item_exist("login_field_group"):
            dpg.delete_item("login_field_group", children_only=True)
            create_login_field()
        
        # Clear the credential field after mode switch
        if dpg.does_item_exist("login_credential"):
            dpg.set_value("login_credential", "")
        
        # Clear any previous validation messages
        dpg.set_value("login_message", "")
        
        # Re-validate inputs with the new mode
        validate_login_inputs()
        
        print(f"✅ Login mode switched to {login_mode}")

def validate_login_inputs():
    """Validate login inputs and enable/disable login button"""
    global login_mode
    
    username = dpg.get_value("login_username").strip() if dpg.does_item_exist("login_username") else ""
    credential = dpg.get_value("login_credential").strip() if dpg.does_item_exist("login_credential") else ""
    
    # Clear username status (no validation feedback)
    if dpg.does_item_exist("login_username_status"):
        dpg.set_value("login_username_status", "")
    
    # Simple username check - just needs to be non-empty
    username_valid = len(username) > 0
    
    # Validate credential based on mode
    credential_valid = False
    if credential:
        if login_mode == "pin":
            if len(credential) == 4 and credential.isdigit():
                credential_valid = True
                if dpg.does_item_exist("login_credential_hint"):
                    dpg.set_value("login_credential_hint", "✓ Valid PIN format")
                    dpg.configure_item("login_credential_hint", color=[100, 255, 100])
            else:
                if dpg.does_item_exist("login_credential_hint"):
                    dpg.set_value("login_credential_hint", "PIN must be exactly 4 digits")
                    dpg.configure_item("login_credential_hint", color=[255, 100, 100])
        else:  # password mode
            if len(credential) >= 6:
                credential_valid = True
                if dpg.does_item_exist("login_credential_hint"):
                    dpg.set_value("login_credential_hint", "✓ Valid password length")
                    dpg.configure_item("login_credential_hint", color=[100, 255, 100])
            else:
                if dpg.does_item_exist("login_credential_hint"):
                    dpg.set_value("login_credential_hint", "Password must be at least 6 characters")
                    dpg.configure_item("login_credential_hint", color=[255, 100, 100])
    else:
        if dpg.does_item_exist("login_credential_hint"):
            if login_mode == "pin":
                dpg.set_value("login_credential_hint", "Enter your 4-digit security PIN")
            else:
                dpg.set_value("login_credential_hint", "Enter your account password")
            dpg.configure_item("login_credential_hint", color=[150, 150, 150])
    
    # Enable login button if both fields are valid
    if username_valid and credential_valid:
        if dpg.does_item_exist("login_btn"):
            dpg.configure_item("login_btn", enabled=True)
            # print(f"Login button enabled - Username: '{username}', Credential valid: {credential_valid}")
    else:
        if dpg.does_item_exist("login_btn"):
            dpg.configure_item("login_btn", enabled=False)
            # print(f"Login button disabled - Username valid: {username_valid}, Credential valid: {credential_valid}")

def attempt_login():
    """Attempt to login with provided credentials with enhanced error handling"""
    global login_mode
    
    try:
        print("🔐 Login attempt started")
        
        if not dpg.does_item_exist("login_username") or not dpg.does_item_exist("login_credential"):
            print("❌ Login form elements not found")
            show_login_message("Login form error. Please refresh the page.", False)
            return
            
        username = dpg.get_value("login_username").strip()
        credential = dpg.get_value("login_credential").strip()
        
        print(f"🔐 Attempting login for user: '{username}' using {login_mode}")
        
        if not username or not credential:
            show_login_message("Please fill in all fields", False)
            return
        
        # Validate credential format before attempting login
        if login_mode == "pin":
            if len(credential) != 4 or not credential.isdigit():
                show_login_message("PIN must be exactly 4 digits", False)
                return
        else:
            if len(credential) < 6:
                show_login_message("Password must be at least 6 characters", False)
                return
        
        # Load user data
        user_data = load_user_data(username)
        if not user_data:
            show_login_message("Invalid username or credentials", False)
            return
        
        # Hash the provided credential
        credential_hash = hashlib.sha256(credential.encode()).hexdigest()
        
        # Check credentials based on login mode
        if login_mode == "pin":
            stored_hash = user_data.get("pin_hash", "")
            credential_type = "PIN"
        else:
            stored_hash = user_data.get("password_hash", "")
            credential_type = "password"
        
        if credential_hash == stored_hash:
            # Successful login
            print("Set current user to:", username)
            constants.Cur_User = username
            
            # Update welcome message if it exists
            if dpg.does_item_exist("user_welcome_message"):
                dpg.set_value("user_welcome_message", username)
            
            print(f"✅ User '{username}' logged in successfully using {credential_type}")
            show_login_message(f"Welcome back, {username}!", True)
            
            # Clear form after successful login
            clear_login_form()
            
            # Optionally redirect to dashboard after a short delay
            dpg.set_frame_callback(dpg.get_frame_count() + 60, lambda: go_to_dashboard())
            
        else:
            # Failed login
            print(f"❌ Login failed for '{username}' using {credential_type}")
            show_login_message(f"Invalid credentials. Please try again.", False)
            
            # Clear only the credential field
            if dpg.does_item_exist("login_credential"):
                dpg.set_value("login_credential", "")
            
            # Re-validate to update button state
            validate_login_inputs()
            
    except Exception as e:
        print(f"❌ Error during login attempt: {e}")
        import traceback
        traceback.print_exc()
        show_login_message("An error occurred during login. Please try again.", False)

def show_login_message(message, success=True):
    """Show login status message"""
    if dpg.does_item_exist("login_message"):
        dpg.set_value("login_message", message)
        if success:
            dpg.configure_item("login_message", color=[100, 255, 100])
        else:
            dpg.configure_item("login_message", color=[255, 100, 100])

def clear_login_form():
    """Clear all login form fields with proper error handling"""
    try:
        if dpg.does_item_exist("login_username"):
            dpg.set_value("login_username", "")
        
        if dpg.does_item_exist("login_credential"):
            dpg.set_value("login_credential", "")
        
        if dpg.does_item_exist("login_message"):
            dpg.set_value("login_message", "")
        
        if dpg.does_item_exist("login_username_status"):
            dpg.set_value("login_username_status", "")
        
        # Reset credential hint based on current mode
        if dpg.does_item_exist("login_credential_hint"):
            if login_mode == "pin":
                dpg.set_value("login_credential_hint", "Enter your 4-digit security PIN")
            else:
                dpg.set_value("login_credential_hint", "Enter your account password")
            dpg.configure_item("login_credential_hint", color=[150, 150, 150])
        
        # Disable login button
        if dpg.does_item_exist("login_btn"):
            dpg.configure_item("login_btn", enabled=False)
            
        print("✅ Login form cleared successfully")
        
    except Exception as e:
        print(f"❌ Error clearing login form: {e}")

def populate_users_list():
    """Populate the users list in the right panel"""
    if not dpg.does_item_exist("users_list_container"):
        return
    
    # Clear existing list
    dpg.delete_item("users_list_container", children_only=True)
    
    usernames = get_all_usernames()
    
    if not usernames:
        dpg.add_text("No users found", parent="users_list_container", color=[150, 150, 150])
        dpg.add_text("Create a new account to get started", parent="users_list_container", color=[150, 150, 150])
        return
    
    dpg.add_text(f"Found {len(usernames)} user(s):", parent="users_list_container", color=[200, 200, 200])
    dpg.add_spacer(height=10, parent="users_list_container")
    
    for username in usernames:
        with dpg.group(horizontal=True, parent="users_list_container"):
            # User icon and name
            if constants.font_awesome_icon_font_id:
                user_icon = dpg.add_text(constants.ICON_USER, color=[100, 200, 255])
                dpg.bind_item_font(user_icon, constants.small_font_awesome_icon_font_id)
            
            # Username button - clicking it fills the form
            user_btn = dpg.add_button(label=username, callback=lambda s, a, u: select_user(u), 
                                    user_data=username, width=150, height=25)
            
            # Current user indicator
            if username == constants.Cur_User:
                dpg.add_text("(current)", color=[255, 200, 100])

def select_user(username):
    """Select a user from the list and fill the username field"""
    if dpg.does_item_exist("login_username"):
        dpg.set_value("login_username", username)
        validate_login_inputs()
        print(f"Selected user: {username}")

def refresh_users_list():
    """Refresh the users list"""
    populate_users_list()
    print("Users list refreshed")

def logout_user():
    """Logout the current user"""
    if constants.Cur_User:
        old_user = constants.Cur_User
        constants.Cur_User = ""
        
        # Update welcome message if it exists
        if dpg.does_item_exist("user_welcome_message"):
            dpg.set_value("user_welcome_message", "")
        
        print(f"✅ User '{old_user}' logged out")
        show_login_message(f"Goodbye, {old_user}!", True)
        
        # Refresh the page to update the status
        from containers.container_content import show_page
        show_page("user_login")

def go_to_dashboard():
    """Navigate to dashboard/enhanced page"""
    print("Navigating to dashboard")
    from containers.container_content import show_page
    show_page("enhanced")

# Helper functions
def get_all_usernames():
    """Helper function to get all existing usernames by cycling through user files"""
    users_dir = "registered_users"
    usernames = []
    
    if not os.path.exists(users_dir):
        return usernames
    
    for filename in os.listdir(users_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(users_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    if 'username' in user_data:
                        usernames.append(user_data['username'])
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"⚠️ Warning: Could not read user file {filename}: {e}")
                continue
    
    return usernames

def user_exists(username):
    """Helper function to check if a specific username exists"""
    users_dir = "registered_users"
    user_file = os.path.join(users_dir, f"{username}.json")
    
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                return user_data.get('username') == username
        except (json.JSONDecodeError, KeyError):
            return False
    
    return False

def load_user_data(username):
    """Helper function to load a specific user's data"""
    users_dir = "registered_users"
    user_file = os.path.join(users_dir, f"{username}.json")
    
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error loading user data for {username}: {e}")
            return None
    
    return None