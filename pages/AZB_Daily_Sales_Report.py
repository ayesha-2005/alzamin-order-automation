import os
from datetime import datetime
from pathlib import Path
 
import pandas as pd
import streamlit as st
 
# ----------------------------------------------------------------
# Page config
# ----------------------------------------------------------------
st.set_page_config(
    page_title="Daily Sales Report | AL Zamin Bakers & Fast Food",
    page_icon="📊",
    layout="centered",
)
 
ROOT_DIR = Path(__file__).resolve().parent.parent
EXCEL_FILE = ROOT_DIR / "orders.xlsx"
 
# ----------------------------------------------------------------
# Custom CSS - same orange / cream branded theme as the rest of the app
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #FFF8ED 0%, #FFF1DC 100%);
    }
    .az-header {
        text-align: center;
        padding: 1.6rem 1rem 1.2rem 1rem;
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(255, 107, 53, 0.25);
        margin-bottom: 1.8rem;
    }
    .az-header h1 {
        color: #FFF8ED;
        font-size: 2rem;
        margin-bottom: 0.2rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .az-header p {
        color: #FFEBD6;
        font-size: 1rem;
        margin: 0;
    }
    .az-card {
        background: #FFFDF8;
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 6px 18px rgba(210, 130, 50, 0.15);
        border: 1px solid #FFE3C2;
        margin-bottom: 1.6rem;
    }
    .az-card h3 {
        color: #D2691E;
        margin-top: 0;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .az-footer {
        text-align: center;
        margin-top: 2.2rem;
        padding: 1rem;
        color: #A9754F;
        font-size: 0.88rem;
        border-top: 1px dashed #FFD3A5;
    }
    .az-footer b {
        color: #D2691E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ----------------------------------------------------------------
# Header
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-header">
        <h1>📊 Daily Sales Report</h1>
        <p>AL Zamin Bakers &amp; Fast Food — today at a glance</p>
    </div>
    """,
    unsafe_allow_html=True,
)
 
# ----------------------------------------------------------------
# Report card
# ----------------------------------------------------------------
st.markdown('<div class="az-card">', unsafe_allow_html=True)
st.markdown("### 📊 Today's Summary")
 
if not os.path.exists(EXCEL_FILE):
    st.info("No orders found yet. Daily report will appear once orders are saved.")
else:
    report_df = None
    try:
        report_df = pd.read_excel(EXCEL_FILE)
    except Exception as exc:
        st.error(f"⚠️ Could not read {EXCEL_FILE.name}: {exc}")
 
    if report_df is None or report_df.empty:
        st.info("No orders found yet. Daily report will appear once orders are saved.")
    elif "Order ID" not in report_df.columns:
        st.error(
            "⚠️ 'Order ID' column not found in orders.xlsx. "
            "This report needs orders saved by the updated Order Input page."
        )
    else:
        # Keep only today's rows
        report_df["Timestamp"] = pd.to_datetime(report_df["Timestamp"], errors="coerce")
        today = datetime.now().date()
        today_df = report_df[report_df["Timestamp"].dt.date == today].copy()
 
        if today_df.empty:
            st.info("No orders recorded today yet. Check back after some orders come in.")
        else:
            # Normalize payment status so "payed"/"notpaid" fold into paid/unpaid
            def _normalize_status(status):
                status = str(status).strip().lower()
                if status in ("paid", "payed"):
                    return "paid"
                if status in ("unpaid", "notpaid"):
                    return "unpaid"
                if status == "pending":
                    return "pending"
                return status
 
            today_df["_status_norm"] = today_df["Payment Status"].apply(_normalize_status)
 
            # One order = one Order ID, no matter how many item rows it has.
            # De-duplicate BEFORE counting orders or summing revenue so a
            # 3-item order isn't counted (or paid) three times over.
            orders_unique = today_df.drop_duplicates(subset=["Order ID"]).copy()
 
            paid_mask = orders_unique["_status_norm"] == "paid"
            unpaid_mask = orders_unique["_status_norm"] == "unpaid"
            pending_mask = orders_unique["_status_norm"] == "pending"
 
            total_orders = len(orders_unique)
            total_revenue = pd.to_numeric(orders_unique.loc[paid_mask, "Payment"], errors="coerce").sum()
            paid_count = int(paid_mask.sum())
            unpaid_count = int(unpaid_mask.sum())
            pending_count = int(pending_mask.sum())
 
            # --- Key metrics ---
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("🧾 Total Orders", total_orders)
            m2.metric("💰 Revenue (Paid)", f"Rs {total_revenue:,.0f}")
            m3.metric("✅ Paid", paid_count)
            m4.metric("⏳ Pending", pending_count)
            m5.metric("❌ Unpaid", unpaid_count)
 
            st.markdown("<br>", unsafe_allow_html=True)
 
            # --- Top 5 items sold today (uses every item row - this is
            #     exactly the level items live at, no de-duplication needed) ---
            col_left, col_right = st.columns(2)
 
            items_df = today_df.copy()
            items_df["Quantity"] = pd.to_numeric(items_df["Quantity"], errors="coerce").fillna(0)
            top_items = (
                items_df.groupby("Item")["Quantity"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .reset_index()
            )
            top_items.columns = ["Item", "Quantity Sold"]
 
            # --- Top 5 customers by number of ORDERS (not item rows) ---
            top_customers = (
                orders_unique.groupby("Customer")["Order ID"]
                .nunique()
                .sort_values(ascending=False)
                .head(5)
                .reset_index(name="Total Orders")
            )
 
            with col_left:
                st.markdown("#### 🍽️ Top 5 Items Sold")
                st.dataframe(top_items, use_container_width=True, hide_index=True)
 
            with col_right:
                st.markdown("#### 👥 Top 5 Customers")
                st.dataframe(top_customers, use_container_width=True, hide_index=True)
 
            # --- Bar chart of item quantities ---
            if not top_items.empty:
                st.markdown("#### 📈 Item Quantity Chart")
                chart_data = top_items.set_index("Item")["Quantity Sold"]
                st.bar_chart(chart_data)
 
            # --- Report generation timestamp ---
            st.caption(f"🕒 Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 
st.markdown("</div>", unsafe_allow_html=True)
 
# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-footer">
        🍔🥐 <b>AL Zamin Bakers &amp; Fast Food</b> — Order Automation System<br>
        Daily Sales Report Module
    </div>
    """,
    unsafe_allow_html=True,
)
 
