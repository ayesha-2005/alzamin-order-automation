"""
extract.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System

extract_order(text) parses a free-text order that may contain
MULTIPLE item-quantity pairs (e.g. "2 burgers 3 shawarmas 1 coke")
and returns one structured dict per order.

NOTE - schema change from earlier versions:
    Old shape: {"customer", "item", "quantity", "payment", "payment_status"}
    New shape: {"customer", "items": [{"item", "quantity"}, ...],
                "payment", "payment_status"}
This is a breaking change for any code that expects a single
"item"/"quantity" field (e.g. the Order Input page's Excel-saving
logic) - that page needs updating to loop over "items" and/or
flatten them when writing rows.

Supported example formats:
    "Ali 2 burgers 3 shawarmas 1 coke 1500 paid"
    "Sara 1 pizza 2 fries 3 drinks 1200 unpaid"

Field rules:
    customer        -> first capitalized word in the text
    items           -> repeating <number> <word(s)> pairs found
                       before the payment number; each becomes
                       {"item": ..., "quantity": ...}
    payment         -> the number immediately followed by 'rs',
                       otherwise the last number before the
                       payment-status word (or the last number
                       overall if no status word is found)
    payment_status  -> last word matching {paid, payed, pending,
                       unpaid, notpaid}

extract_order() always returns a single dict (never a list).
Any field that can't be found is None ("items" is [] when no
item-quantity pairs are found, since it's a list-typed field).
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
    Returns payment_idx (int) or None.
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
    Walk the numeric tokens that come BEFORE the payment number.
    Each one is a quantity; the words up to the next numeric token
    (or up to the payment number) form that item's name. Supports
    both single-word ("burgers") and multi-word ("Big shawarmas")
    item names.
    """
    item_number_indices = [
        i for i in numeric_indices 
        if i != payment_idx and (payment_idx is None or i < payment_idx)
    ]

    items = []
    for pos, idx in enumerate(item_number_indices):
        quantity = _to_number(tokens[idx])

        # the item's words run from just after this number to just
        # before the next item-number, or the payment number, or the
        # end of the tokens if neither exists
        if pos + 1 < len(item_number_indices):
            end = item_number_indices[pos + 1]
        elif payment_idx is not None:
            end = payment_idx
        elif status_idx is not None:
            end = status_idx
        else:
            end = len(tokens)

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
    Parse a free-text order (possibly with multiple item-quantity
    pairs) and return a dict with:
        customer, items (list of {item, quantity}), payment,
        payment_status.

    Always returns a single dict (never a list). Missing scalar
    fields are None; "items" is [] when no pairs were found.
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
        # Never crash the caller - return a safe, empty structure instead.
        return {
            "customer": None,
            "items": [],
            "payment": None,
            "payment_status": None,
        }


if __name__ == "__main__":
    import json

    samples = [
        "Ali 2 burgers 3 shawarmas 1 coke 1500 paid",
        "Sara 1 pizza 2 fries 3 drinks 1200 unpaid",
    ]
    for s in samples:
        print(s, "->", json.dumps(extract_order(s), indent=2))