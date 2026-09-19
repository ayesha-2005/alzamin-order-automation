"""
extract.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System

Menu-aware extraction using Supabase Database.
"""

import re
import db

PAYMENT_STATUSES = {"paid", "payed", "pending", "unpaid", "notpaid"}
CAPITALIZED_WORD_RE = re.compile(r'^[A-Z][a-zA-Z]*$')

def load_menu_items():
    """Fetch live menu items from Supabase."""
    try:
        # Fetch dictionary from DB and return just the names (keys)
        menu_dict = db.get_menu_items()
        if menu_dict:
            return list(menu_dict.keys())
    except Exception:
        pass
        
    # Fallback if DB is completely unreachable
    return [
        "Burger", "Chicken Burger", "Small Shawarma", "Big Shawarma", 
        "Double Anda Burger", "Fries", "Coke", "Drink", "Disposable Glass"
    ]

def extract_order(text):
    if not text:
        return {"customer": None, "items": [], "payment": None, "payment_status": None}

    lower_text = text.lower()
    tokens = text.split()

    payment_status = "pending"
    for tok in tokens:
        cleaned_tok = re.sub(r'[^A-Za-z]', '', tok).lower()
        if cleaned_tok in PAYMENT_STATUSES:
            payment_status = cleaned_tok
            break

    customer = "Walk-in"
    for tok in tokens:
        if CAPITALIZED_WORD_RE.match(tok) and tok.lower() not in PAYMENT_STATUSES:
            customer = tok.capitalize()
            break

    menu_items = load_menu_items()
    items = []
    
    sorted_menu = sorted(menu_items, key=len, reverse=True)

    for menu_item in sorted_menu:
        item_lower = menu_item.lower()
        item_pattern = re.escape(item_lower) + r"s?\b"
        
        match = re.search(item_pattern, lower_text)
        if match:
            sub_text = lower_text[:match.start()]
            num_matches = re.findall(r'\b(\d+)\b', sub_text)
            
            qty = int(num_matches[-1]) if num_matches else 1
            items.append({"item": menu_item, "quantity": qty})

    return {
        "customer": customer,
        "items": items,
        "payment": None, 
        "payment_status": payment_status,
    }