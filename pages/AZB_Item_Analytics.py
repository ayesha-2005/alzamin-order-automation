import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit as st
# Protect page + Enforce Role
if not st.session_state.get("logged_in") or st.session_state.get("current_role") != "admin":
    st.switch_page("app.py") # Kicks non-admins and logged-out users back to home
# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Item Analytics | AL Zamin",
    page_icon="🍕",
    layout="wide"
)

# --- CUSTOM CSS (Theme Match) ---
st.markdown("""
    <style>
    /* Primary text and header colors */
    h1, h2, h3, h4, h5, h6 {
        color: #f47b20;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Style st.metric to match the requested card design */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f1e4d8;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 30px rgba(244,123,32,0.08);
    }
    
    [data-testid="stMetricLabel"] {
        color: #555555;
        font-weight: 600;
        font-size: 16px;
    }
    
    [data-testid="stMetricValue"] {
        color: #f47b20;
        font-weight: bold;
    }
    
    /* Background adjustments */
    .stApp {
        background-color: #fdfbf9;
    }
    
    hr {
        border-color: #f1e4d8;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def assign_category(item_name):
    """Classifies an item into categories based on keywords."""
    item = str(item_name).lower()
    if any(kw in item for kw in ['burger', 'shawarma', 'pizza', 'fries', 'sandwich', 'wrap']):
        return 'Fast Food'
    elif any(kw in item for kw in ['cake', 'bread', 'donut', 'pastry', 'biscuit', 'cookie']):
        return 'Bakery'
    elif any(kw in item for kw in ['coke', 'tea', 'coffee', 'juice', 'shake', 'drink']):
        return 'Drinks'
    else:
        return 'Others'

def load_data():
    """Loads the orders data and handles missing files."""
    file_path = "orders.xlsx"
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return None
        
        # Clean and convert data types
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        df['Payment'] = pd.to_numeric(df['Payment'], errors='coerce').fillna(0)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Category'] = df['Item'].apply(assign_category)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- HEADER ---
st.title("🍕 Item Analytics Dashboard")
st.markdown(f"<p style='text-align: center; color: #888;'>Analytics generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN DASHBOARD LOGIC ---
df = load_data()

if df is None:
    st.info("👋 Welcome! It looks like there are no orders yet. Start adding orders in the Input module to see analytics here.")
else:
    # --- QUICK STATS METRICS ---
    total_items_sold = int(df['Quantity'].sum())
    paid_revenue = df[df['Payment Status'].str.lower() == 'paid']['Payment'].sum()
    unique_items = df['Item'].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🍔 Total Items Sold", value=f"{total_items_sold:,}")
    with col2:
        st.metric(label="💰 Total Item Revenue (Paid)", value=f"Rs {paid_revenue:,.2f}")
    with col3:
        st.metric(label="🍩 Unique Menu Items Sold", value=f"{unique_items}")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS SECTION 1: TOP ITEMS & REVENUE ---
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
            <h4 style='margin-top:0;'>📈 Top Selling Items (By Qty)</h4>
        </div>
        <br>
        """, unsafe_allow_html=True)
        top_items = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_items, color="#f47b20")

    with colB:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
            <h4 style='margin-top:0;'>💵 Revenue Per Item (Paid Only)</h4>
        </div>
        <br>
        """, unsafe_allow_html=True)
        # Filter for paid only, group by item, sum payment
        rev_per_item = df[df['Payment Status'].str.lower() == 'paid'].groupby('Item')['Payment'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(rev_per_item, color="#e6a668")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS SECTION 2: CATEGORY PERFORMANCE & REVENUE DISTRIBUTION ---
    colC, colD = st.columns(2)

    with colC:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
            <h4 style='margin-top:0;'>📦 Category Performance (Qty Sold)</h4>
        </div>
        <br>
        """, unsafe_allow_html=True)
        cat_performance = df.groupby('Category')['Quantity'].sum().sort_values(ascending=False)
        st.bar_chart(cat_performance, color="#f47b20")

    with colD:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
            <h4 style='margin-top:0;'>🥧 Revenue Distribution by Category</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Pie Chart using matplotlib (st.pyplot)
        cat_revenue = df[df['Payment Status'].str.lower() == 'paid'].groupby('Category')['Payment'].sum()
        
        if not cat_revenue.empty and cat_revenue.sum() > 0:
            fig, ax = plt.subplots(figsize=(6, 4))
            # Bakery/Fast food themed color palette
            colors = ['#f47b20', '#f1e4d8', '#f0a35c', '#d96314'] 
            
            # Formatting the pie chart
            wedges, texts, autotexts = ax.pie(
                cat_revenue, 
                labels=cat_revenue.index, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colors,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
            )
            
            # Styling text
            plt.setp(autotexts, size=10, weight="bold", color="black")
            plt.setp(texts, size=10)
            
            # Transparent background for seamless blending
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            st.pyplot(fig)
        else:
            st.info("No paid revenue available yet to show distribution.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS SECTION 3: DEMAND TREND ---
    st.markdown("""
    <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
        <h4 style='margin-top:0;'>⏳ Demand Trend (Items Sold Over Time)</h4>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    # Process trend data (aggregate by date to make chart readable)
    df_trend = df.copy()
    df_trend['Date'] = df_trend['Timestamp'].dt.date
    
    if not df_trend['Date'].isnull().all():
        trend_data = df_trend.groupby(['Date', 'Category'])['Quantity'].sum().unstack(fill_value=0)
        st.line_chart(trend_data)
    else:
        st.warning("Not enough timestamp data to generate a trend chart.")