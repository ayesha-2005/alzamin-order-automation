"""
extract.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System

extract_order(text, menu_items) parses a free-text order by scanning
against known menu items, capturing quantities, customer names,
and payment status.
"""

import re
import json
import os
from pathlib import Path

PAYMENT_STATUSES = {"paid", "payed", "pending", "unpaid", "notpaid"}
CAPITALIZED_WORD_RE = re.compile(r'^[A-Z][a-zA-Z]*$')

def load_menu_items():
    """Load items from prices.json or fallback to defaults."""
    prices_path = Path(__file__).resolve().parent / "prices.json"
    if prices_path.exists():
        try:
            with open(prices_path, "r") as f:
                data = json.load(f)
                if data:
                    return list(data.keys())
        except Exception:
            pass
    # Fallback standard menu items
    return [
        "Burger", "Chicken Burger", "Small Shawarma", "Big Shawarma", 
        "Double Anda Burger", "Fries", "Coke", "Drink", "Disposable Glass"
    ]

def extract_order(text):
    """
    Parses a free-text order against known menu items and returns a structured dictionary:
    {
        "customer": str,
        "items": [{"item": str, "quantity": int}, ...],
        "payment": float,
        "payment_status": str
    }
    """
    if not text:
        return {"customer": None, "items": [], "payment": None, "payment_status": None}

    lower_text = text.lower()
    tokens = text.split()

    # 1. Extract Payment Status
    payment_status = "pending"
    for tok in tokens:
        cleaned_tok = re.sub(r'[^A-Za-z]', '', tok).lower()
        if cleaned_tok in PAYMENT_STATUSES:
            payment_status = cleaned_tok
            break

    # 2. Extract Customer Name (First capitalized word not matching a status)
    customer = "Walk-in"
    for tok in tokens:
        if CAPITALIZED_WORD_RE.match(tok) and tok.lower() not in PAYMENT_STATUSES:
            customer = tok.capitalize()
            break

    # 3. Smart Menu-Driven Item & Quantity Matching
    menu_items = load_menu_items()
    items = []
    
    # Sort menu items by length descending so multi-word items ("Double Anda Burger") match before "Burger"
    sorted_menu = sorted(menu_items, key=len, reverse=True)

    # Search text for menu keywords and look for preceding numbers
    for menu_item in sorted_menu:
        item_lower = menu_item.lower()
        # Create a regex that handles optional plural 's' (e.g., burger/burgers, shawarma/shawarmas)
        item_pattern = re.escape(item_lower) + r"s?\b"
        
        match = re.search(item_pattern, lower_text)
        if match:
            # Look backwards from the item match position to find the closest preceding quantity number
            sub_text = lower_text[:match.start()]
            num_matches = re.findall(r'\b(\d+)\b', sub_text)
            
            qty = int(num_matches[-1]) if num_matches else 1
            items.append({"item": menu_item, "quantity": qty})

    return {
        "customer": customer,
        "items": items,
        "payment": None, # Will be auto-calculated via prices.json in Order Input
        "payment_status": payment_status,
    }


if __name__ == "__main__":
    sample = "Ali 2 burgers 3 shawarmas 1 coke 1 disposable glass paid"
    print(json.dumps(extract_order(sample), indent=2))