"""
pages/1_📦_Order_Input.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System (Cloud-backed)
"""

import sys
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from extract import extract_order
import db 

st.set_page_config(page_title="Order Input | AL Zamin Bakers & Fast Food", page_icon="📦", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #FFF8ED 0%, #FFF1DC 100%); }
    .az-header {
        text-align: center; padding: 1.6rem 1rem 1.2rem 1rem;
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
        border-radius: 20px; box-shadow: 0 8px 20px rgba(255, 107, 53, 0.25); margin-bottom: 1.8rem;
    }
    .az-header h1 { color: #FFF8ED; font-size: 2rem; margin-bottom: 0.2rem; font-weight: 800; letter-spacing: 0.5px; }
    .az-header p { color: #FFEBD6; font-size: 1rem; margin: 0; }
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px !important; border: 1.5px solid #FFD3A5 !important;
        padding: 0.8rem !important; background-color: #FFFDF8 !important;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%); color: white; border: none;
        border-radius: 12px; padding: 0.55rem 1.4rem; font-weight: 700; box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3); width: 100%;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover { background: linear-gradient(135deg, #FF6B35 100%, #E85D2F 100%); color: white; }
    .az-footer { text-align: center; margin-top: 2.2rem; padding: 1rem; color: #A9754F; font-size: 0.88rem; border-top: 1px dashed #FFD3A5; }
    .az-footer b { color: #D2691E; }
    </style>
""", unsafe_allow_html=True)

if "last_saved_message" not in st.session_state:
    st.session_state["last_saved_message"] = None
if "show_receipt_modal" not in st.session_state:
    st.session_state["show_receipt_modal"] = False
if "latest_saved_order" not in st.session_state:
    st.session_state["latest_saved_order"] = None

st.markdown("""
    <div class="az-header">
        <h1>📦 Order Input</h1>
        <p>AL Zamin Bakers &amp; Fast Food — supports multi-item orders</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state["last_saved_message"]:
    st.success(st.session_state["last_saved_message"])

def find_best_price(item_name, smart_menu):
    name = str(item_name).strip().lower()
    if name in smart_menu:
        return smart_menu[name]
    if name.endswith('s') and name[:-1] in smart_menu:
        return smart_menu[name[:-1]]
        
    search_name = name[:-1] if name.endswith('s') else name
    for menu_item, price in smart_menu.items():
        if search_name in menu_item or menu_item in search_name:
            return price
    return 0.0

def calculate_order_total(items):
    menu = db.get_menu_items() 
    smart_menu = {str(k).strip().lower(): float(v) for k, v in menu.items()}
    total = 0.0
    for item in items:
        unit_price = find_best_price(item.get("item"), smart_menu)
        total += (unit_price * item.get("quantity", 0))
    return total

def safe_value(value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "Not provided"
    return value

# --- Input UI ---
st.markdown("### 📝 Enter Order Details")
with st.form(key="order_input_form", clear_on_submit=False):
    order_text = st.text_area(
        'Type the order exactly as received:',
        placeholder="e.g. Ali 2 burgers 3 shawarmas 1 coke paid",
        height=120, key="order_text_input"
    )
    submitted = st.form_submit_button("🔍 Extract Order")

if submitted:
    st.session_state["last_saved_message"] = None 
    st.session_state["show_receipt_modal"] = False
    if not order_text.strip():
        st.warning("⚠️ Please type an order before submitting.")
    else:
        try:
            extracted = extract_order(order_text)
            st.session_state["pending_order"] = extracted
        except Exception as exc:
            st.error(f"😕 Sorry, we couldn't process that order. ({exc})")

# --- Interactive Review & Edit Section ---
if st.session_state.get("pending_order"):
    order = st.session_state["pending_order"]

    st.markdown("---")
    st.markdown("### ✏️ Review & Edit Order Before Saving")

    customer = st.text_input("Customer", value=safe_value(order.get("customer")))
    
    raw_status = str(order.get("payment_status", "pending")).lower()
    if raw_status not in ["paid", "unpaid", "pending"]:
        raw_status = "pending"
    status_index = ["paid", "unpaid", "pending"].index(raw_status)
    payment_status = st.selectbox("Payment Status", ["paid", "unpaid", "pending"], index=status_index)

    st.markdown("### 🍔 Items")
    
    items_to_keep = []
    current_items_for_calc = []
    
    items_list = order.get("items", [])
    for idx, entry in enumerate(items_list):
        col1, col2, col3 = st.columns([2.5, 1, 0.6])
        with col1:
            item_name = st.text_input(f"Item {idx+1}", value=safe_value(entry.get("item")), key=f"item_name_{idx}")
        with col2:
            qty = st.number_input(f"Qty {idx+1}", value=int(entry.get("quantity") or 0), min_value=1, key=f"item_qty_{idx}")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            delete_clicked = st.button("🗑️", key=f"del_item_{idx}")
            
        if not delete_clicked:
            items_to_keep.append({"item": item_name, "quantity": qty})
            current_items_for_calc.append({"item": item_name, "quantity": qty})
        else:
            order["items"] = [it for i, it in enumerate(items_list) if i != idx]
            st.session_state["pending_order"] = order
            st.rerun()

    auto_total = calculate_order_total(current_items_for_calc)
    payment = st.number_input("Total Payment (PKR)", value=float(auto_total), step=10.0)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ Confirm & Save"):
        if not current_items_for_calc:
            st.warning("⚠️ Cannot save an order with no items!")
        else:
            final_order = {
                "customer": customer, "payment": payment,
                "payment_status": payment_status, "items": current_items_for_calc,
            }
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                # Save to Supabase Cloud DB
                order_id = db.get_next_order_id()
                db.save_order_to_db(order_id, customer, current_items_for_calc, payment, payment_status, timestamp)
                
                # Create DataFrame for receipt modal view
                saved_df = pd.DataFrame([{
                    "Order ID": order_id, "Customer": customer, "Item": entry["item"],
                    "Quantity": entry["quantity"], "Payment": payment,
                    "Payment Status": payment_status, "Timestamp": timestamp
                } for entry in current_items_for_calc])

                st.session_state["last_saved_message"] = f"💾 Order #{order_id} saved permanently to Supabase!"
                st.session_state["latest_saved_order"] = saved_df
                st.session_state["show_receipt_modal"] = True

                keys_to_clear = ["pending_order", "order_text_input"]
                for key in list(st.session_state.keys()):
                    if key in keys_to_clear or key.startswith("item_name_") or key.startswith("item_qty_"):
                        del st.session_state[key]
                st.rerun()
            except Exception as exc:
                st.error(f"⚠️ Saving to cloud failed: {exc}")

# --- RECEIPT MODAL OVERLAY ---
if st.session_state.get("show_receipt_modal") and st.session_state.get("latest_saved_order") is not None:
    saved_df = st.session_state["latest_saved_order"]
    inv_id = saved_df["Order ID"].iloc[0]
    cust = saved_df["Customer"].iloc[0]
    stat = saved_df["Payment Status"].iloc[0].upper()
    tot_pay = saved_df["Payment"].iloc[0]
    time_str = saved_df["Timestamp"].iloc[0]

    st.markdown("""
        <style>
        .receipt-modal {
            background: #ffffff; border: 2px solid #FF8C42; border-radius: 20px;
            padding: 30px; box-shadow: 0 12px 40px rgba(255, 107, 53, 0.25);
            margin-top: 20px; margin-bottom: 30px; position: relative;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="receipt-modal">', unsafe_allow_html=True)
    
    col_title, col_close = st.columns([5, 1])
    with col_title:
        st.markdown("<h2 style='color: #FF8C42; margin:0;'>🧾 Order Receipt</h2>", unsafe_allow_html=True)
    with col_close:
        if st.button("❌ Close", key="close_receipt_btn"):
            st.session_state["show_receipt_modal"] = False
            st.rerun()

    st.markdown("---")
    st.markdown(f"**Customer:** {cust} &nbsp;&nbsp;|&nbsp;&nbsp; **Order ID:** #{inv_id} &nbsp;&nbsp;|&nbsp;&nbsp; **Status:** {stat}")
    st.markdown(f"**Date:** {time_str}")
    st.markdown("<br>", unsafe_allow_html=True)

    menu = db.get_menu_items()
    smart_menu = {str(k).strip().lower(): float(v) for k, v in menu.items()}
    
    receipt_rows = []
    for _, row in saved_df.iterrows():
        item_n = row["Item"]
        q = row["Quantity"]
        u_price = find_best_price(item_n, smart_menu)
        l_total = u_price * int(q)
        receipt_rows.append({"Item": item_n, "Quantity": q, "Unit Price (PKR)": u_price, "Line Total (PKR)": l_total})

    receipt_display_df = pd.DataFrame(receipt_rows)
    st.dataframe(receipt_display_df, use_container_width=True, hide_index=True)

    st.markdown(f"<h3 style='text-align: right; color: #FF8C42;'>Grand Total: {tot_pay:,.2f} PKR</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """<div class="az-footer">🍔🥐 <b>AL Zamin Bakers &amp; Fast Food</b> — Order Automation System<br>Order Input Module</div>""",
    unsafe_allow_html=True,
)