"""
AL Zamin Bakers & Fast Food - Order Automation System
Enhanced multi-item extraction logic
"""

import re
import json
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
    return [
        "Burger", "Chicken Burger", "Small Shawarma", "Big Shawarma",
        "Double Anda Burger", "Fries", "Coke", "Drink", "Disposable Glass"
    ]

def extract_order(text):
    """
    Parses a free-text order and returns structured data:
    {
        "customer": str,
        "items": [{"item": str, "quantity": int}, ...],
        "payment": None,
        "payment_status": str
    }
    """
    if not text:
        return {"customer": None, "items": [], "payment": None, "payment_status": None}

    lower_text = text.lower()
    tokens = text.split()

    # 1️⃣ Payment Status
    payment_status = "pending"
    for tok in tokens:
        cleaned_tok = re.sub(r'[^A-Za-z]', '', tok).lower()
        if cleaned_tok in PAYMENT_STATUSES:
            payment_status = cleaned_tok
            break

    # 2️⃣ Customer Name
    customer = "Walk-in"
    for tok in tokens:
        if CAPITALIZED_WORD_RE.match(tok) and tok.lower() not in PAYMENT_STATUSES:
            customer = tok.capitalize()
            break

    # 3️⃣ Multi-item Extraction
    menu_items = load_menu_items()
    items = []
    sorted_menu = sorted(menu_items, key=len, reverse=True)

    for menu_item in sorted_menu:
        item_lower = menu_item.lower()
        pattern = rf'(\d+)\s+{re.escape(item_lower)}s?\b'
        for match in re.finditer(pattern, lower_text):
            qty = int(match.group(1))
            items.append({"item": menu_item, "quantity": qty})

    # Handle items mentioned without quantity (default = 1)
    for menu_item in sorted_menu:
        item_lower = menu_item.lower()
        pattern = rf'\b{re.escape(item_lower)}s?\b'
        for match in re.finditer(pattern, lower_text):
            # Skip if already captured
            if any(i["item"].lower() == item_lower for i in items):
                continue
            items.append({"item": menu_item, "quantity": 1})

    return {
        "customer": customer,
        "items": items,
        "payment": None,
        "payment_status": payment_status,
    }

if __name__ == "__main__":
    sample = "Ali 2 burgers 3 shawarmas 1 coke 1 disposable glass paid"
    print(json.dumps(extract_order(sample), indent=2))
