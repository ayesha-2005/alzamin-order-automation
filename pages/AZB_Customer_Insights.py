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
    page_title="Customer Insights | AL Zamin",
    page_icon="👤",
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
    
    /* Order History Table styling wrapper */
    .table-container {
        background:#ffffff;
        border:1px solid #f1e4d8;
        border-radius:18px;
        padding:22px;
        box-shadow:0 8px 30px rgba(244,123,32,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_data():
    """Loads the orders data and handles missing files/values."""
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
        
        # Standardize Payment Status for accurate filtering
        if 'Payment Status' in df.columns:
            df['Payment Status Clean'] = df['Payment Status'].astype(str).str.strip().str.lower()
        else:
            df['Payment Status Clean'] = 'unknown'
            
        # Ensure Customer column exists and clean it
        if 'Customer' in df.columns:
            df['Customer'] = df['Customer'].astype(str).str.strip()
            df = df[df['Customer'] != 'nan'] # Remove empty parses
        else:
            return None
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- HEADER ---
st.title("👤 Customer Insights Dashboard")
st.markdown(f"<p style='text-align: center; color: #888;'>Insights generated at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN DASHBOARD LOGIC ---
df = load_data()

if df is None:
    st.info("👋 Welcome! It looks like there are no orders yet. Start adding orders in the Input module to see customer insights here.")
else:
    # --- CUSTOMER SELECTOR ---
    unique_customers = sorted(df['Customer'].unique().tolist())
    
    if not unique_customers:
        st.info("No valid customers found in the dataset.")
    else:
        st.markdown("### 🔍 Select a Customer")
        selected_customer = st.selectbox("Search Customer", unique_customers, label_visibility="collapsed")
        
        # Filter dataframe for selected customer
        cust_df = df[df['Customer'] == selected_customer].copy()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- SUMMARY METRICS ---
        # Calculate Total Orders (based on unique timestamps to group multi-item orders)
        valid_timestamps = cust_df.dropna(subset=['Timestamp'])
        total_orders = valid_timestamps['Timestamp'].nunique() if not valid_timestamps.empty else len(cust_df)
        
        total_items = int(cust_df['Quantity'].sum())
        total_spent = cust_df[cust_df['Payment Status Clean'] == 'paid']['Payment'].sum()
        
        # Calculate Last Order Date
        if not pd.isnull(cust_df['Timestamp'].max()):
            last_order_date = cust_df['Timestamp'].max().strftime('%Y-%m-%d')
        else:
            last_order_date = "N/A"
            
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="🛍️ Total Orders", value=f"{total_orders}")
        with col2:
            st.metric(label="🍔 Total Items", value=f"{total_items:,}")
        with col3:
            st.metric(label="💳 Total Spent (Paid)", value=f"Rs {total_spent:,.2f}")
        with col4:
            st.metric(label="📅 Last Order Date", value=f"{last_order_date}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- CHARTS SECTION: FAVORITES & PAYMENT BEHAVIOR ---
        colA, colB = st.columns(2)
        
        with colA:
            st.markdown("""
            <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
                <h4 style='margin-top:0;'>⭐ Top 3 Favorite Items</h4>
            </div>
            <br>
            """, unsafe_allow_html=True)
            
            top_items = cust_df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(3)
            
            if not top_items.empty and top_items.sum() > 0:
                st.bar_chart(top_items, color="#f47b20")
            else:
                st.info("No item data available for this customer.")

        with colB:
            st.markdown("""
            <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08);">
                <h4 style='margin-top:0;'>📊 Payment Behavior</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Pie Chart using matplotlib (st.pyplot) for payment status
            status_counts = cust_df['Payment Status'].value_counts()
            
            if not status_counts.empty:
                fig, ax = plt.subplots(figsize=(6, 4))
                # Custom colors for Paid (Orange), Unpaid (Cream), Pending/Others (Light Orange)
                colors = ['#f47b20', '#f1e4d8', '#f0a35c', '#d96314'] 
                
                wedges, texts, autotexts = ax.pie(
                    status_counts, 
                    labels=status_counts.index, 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    colors=colors[:len(status_counts)],
                    wedgeprops={'edgecolor': '#f47b20', 'linewidth': 1}
                )
                
                plt.setp(autotexts, size=10, weight="bold", color="black")
                plt.setp(texts, size=10)
                
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                
                st.pyplot(fig)
            else:
                st.info("No payment status data available.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ORDER HISTORY TABLE ---
        st.markdown("""
        <div class="table-container">
            <h4 style='margin-top:0;'>📜 Complete Order History</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Prepare dataframe for display (filtering to requested columns)
        display_cols = ['Item', 'Quantity', 'Payment', 'Payment Status', 'Timestamp']
        # Check if columns actually exist before showing them to prevent KeyError
        actual_cols = [col for col in display_cols if col in cust_df.columns]
        
        history_df = cust_df[actual_cols].sort_values(by='Timestamp', ascending=False, na_position='last')
        
        # Format Timestamp for cleaner UI reading if it exists
        if 'Timestamp' in history_df.columns:
            history_df['Timestamp'] = history_df['Timestamp'].dt.strftime('%Y-%m-%d %I:%M %p')
            
        st.dataframe(
            history_df, 
            use_container_width=True,
            hide_index=True
        )