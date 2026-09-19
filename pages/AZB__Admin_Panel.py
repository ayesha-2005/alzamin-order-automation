import streamlit as st
import pandas as pd
import os
import io
import db
from datetime import datetime

# Protect page + Enforce Role
if not st.session_state.get("logged_in") or st.session_state.get("current_role") != "admin":
    st.switch_page("app.py") # Kicks non-admins and logged-out users back to home
# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Admin Panel | AL Zamin",
    page_icon="⚙️",
    layout="wide"
)

# --- CUSTOM CSS (Theme Match) ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 {
        color: #f47b20;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background-color: #fdfbf9;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f1e4d8;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 30px rgba(244,123,32,0.08);
    }
    [data-testid="stMetricLabel"] { color: #555555; font-weight: 600; font-size: 16px; }
    [data-testid="stMetricValue"] { color: #f47b20; font-weight: bold; }
    
    /* Button & Download Styling */
    .stButton>button, .stDownloadButton>button {
        background-color: #f47b20;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #d96314;
        color: white;
        box-shadow: 0 4px 12px rgba(244,123,32,0.2);
    }
    hr { border-color: #f1e4d8; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=10)
def load_data():
    df = db.get_all_orders_df()
    if df is None or df.empty:
        return None
    try:
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        df['Payment'] = pd.to_numeric(df['Payment'], errors='coerce').fillna(0)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        if 'Customer' in df.columns:
            df['Customer'] = df['Customer'].astype(str).str.strip()
            df = df[df['Customer'] != 'nan']
        if 'Payment Status' in df.columns:
            df['Payment Status Clean'] = df['Payment Status'].astype(str).str.strip().str.title()
        else:
            df['Payment Status Clean'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def clear_all_orders():
    """Clears orders from Supabase table."""
    try:
        db.supabase.table("orders").delete().neq("id", 0).execute()
        load_data.clear()
    except Exception as e:
        st.error(f"Error clearing database: {e}")

def convert_df_to_excel(df):
    """Converts a pandas DataFrame to an Excel byte string in memory."""
    output = io.BytesIO()
    # using default pandas to_excel (openpyxl or xlsxwriter under the hood)
    with pd.ExcelWriter(output, engine='xlsxwriter' if 'xlsxwriter' in pd.options.io.excel.xlsx.writer else None) as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')
    processed_data = output.getvalue()
    return processed_data

# --- HEADER ---
st.title("⚙️ Admin Panel")
st.markdown(f"<p style='text-align: center; color: #888;'>Last action performed at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN DASHBOARD LOGIC ---
df = load_data()

if df is None:
    st.info("👋 The database is currently empty. Orders will appear here once submitted in the Input module.")
    if st.button("🔄 Refresh Application"):
        st.rerun()
else:
    tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Full Database", "🔍 Filter Tools", "⚠️ Unpaid Orders", "🛠️ System & Export"])
    
    # === TAB 1: FULL DATABASE ===
    with tab1:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;">
            <h3 style='margin-top:0;'>📚 Complete Order Database</h3>
            <p style='text-align:center; color:#555;'>Click any column header to sort the data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        display_df = df.drop(columns=['Payment Status Clean'], errors='ignore')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # === TAB 2: FILTER TOOLS ===
    with tab2:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;">
            <h3 style='margin-top:0;'>🔎 Advanced Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        colA, colB, colC = st.columns(3)
        with colA:
            customer_list = ['All'] + sorted(df['Customer'].unique().tolist())
            selected_customer = st.selectbox("👤 Customer", customer_list)
        with colB:
            status_list = ['All'] + sorted(df['Payment Status Clean'].unique().tolist())
            selected_status = st.selectbox("💳 Payment Status", status_list)
        with colC:
            valid_dates = df.dropna(subset=['Timestamp'])
            if not valid_dates.empty:
                min_date = valid_dates['Timestamp'].min().date()
                max_date = valid_dates['Timestamp'].max().date()
            else:
                min_date, max_date = datetime.today().date(), datetime.today().date()
            selected_dates = st.date_input("📅 Date Range", [min_date, max_date])

        # Apply Filters
        filtered_df = df.copy()
        if selected_customer != 'All':
            filtered_df = filtered_df[filtered_df['Customer'] == selected_customer]
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['Payment Status Clean'] == selected_status]
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered_df = filtered_df[
                (filtered_df['Timestamp'].dt.date >= start_date) & 
                (filtered_df['Timestamp'].dt.date <= end_date)
            ]
            
        st.markdown(f"**Found {len(filtered_df)} matching records.**")
        export_filtered_df = filtered_df.drop(columns=['Payment Status Clean'], errors='ignore')
        st.dataframe(export_filtered_df, use_container_width=True, hide_index=True)

    # === TAB 3: UNPAID ORDERS SUMMARY ===
    with tab3:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;">
            <h3 style='margin-top:0;'>⚠️ Unpaid Orders Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        unpaid_df = df[df['Payment Status Clean'] == 'Unpaid']
        
        if unpaid_df.empty:
            st.success("🎉 Great news! There are currently no unpaid orders.")
        else:
            total_unpaid = unpaid_df['Payment'].sum()
            unpaid_count = len(unpaid_df)
            col1, col2 = st.columns(2)
            with col1: st.metric("🚨 Total Unpaid Amount", f"Rs {total_unpaid:,.2f}")
            with col2: st.metric("📄 Unpaid Order Rows", f"{unpaid_count}")
            st.markdown("<br>#### Unpaid Records Detail", unsafe_allow_html=True)
            st.dataframe(unpaid_df.drop(columns=['Payment Status Clean'], errors='ignore'), use_container_width=True, hide_index=True)

    # === TAB 4: SYSTEM & EXPORT ===
    with tab4:
        st.markdown("""
        <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;">
            <h3 style='margin-top:0;'>🛠️ System Maintenance & Data Export</h3>
        </div>
        """, unsafe_allow_html=True)
        
        colE, colF = st.columns(2)
        
        with colE:
            st.markdown("#### 📤 Export Options")
            
            # 1. Export Filtered
            filtered_excel = convert_df_to_excel(export_filtered_df)
            st.download_button(
                label="📊 Export Filtered Data (Excel)",
                data=filtered_excel,
                file_name="alzamin_filtered_orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # 2. Export All
            all_excel = convert_df_to_excel(display_df)
            st.download_button(
                label="📑 Export All Data (Excel)",
                data=all_excel,
                file_name="alzamin_all_orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
                
        with colF:
            st.markdown("#### ⚙️ Maintenance Tools")
            
            # Refresh
            if st.button("🔄 Refresh Data", use_container_width=True):
                load_data.clear() 
                st.toast("✅ Data refreshed successfully!")
                st.rerun()
                
            # Clear Data
            if st.button("🗑️ Clear All Orders", use_container_width=True, type="primary"):
                clear_all_orders()
                st.toast("✅ Database cleared successfully!")
                st.rerun()