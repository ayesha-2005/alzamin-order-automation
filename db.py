import streamlit as st
from supabase import create_client
import hashlib
import pandas as pd

# Initialize Supabase client first
@st.cache_resource
def init_db():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_db()

def hash_password(password):
    """Securely hash the password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# --- USER MANAGEMENT ---
def get_users():
    """Fetch all users from DB and return as a dictionary."""
    response = supabase.table("users").select("*").execute()
    users_dict = {}
    for row in response.data:
        clean_user = str(row["username"]).strip().lower()
        clean_hash = str(row["password_hash"]).strip()
        clean_role = str(row["role"]).strip().lower()
        
        users_dict[clean_user] = {
            "password": clean_hash,
            "role": clean_role
        }
    return users_dict

def add_user(username, password, role):
    """Hash password and insert/update user in DB."""
    pwd_hash = hash_password(password)
    supabase.table("users").upsert({
        "username": username,
        "password_hash": pwd_hash,
        "role": role
    }).execute()

def remove_user(username):
    """Delete a user from the DB."""
    supabase.table("users").delete().eq("username", username).execute()

# --- MENU MANAGEMENT ---
def get_menu_items():
    """Fetch menu prices from DB and return as a dictionary."""
    response = supabase.table("menu").select("*").execute()
    menu_dict = {}
    for row in response.data:
        menu_dict[row["item_name"]] = float(row["price"])
    return menu_dict

def sync_menu_items(menu_dict):
    """Smart sync: Removes deleted items and upserts existing/new ones."""
    current_res = supabase.table("menu").select("item_name").execute()
    current_items = set(row["item_name"] for row in current_res.data)
    new_items = set(menu_dict.keys())
    
    to_delete = current_items - new_items
    for item in to_delete:
        supabase.table("menu").delete().eq("item_name", item).execute()
        
    for item, price in menu_dict.items():
        supabase.table("menu").upsert({"item_name": item, "price": price}).execute()

# --- ORDER MANAGEMENT ---
def get_next_order_id():
    """Fetch the highest order ID from Supabase and increment by 1."""
    try:
        response = supabase.table("orders").select("order_id").order("order_id", desc=True).limit(1).execute()
        if response.data:
            return int(response.data[0]["order_id"]) + 1
    except Exception:
        pass
    return 1

def save_order_to_db(order_id, customer, items, payment, payment_status, timestamp):
    """Save all items of an order into Supabase."""
    rows = []
    for entry in items:
        rows.append({
            "order_id": order_id,
            "customer": str(customer),
            "item": str(entry.get("item")),
            "quantity": int(entry.get("quantity", 1)),
            "payment": float(payment),
            "payment_status": str(payment_status),
            "timestamp": str(timestamp)
        })
    supabase.table("orders").insert(rows).execute()

def get_all_orders_df():
    """Fetch all orders from Supabase and format as a DataFrame matching Excel columns."""
    try:
        response = supabase.table("orders").select("*").execute()
        if not response.data:
            return None
        df = pd.DataFrame(response.data)
        df = df.rename(columns={
            "order_id": "Order ID",
            "customer": "Customer",
            "item": "Item",
            "quantity": "Quantity",
            "payment": "Payment",
            "payment_status": "Payment Status",
            "timestamp": "Timestamp"
        })
        return df
    except Exception:
        return None