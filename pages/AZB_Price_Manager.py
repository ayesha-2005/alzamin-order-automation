import streamlit as st
import pandas as pd

# --- SECURITY / ACCESS CONTROL ---
if not st.session_state.get("logged_in") or st.session_state.get("current_role") != "admin":
    st.switch_page("app.py")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Price Manager | AL Zamin",
    page_icon="💰",
    layout="centered"
)

# --- CUSTOM CSS (Theme Match) ---
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
    hr { border-color: #f1e4d8; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE MENU PRICES ---
if "menu_prices" not in st.session_state:
    st.session_state["menu_prices"] = {
        "Burger": 150.0,
        "Chicken Burger": 250.0,
        "Small Shawarma": 150.0,
        "Big Shawarma": 200.0,
        "Double Anda (Egg) Burger": 200.0
    }

# --- HEADER ---
st.markdown("""
<div class="theme-card">
    <h1 style='margin-top:0;'>💰 Price Management</h1>
    <p style='text-align:center; color:#555;'>Update menu prices dynamically. These prices will be used to calculate invoice totals.</p>
</div>
""", unsafe_allow_html=True)

# --- PRICE EDITOR LOGIC ---
# Convert dict to DataFrame for the data editor
prices_df = pd.DataFrame(
    list(st.session_state["menu_prices"].items()), 
    columns=["Item Name", "Price (PKR)"]
)

st.markdown("### 📋 Edit Menu Prices")
st.info("💡 You can edit prices directly, add new items by clicking the bottom row, or select rows to delete them.")

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
    # Convert DataFrame back to dictionary
    # Drop rows where item name might be empty
    cleaned_df = edited_df.dropna(subset=["Item Name"])
    cleaned_df = cleaned_df[cleaned_df["Item Name"].str.strip() != ""]
    
    # Save to session state
    new_prices_dict = dict(zip(cleaned_df["Item Name"], cleaned_df["Price (PKR)"]))
    st.session_state["menu_prices"] = new_prices_dict
    
    st.success("✅ Menu prices updated successfully! Invoices will now use these prices.")
    st.balloons()