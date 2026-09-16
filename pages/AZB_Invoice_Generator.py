import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Invoice Generator | AL Zamin",
    page_icon="🧾",
    layout="centered"
)

# --- CUSTOM CSS (Theme Match) ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6 {
        color: #f47b20;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background-color: #fdfbf9;
    }
    /* Style st.download_button to match the theme */
    .stDownloadButton>button {
        background-color: #f47b20;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stDownloadButton>button:hover {
        background-color: #d96314;
        color: white;
        box-shadow: 0 4px 12px rgba(244,123,32,0.2);
    }
    [data-testid="stTable"] {
        background-color: #ffffff;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #f1e4d8;
    }
    hr {
        border-color: #f1e4d8;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_latest_order():
    """Loads the orders data and extracts the most recent order by Timestamp."""
    file_path = "orders.xlsx"
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return None
        
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        df['Payment'] = pd.to_numeric(df['Payment'], errors='coerce').fillna(0)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.dropna(subset=['Timestamp'])
        
        if df.empty:
            return None
            
        latest_time = df['Timestamp'].max()
        latest_order_df = df[df['Timestamp'] == latest_time].copy()
        
        return latest_order_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_pdf(order_df, inv_number, inv_date, customer_name, payment_status, total_amount):
    """Generates a PDF invoice."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_text_color(244, 123, 32) # Orange #f47b20
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 12, "AL Zamin Bakers & Fast Food", ln=True, align='C')
    
    pdf.set_text_color(119, 119, 119) # Gray
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Serving Happiness Every Day!", ln=True, align='C')
    pdf.cell(0, 6, "Contact: 0309 7405531 | whatsapp: +92 309-7405531", ln=True, align='C')
    pdf.ln(10)
    
    # Customer and Invoice Info
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 8, f"Customer: {customer_name}", ln=False)
    pdf.cell(90, 8, f"Invoice #: {inv_number}", ln=True, align='R')
    pdf.cell(100, 8, f"Status: {payment_status}", ln=False)
    pdf.cell(90, 8, f"Date: {inv_date}", ln=True, align='R')
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(241, 228, 216) # Cream #f1e4d8
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Item", border=1, fill=True)
    pdf.cell(40, 10, "Quantity", border=1, fill=True, align='C')
    pdf.cell(60, 10, "Line Total (Rupees)", border=1, fill=True, align='C')
    pdf.ln()
    
    # Table Body
    pdf.set_font("Arial", '', 12)
    for _, row in order_df.iterrows():
        pdf.cell(90, 10, str(row['Item']), border=1)
        pdf.cell(40, 10, str(int(row['Quantity'])), border=1, align='C')
        pdf.cell(60, 10, f"Rs {row['Payment']:.2f}", border=1, align='C')
        pdf.ln()
        
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(244, 123, 32)
    pdf.cell(130, 10, "Grand Total:", border=0, align='R')
    pdf.cell(60, 10, f"Rs {total_amount:,.2f}", border=0, align='C')
    
    # Try FPDF 1.x and 2.x string output compatibility
    try:
        return pdf.output(dest='S').encode('latin-1')
    except TypeError:
        return bytes(pdf.output())

# --- HEADER ---
st.title("🧾 Invoice Generator")
st.markdown(f"<p style='text-align: center; color: #888;'>Last action performed at: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MAIN INVOICE LOGIC ---
order_df = load_latest_order()

if order_df is None or order_df.empty:
    st.info("👋 No orders found in the system. Start adding orders in the Input module to generate invoices.")
else:
    # --- EXTRACT INVOICE DATA ---
    latest_time = order_df['Timestamp'].iloc[0]
    inv_number = f"INV-{latest_time.strftime('%Y%m%d-%H%M')}"
    inv_date = latest_time.strftime('%B %d, %Y - %I:%M %p')
    customer_name = order_df['Customer'].iloc[0]
    payment_status = order_df['Payment Status'].iloc[0].upper()
    total_amount = order_df['Payment'].sum()
    
    display_df = order_df[['Item', 'Quantity', 'Payment']].copy()
    display_df.rename(columns={'Payment': 'Line Total (Rupees)'}, inplace=True)
    status_color = "green" if "PAID" in payment_status else "red"

    # --- RENDER INVOICE UI ---
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:30px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-bottom: 20px;">
        <h2 style='text-align:center; margin-top:0;'>🥐 AL Zamin Bakers & Fast Food 🍔</h2>
        <p style='text-align:center; color:#777; margin-bottom: 20px;'>
            Serving Happiness Every Day!<br>
            Contact: info@alzamin.com | Tel: +92 309-7405531
        </p>
        <hr style='border-top: 2px dashed #f1e4d8;'>
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div>
                <p style="margin: 0;"><strong>👤 Customer:</strong> {customer_name}</p>
                <p style="margin: 0;"><strong>💳 Status:</strong> <span style="color: {status_color}; font-weight: bold;">{payment_status}</span></p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0;"><strong>🧾 Invoice #:</strong> {inv_number}</p>
                <p style="margin: 0;"><strong>📅 Date:</strong> {inv_date}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🛒 Order Details")
    st.table(display_df)
    
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid #f1e4d8;border-radius:18px;padding:22px;box-shadow:0 8px 30px rgba(244,123,32,0.08); margin-top: 20px;">
        <h2 style='text-align:right; margin:0;'>Grand Total: <span style="color: #f47b20;">Rs {total_amount:,.2f}</span></h2>
        <p style='text-align:center; color:#888; margin-top:15px; margin-bottom:0; font-size: 14px;'>
            🍕 Thank you for dining with AL Zamin! We hope to see you again soon. 🍩
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- FUNCTIONAL EXPORT BUTTONS ---
    pdf_bytes = create_pdf(order_df, inv_number, inv_date, customer_name, payment_status, total_amount)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download PDF Invoice",
            data=pdf_bytes,
            file_name=f"{inv_number}.pdf",
            mime="application/pdf",
            use_container_width=True
        )