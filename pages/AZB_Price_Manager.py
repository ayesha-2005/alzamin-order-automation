import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Protect page
if not st.session_state.get("logged_in") or st.session_state.get("current_role") != "admin":
    st.switch_page("app.py")

# Ensure db is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Price Manager | AL Zamin",
    page_icon="💰",
    layout="centered"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 { color: #f47b20; font-family: 'Segoe UI', sans-serif; text-align: center; }
    .stApp { background-color: #fdfbf9; }
    .theme-card {
        background:#ffffff; border:1px solid #f1e4d8; border-radius:18px;
        padding:22px; box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #f47b20; color: white; border-radius: 8px; border: none;
        padding: 10px 24px; font-weight: bold; width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #d96314; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="theme-card">
    <h1 style='margin-top:0;'>💰 Price Management</h1>
    <p style='text-align:center; color:#555;'>Update menu prices or remove unavailable items. Changes sync permanently to Supabase!</p>
</div>
""", unsafe_allow_html=True)

# Pull fresh items from Supabase
menu_prices = db.get_menu_items()

# --- QUICK DELETE SECTION FOR UNAVAILABLE ITEMS ---
if menu_prices:
    st.markdown("### 🗑️ Remove Unavailable Item")
    with st.form("quick_delete_form"):
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            item_to_delete = st.selectbox("Select item to remove from menu", options=list(menu_prices.keys()), label_visibility="collapsed")
        with col_del2:
            delete_submitted = st.form_submit_button("Delete Item")
            
        if delete_submitted:
            if item_to_delete in menu_prices:
                del menu_prices[item_to_delete]
                db.sync_menu_items(menu_prices)
                st.success(f"✅ '{item_to_delete}' has been removed from the menu permanently!")
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- PRICE EDITOR TABLE ---
prices_df = pd.DataFrame(
    list(menu_prices.items()), 
    columns=["Item Name", "Price (PKR)"]
)

st.markdown("### 📋 Edit Menu Prices & Add Items")
st.info("💡 Edit prices directly, add new items at the bottom row, or delete rows via the table.")

edited_df = st.data_editor(
    prices_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Item Name": st.column_config.TextColumn("Item Name", required=True),
        "Price (PKR)": st.column_config.NumberColumn("Price (PKR)", min_value=0.0, step=10.0, required=True)
    }
)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("💾 Save All Changes"):
    cleaned_df = edited_df.dropna(subset=["Item Name"])
    cleaned_df = cleaned_df[cleaned_df["Item Name"].str.strip() != ""]
    
    new_prices_dict = dict(zip(cleaned_df["Item Name"], cleaned_df["Price (PKR)"]))
    
    # Sync securely to DB (handles both adds, updates, and table deletions)
    db.sync_menu_items(new_prices_dict)
    
    st.success("✅ Menu prices updated and saved permanently to Supabase!")
    st.balloons()