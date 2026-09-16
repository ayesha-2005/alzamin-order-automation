"""
pages/1_📦_Order_Input.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System
Multi-page dashboard | Page: Order Input

Updated for editable review + confirm & save workflow + full clear after save + persistent success message.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit as st
# Protect page
if not st.session_state.get("logged_in"):
    st.switch_page("app.py") # Kicks them back to login
# ----------------------------------------------------------------
# Make sure the project root (parent of /pages) is importable
# ----------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from extract import extract_order  # noqa: E402

# ----------------------------------------------------------------
# Page config
# ----------------------------------------------------------------
st.set_page_config(
    page_title="Order Input | AL Zamin Bakers & Fast Food",
    page_icon="📦",
    layout="centered",
)

EXCEL_FILE = ROOT_DIR / "orders.xlsx"
EXCEL_COLUMNS = ["Order ID", "Customer", "Item", "Quantity", "Payment", "Payment Status", "Timestamp"]

# ----------------------------------------------------------------
# Custom CSS (unchanged)
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

    .az-field {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.65rem 1rem;
        background: #FFF3E1;
        border-radius: 12px;
        margin-bottom: 0.6rem;
        border-left: 5px solid #FF8C42;
    }
    .az-field-label {
        font-weight: 700;
        color: #8B4513;
        font-size: 0.95rem;
    }
    .az-field-value {
        font-weight: 600;
        color: #2E2620;
        font-size: 0.98rem;
        text-align: right;
    }

    .az-item-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.55rem 1rem;
        background: #FFEFD9;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #FFB877;
    }
    .az-item-name {
        font-weight: 600;
        color: #6B4226;
    }
    .az-item-qty {
        font-weight: 700;
        color: #D2691E;
        background: #FFF8ED;
        border-radius: 8px;
        padding: 0.1rem 0.6rem;
    }

    div.stButton > button, div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.55rem 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
        width: 100%;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #FF6B35 0%, #E85D2F 100%);
        color: white;
    }

    .stTextInput input {
        border-radius: 12px !important;
        border: 1.5px solid #FFD3A5 !important;
        padding: 0.6rem !important;
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
# Initialize Session States
# ----------------------------------------------------------------
if "last_saved_message" not in st.session_state:
    st.session_state["last_saved_message"] = None

# ----------------------------------------------------------------
# Header & Persistent Success Message
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-header">
        <h1>📦 Order Input</h1>
        <p>AL Zamin Bakers &amp; Fast Food — supports multi-item orders</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display the message if it exists (survives the rerun)
if st.session_state["last_saved_message"]:
    st.success(st.session_state["last_saved_message"])

# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def safe_value(value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "Not provided"
    return value

def get_next_order_id():
    if not Path(EXCEL_FILE).exists():
        return 1
    try:
        existing_df = pd.read_excel(EXCEL_FILE)
        if "Order ID" in existing_df.columns and not existing_df.empty:
            max_id = pd.to_numeric(existing_df["Order ID"], errors="coerce").max()
            if pd.notna(max_id):
                return int(max_id) + 1
    except Exception:
        pass
    return 1

def save_to_excel(order_dict, timestamp):
    order_id = get_next_order_id()
    customer = safe_value(order_dict.get("customer"))
    payment = safe_value(order_dict.get("payment"))
    payment_status = safe_value(order_dict.get("payment_status"))

    items = order_dict.get("items") or []
    if not items:
        items = [{"item": None, "quantity": None}]

    new_rows = []
    for entry in items:
        new_rows.append(
            {
                "Order ID": order_id,
                "Customer": customer,
                "Item": safe_value(entry.get("item")),
                "Quantity": safe_value(entry.get("quantity")),
                "Payment": payment,
                "Payment Status": payment_status,
                "Timestamp": timestamp,
            }
        )

    new_rows_df = pd.DataFrame(new_rows, columns=EXCEL_COLUMNS)

    if Path(EXCEL_FILE).exists():
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
        except Exception:
            existing_df = pd.DataFrame(columns=EXCEL_COLUMNS)
        updated_df = pd.concat([existing_df, new_rows_df], ignore_index=True)
    else:
        updated_df = new_rows_df

    updated_df.to_excel(EXCEL_FILE, index=False)
    return order_id

# ----------------------------------------------------------------
# Input card
# ----------------------------------------------------------------
st.markdown('<div class="az-card">', unsafe_allow_html=True)
st.markdown("### 📝 Enter Order Details")

with st.form(key="order_input_form", clear_on_submit=False):
    order_text = st.text_input(
        'Type the order exactly as received (e.g. "Ali 2 burgers 3 shawarmas 1 coke paid")',
        placeholder="e.g. Sara 1 pizza 2 fries 3 drinks unpaid",
        key="order_text_input"
    )
    submitted = st.form_submit_button("🔍 Extract Order")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Extraction (no auto-save)
# ----------------------------------------------------------------
if submitted:
    # Clear the previous success message when a new extraction is started
    st.session_state["last_saved_message"] = None 
    
    if not order_text.strip():
        st.warning("⚠️ Please type an order before submitting.")
    else:
        try:
            extracted = extract_order(order_text)
            st.session_state["pending_order"] = extracted
        except Exception as exc:
            st.error(f"😕 Sorry, we couldn't process that order. ({exc})")

# ----------------------------------------------------------------
# Editable Review Section
# ----------------------------------------------------------------
if st.session_state.get("pending_order"):
    order = st.session_state["pending_order"]

    st.markdown('<div class="az-card">', unsafe_allow_html=True)
    st.markdown("### ✏️ Review & Edit Order Before Saving")

    # Editable top fields
    customer = st.text_input("Customer", value=safe_value(order.get("customer")))
    payment = st.number_input("Payment", value=int(order.get("payment") or 0))
    
    # Safely handle payment status index
    raw_status = str(order.get("payment_status", "paid")).lower()
    if raw_status not in ["paid", "unpaid", "pending"]:
        raw_status = "pending"
    status_index = ["paid", "unpaid", "pending"].index(raw_status)
    
    payment_status = st.selectbox(
        "Payment Status",
        ["paid", "unpaid", "pending"],
        index=status_index
    )

    # Editable items
    st.markdown("### 🍔 Items")
    edited_items = []
    for idx, entry in enumerate(order.get("items", [])):
        col1, col2 = st.columns([3, 1])
        with col1:
            item_name = st.text_input(
                f"Item {idx+1}",
                value=safe_value(entry.get("item")),
                key=f"item_name_{idx}"
            )
        with col2:
            qty = st.number_input(
                f"Qty {idx+1}",
                value=int(entry.get("quantity") or 0),
                key=f"item_qty_{idx}"
            )
        edited_items.append({"item": item_name, "quantity": qty})

    # Confirm & Save + FULL CLEAR
    if st.button("✅ Confirm & Save"):
        final_order = {
            "customer": customer,
            "payment": payment,
            "payment_status": payment_status,
            "items": edited_items,
        }

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            order_id = save_to_excel(final_order, timestamp)
            
            # 1. SET THE MESSAGE IN STATE SO IT SURVIVES
            st.session_state["last_saved_message"] = f"💾 Order #{order_id} saved successfully!"

            # 2. FULL CLEAR: Delete session state keys to wipe out the form UI
            keys_to_clear = ["pending_order", "order_text_input"]
            for key in list(st.session_state.keys()):
                if key in keys_to_clear or key.startswith("item_name_") or key.startswith("item_qty_"):
                    del st.session_state[key]
            
            # 3. TRIGGER REFRESH
            st.rerun()

        except Exception as exc:
            st.error(f"⚠️ Saving failed: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-footer">
        🍔🥐 <b>AL Zamin Bakers &amp; Fast Food</b> — Order Automation System<br>
        Order Input Module
    </div>
    """,
    unsafe_allow_html=True,
)