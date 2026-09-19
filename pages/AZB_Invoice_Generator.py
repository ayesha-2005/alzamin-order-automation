"""
pages/5_🧾_Invoice_Generator.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Invoice Generator Module
Supports viewing and downloading invoices for any order by Order ID.
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
from fpdf import FPDF
from pathlib import Path

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import db

st.set_page_config(page_title="Invoice Generator | AL Zamin", page_icon="🧾", layout="centered")

st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 { color: #f47b20; font-family: 'Segoe UI', sans-serif; }
    .stApp { background-color: #fdfbf9; }
    .stDownloadButton>button {
        background-color: #f47b20; color: white; border-radius: 8px; border: none;
        padding: 10px 24px; font-weight: bold; transition: all 0.3s ease; width: 100%;
    }
    .stDownloadButton>button:hover { background-color: #d96314; box-shadow: 0 4px 12px rgba(244,123,32,0.2); }
    [data-testid="stTable"] { background-color: #ffffff; border-radius: 10px; overflow: hidden; border: 1px solid #f1e4d8; }
    hr { border-color: #f1e4d8; }
    </style>
""", unsafe_allow_html=True)

def load_all_orders():
    df = db.get_all_orders_df()
    if df is None or df.empty or "Order ID" not in df.columns: 
        return None
    try:
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        # Ensure timestamp is explicitly converted to datetime, handling string formats safely
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def search_in_menu(query, menu_item):
    query_parts = query.split()
    menu_parts = menu_item.lower().split()
    return any(part in menu_parts for part in query_parts)

def find_best_price(item_name, smart_menu):
    name = str(item_name).strip().lower()
    if name in smart_menu:
        return smart_menu[name]
        
    singular_name = name[:-1] if name.endswith('s') else name
    if singular_name in smart_menu:
        return smart_menu[singular_name]
        
    for menu_item, price in smart_menu.items():
        if search_in_menu(singular_name, menu_item):
            return price
            
    return 0.0

def create_pdf(order_df, inv_number, inv_date, customer_name, payment_status, total_amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_text_color(244, 123, 32)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 12, "AL Zamin Bakers & Fast Food", ln=True, align='C')
    pdf.set_text_color(119, 119, 119)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Serving Happiness Every Day!", ln=True, align='C')
    pdf.cell(0, 6, "Contact: info@alzamin.com | Tel: +92 300 1234567", ln=True, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 8, f"Customer: {customer_name}", ln=False)
    pdf.cell(90, 8, f"Invoice #: {inv_number}", ln=True, align='R')
    pdf.cell(100, 8, f"Status: {payment_status}", ln=False)
    pdf.cell(90, 8, f"Date: {inv_date}", ln=True, align='R')
    pdf.ln(10)
    pdf.set_fill_color(241, 228, 216)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(70, 10, "Item", border=1, fill=True)
    pdf.cell(30, 10, "Quantity", border=1, fill=True, align='C')
    pdf.cell(40, 10, "Unit Price", border=1, fill=True, align='C')
    pdf.cell(50, 10, "Line Total (PKR)", border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_font("Arial", '', 11)
    for _, row in order_df.iterrows():
        pdf.cell(70, 10, str(row['Item']), border=1)
        pdf.cell(30, 10, str(int(row['Quantity'])), border=1, align='C')
        pdf.cell(40, 10, f"{row['Unit Price']:.2f}", border=1, align='C')
        pdf.cell(50, 10, f"{row['Line Total (PKR)']:.2f}", border=1, align='C')
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(244, 123, 32)
    pdf.cell(140, 10, "Grand Total (PKR):", border=0, align='R')
    pdf.cell(50, 10, f"{total_amount:,.2f}", border=0, align='C')
    
    try:
        return pdf.output(dest='S').encode('latin-1')
    except TypeError:
        return bytes(pdf.output())

st.title("🧾 Invoice & Receipt Generator")
st.markdown("<p style='text-align: center; color: #888;'>Select any Order ID to view and download past receipts.</p>", unsafe_allow_html=True)
st.markdown("---")

all_orders_df = load_all_orders()

if all_orders_df is None or all_orders_df.empty:
    st.info("👋 No orders found in the system. Start adding orders in the Input module to generate invoices.")
else:
    # Get unique sorted Order IDs for the selector dropdown
    unique_order_ids = sorted(all_orders_df['Order ID'].dropna().unique(), reverse=True)
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        selected_order_id = st.selectbox("🔍 Search by Order ID", options=unique_order_ids, format_func=lambda x: f"Order #{x}")
    with col_sel2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"Total Orders: {len(unique_order_ids)}")

    if selected_order_id is not None:
        order_df = all_orders_df[all_orders_df['Order ID'] == selected_order_id].copy()
        
        if not order_df.empty:
            timestamp_val = order_df['Timestamp'].iloc[0]
            time_formatted = timestamp_val.strftime('%B %d, %Y - %I:%M %p') if pd.notna(timestamp_val) else "N/A"
            inv_number = f"INV-{selected_order_id}-{timestamp_val.strftime('%Y%m%d') if pd.notna(timestamp_val) else '0000'}"
            customer_name = order_df['Customer'].iloc[0]
            payment_status = order_df['Payment Status'].iloc[0].upper()
            
            # Fetch live menu prices from Database
            menu = db.get_menu_items()
            smart_menu = {str(k).strip().lower(): float(v) for k, v in menu.items()}
            
            order_df['Unit Price'] = order_df['Item'].apply(lambda x: find_best_price(x, smart_menu))
            order_df['Line Total (PKR)'] = order_df['Unit Price'] * order_df['Quantity']
            total_amount = order_df['Line Total (PKR)'].sum()
            display_df = order_df[['Item', 'Quantity', 'Unit Price', 'Line Total (PKR)']].copy()
            
            status_color = "green" if "PAID" in payment_status else "red"

            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:30px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-top: 20px; margin-bottom: 20px;">
                <h2 style='text-align:center; margin-top:0;'>🥐 AL Zamin Bakers & Fast Food 🍔</h2>
                <p style='text-align:center; color:#777; margin-bottom: 20px;'>
                    Serving Happiness Every Day!<br>Contact: alzaminbakers@gmail.com | Tel: +92 309 7405531
                </p>
                <hr style='border-top: 2px dashed #f1e4d8;'>
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div>
                        <p style="margin: 0;"><strong>👤 Customer:</strong> {customer_name}</p>
                        <p style="margin: 0;"><strong>💳 Status:</strong> <span style="color: {status_color}; font-weight: bold;">{payment_status}</span></p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0;"><strong>🧾 Invoice #:</strong> {inv_number}</p>
                        <p style="margin: 0;"><strong>📅 Date:</strong> {time_formatted}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🛒 Order Details")
            st.table(display_df.style.format({"Unit Price": "{:.2f}", "Line Total (PKR)": "{:.2f}"}))
            
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-top: 20px;">
                <h2 style='text-align:right; margin:0;'>Grand Total: <span style="color: #f47b20;">{total_amount:,.2f} PKR</span></h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_bytes = create_pdf(order_df, inv_number, time_formatted, customer_name, payment_status, total_amount)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(label="📥 Download PDF Invoice", data=pdf_bytes, file_name=f"Order_{selected_order_id}.pdf", mime="application/pdf")