import streamlit as st
import pandas as pd
import json
import os

# --- SECURITY / ACCESS CONTROL ---
if not st.session_state.get("logged_in") or st.session_state.get("current_role") != "admin":
    st.switch_page("app.py")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Price Manager | AL Zamin",
    page_icon="💰",
    layout="centered"
)

PRICES_FILE = "prices.json"

def load_prices():
    """Load prices permanently from JSON file."""
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r") as f:
            return json.load(f)
    else:
        # Default prices
        defaults = {
            "Burger": 150.0,
            "Chicken Burger": 250.0,
            "Small Shawarma": 150.0,
            "Big Shawarma": 200.0,
            "Double Anda Burger": 200.0,
            "Fries": 100.0,
            "Drink": 80.0
        }
        save_prices(defaults)
        return defaults

def save_prices(prices_dict):
    """Save prices permanently to JSON file."""
    with open(PRICES_FILE, "w") as f:
        json.dump(prices_dict, f, indent=4)

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
    <p style='text-align:center; color:#555;'>Update menu prices here. These will permanently save and calculate your invoices!</p>
</div>
""", unsafe_allow_html=True)

# --- PRICE EDITOR LOGIC ---
menu_prices = load_prices()

# Convert dict to DataFrame for the data editor
prices_df = pd.DataFrame(
    list(menu_prices.items()), 
    columns=["Item Name", "Price (PKR)"]
)

st.markdown("### 📋 Edit Menu Prices")
st.info("💡 Edit prices directly, add new items at the bottom, or select rows to delete them.")

# Editable table
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

# Save Button
if st.button("💾 Save Prices"):
    # Clean data (remove empty rows)
    cleaned_df = edited_df.dropna(subset=["Item Name"])
    cleaned_df = cleaned_df[cleaned_df["Item Name"].str.strip() != ""]
    
    # Convert back to dict and save
    new_prices_dict = dict(zip(cleaned_df["Item Name"], cleaned_df["Price (PKR)"]))
    save_prices(new_prices_dict)
    
    st.success("✅ Menu prices updated and saved permanently! Invoices will now use these prices.")
    st.balloons()