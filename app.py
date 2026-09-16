import streamlit as st
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AL Zamin | Dashboard",
    page_icon="🍔",
    layout="centered"
)

# --- FILE CONFIGURATION ---
USERS_FILE = "users.json"

def load_users():
    """Loads users from a JSON file. Creates defaults if file doesn't exist."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        # Default users
        defaults = {
            "ayesha": {"password": "Ayesha@910", "role": "admin"},
            "staff": {"password": "staff@Alzamin", "role": "staff"}
        }
        save_users(defaults)
        return defaults

def save_users(users_dict):
    """Saves the user dictionary to the JSON file permanently."""
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)

# --- INITIALIZE SESSION STATE ---
def init_session_state():
    if "users" not in st.session_state:
        st.session_state["users"] = load_users()
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None
    if "current_role" not in st.session_state:
        st.session_state["current_role"] = None
    if "admin_msg" not in st.session_state:
        st.session_state["admin_msg"] = None

# --- CUSTOM CSS ---
def inject_custom_css(hide_sidebar=False):
    css = """
    <style>
    h1, h2, h3, h4, h5, h6 { color: #f47b20; font-family: 'Segoe UI', sans-serif; }
    .stApp { background-color: #fdfbf9; }
    .theme-card {
        background:#ffffff; border:1px solid #f1e4d8; border-radius:18px;
        padding:22px; box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;
    }
    .stButton>button, .stFormSubmitButton>button {
        background-color: #f47b20; color: white; border-radius: 8px; border: none; font-weight: bold;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover { background-color: #d96314; color: white; }
    """
    if hide_sidebar:
        css += """
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
        """
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)

# --- LOGIN PAGE ---
def login_page():
    inject_custom_css(hide_sidebar=True) 
    
    st.markdown("""
    <div class="theme-card" style="text-align: center;">
        <h1 style='margin-top:0;'>🥐 AL Zamin Portal 🍔</h1>
        <p style='color:#555;'>Please enter your credentials to access the system.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username").strip().lower()
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Secure Login", use_container_width=True)
        
        if submit:
            # Always reload users from file just in case it was updated
            st.session_state["users"] = load_users()
            users = st.session_state["users"]
            
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = username
                st.session_state["current_role"] = users[username]["role"]
                st.success("✅ Login successful! Loading dashboard...")
                st.rerun()
            else:
                st.error("❌ Access denied. Invalid username or password.")

# --- LOGOUT LOGIC ---
def logout():
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = None
    st.session_state["current_role"] = None
    st.rerun()

# --- ADMIN PANEL ---
def admin_panel():
    st.markdown("""
    <div class="theme-card">
        <h3 style='margin-top:0;'>⚙️ System Administration</h3>
        <p style='color:#555;'>Manage employee access and roles.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display persistent messages
    if st.session_state.get("admin_msg"):
        st.success(st.session_state["admin_msg"])
        st.session_state["admin_msg"] = None # Clear it after showing
    
    # 1. View Users
    st.markdown("#### 👥 Current Users")
    display_users = []
    for user, details in st.session_state["users"].items():
        display_users.append({"Username": user, "Role": details["role"].capitalize()})
    st.dataframe(display_users, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Add / Remove Users
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**➕ Add New User**")
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("New Username").strip().lower()
            new_password = st.text_input("New Password", type="password")
            new_role = st.selectbox("Assign Role", ["staff", "admin"])
            
            if st.form_submit_button("Add User", use_container_width=True):
                if not new_username or not new_password:
                    st.warning("⚠️ Username and Password are required.")
                elif new_username in st.session_state["users"]:
                    st.error(f"⚠️ User '{new_username}' already exists.")
                else:
                    # Update state AND save to file permanently
                    st.session_state["users"][new_username] = {"password": new_password, "role": new_role}
                    save_users(st.session_state["users"])
                    
                    st.session_state["admin_msg"] = f"✅ User '{new_username}' added permanently!"
                    st.rerun()
                    
    with col2:
        st.markdown("**🗑️ Remove User**")
        with st.form("remove_user_form"):
            user_to_remove = st.selectbox("Select User", options=list(st.session_state["users"].keys()))
            
            if st.form_submit_button("Remove User", use_container_width=True):
                if user_to_remove == "ayesha":
                    st.error("⚠️ Cannot remove the master admin ('ayesha').")
                elif user_to_remove == st.session_state["current_user"]:
                    st.error("⚠️ You cannot delete your own active account.")
                else:
                    # Delete from state AND save to file permanently
                    del st.session_state["users"][user_to_remove]
                    save_users(st.session_state["users"])
                    
                    st.session_state["admin_msg"] = f"✅ User '{user_to_remove}' removed permanently!"
                    st.rerun()

# --- MAIN LANDING PAGE ---
def landing_page():
    inject_custom_css(hide_sidebar=False)
    
    # Sidebar Profile & Logout
    st.sidebar.markdown(f"### 👤 Profile")
    st.sidebar.markdown(f"**User:** {st.session_state['current_user']}")
    st.sidebar.markdown(f"**Role:** {st.session_state['current_role'].capitalize()}")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.markdown("---")
    st.sidebar.info("👈 **Hint:** Use the sidebar menu above to navigate between system modules.")
    
    # Main Welcome Content
    st.markdown("""
    <div class="theme-card" style="text-align: center;">
        <h1 style='margin-top:0;'>👋 Welcome to AL Zamin Bakers & Fast Food</h1>
        <p style='color:#555; font-size: 16px;'>
            Your central hub for order automation, daily sales tracking, and restaurant insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show Admin Panel ONLY if role is admin
    if st.session_state["current_role"] == "admin":
        admin_panel()
    else:
        st.info("👋 Welcome Staff! Please use the sidebar to access the Order Input and Reports modules.")

# --- APP EXECUTION ---
def main():
    init_session_state()
    
    if not st.session_state["logged_in"]:
        login_page()
    else:
        landing_page()

if __name__ == "__main__":
    main()