"""
extract.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System

extract_order(text) parses a free-text order that may contain
MULTIPLE item-quantity pairs (e.g. "2 burgers 3 shawarmas 1 coke")
and returns one structured dict per order.
"""

import re

PAYMENT_STATUSES = {"paid", "payed", "pending", "unpaid", "notpaid"}

# A number immediately (optionally with a space) followed by 'rs'
RS_NEAR_NUMBER_RE = re.compile(r'\b(\d+)\s*rs\b', re.IGNORECASE)

# A "clean" capitalized word: starts uppercase, rest are letters only
CAPITALIZED_WORD_RE = re.compile(r'^[A-Z][a-zA-Z]*$')


def _to_number(value):
    """Convert a numeric string to int when possible, else return as-is."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _find_payment_status(tokens):
    """Return (index, normalized_status) for the LAST token matching a
    known payment status, or (None, None) if none match."""
    status_idx, status = None, None
    for i, tok in enumerate(tokens):
        cleaned = re.sub(r'[^A-Za-z]', '', tok).lower()
        if cleaned in PAYMENT_STATUSES:
            status_idx, status = i, cleaned
    return status_idx, status


def _find_numeric_indices(tokens):
    """Return a list of token indices that are pure numbers."""
    return [i for i, tok in enumerate(tokens) if re.fullmatch(r'\d+', tok)]


def _find_payment(text, tokens, numeric_indices, status_idx):
    """
    Decide which numeric token index is the 'payment':
    - the number immediately followed by 'rs', if present
    - otherwise the last number before the payment-status word
      (or the last number overall, if there's no status word)
    """
    if not numeric_indices:
        return None

    rs_match = RS_NEAR_NUMBER_RE.search(text)
    if rs_match:
        target_value = rs_match.group(1)
        for i in reversed(numeric_indices):
            if tokens[i] == target_value:
                return i

    if status_idx is not None:
        before_status = [i for i in numeric_indices if i < status_idx]
        if before_status:
            return before_status[-1]

    return numeric_indices[-1]


def _extract_items(tokens, numeric_indices, payment_idx, status_idx):
    """
    Walk the numeric tokens that come BEFORE the payment number or status.
    Each one is a quantity; words up to the next number form the item's name.
    """
    # Determine the cutoff boundary: items should only be parsed before the payment index or status index
    cutoff_idx = len(tokens)
    if payment_idx is not None and status_idx is not None:
        cutoff_idx = min(payment_idx, status_idx)
    elif payment_idx is not None:
        cutoff_idx = payment_idx
    elif status_idx is not None:
        cutoff_idx = status_idx

    item_number_indices = [i for i in numeric_indices if i < cutoff_idx]

    items = []
    for pos, idx in enumerate(item_number_indices):
        quantity = _to_number(tokens[idx])

        # Find the boundary for the current item name tokens
        if pos + 1 < len(item_number_indices):
            end = item_number_indices[pos + 1]
        else:
            end = cutoff_idx

        name_tokens = tokens[idx + 1:end]
        item_name = " ".join(name_tokens).strip()

        if item_name:
            items.append({"item": item_name, "quantity": quantity})

    return items


def _extract_customer(tokens):
    """First capitalized word found anywhere in the text."""
    for tok in tokens:
        if CAPITALIZED_WORD_RE.match(tok) and tok.lower() not in PAYMENT_STATUSES:
            return tok
    return None


def extract_order(text):
    """
    Parse a free-text order and return a dict with:
        customer, items (list of {item, quantity}), payment, payment_status.
    """
    if not text:
        text = ""

    try:
        tokens = text.split()

        status_idx, payment_status = _find_payment_status(tokens)
        numeric_indices = _find_numeric_indices(tokens)
        payment_idx = _find_payment(text, tokens, numeric_indices, status_idx)
        payment = tokens[payment_idx] if payment_idx is not None else None

        items = _extract_items(tokens, numeric_indices, payment_idx, status_idx)
        customer = _extract_customer(tokens)

        return {
            "customer": customer,
            "items": items,
            "payment": _to_number(payment),
            "payment_status": payment_status,
        }
    except Exception:
        return {
            "customer": None,
            "items": [],
            "payment": None,
            "payment_status": None,
        }


if __name__ == "__main__":
    import json

    samples = [
        "Ali 2 burgers 3 shawarmas 1 coke regular paid",
        "Sara 1 pizza 2 fries 3 drinks 1200 unpaid",
    ]
    for s in samples:
        print(s, "->", json.dumps(extract_order(s), indent=2))