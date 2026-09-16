"""
app.py
------------------------------------------------------------
AL Zamin Bakers & Fast Food - Order Automation System
Multi-page dashboard | Home / Landing Page

This file is now ONLY the landing page for the multi-page app.
All functional logic lives in its own page under /pages:
    pages/1_📦_Order_Input.py   -> order entry, extraction, Excel saving
    pages/2_...                 -> Daily Sales Report / analytics, etc.

app.py intentionally contains no extraction logic, no forms, and no
Excel or analytics code - it just sets the theme and welcomes the
user, pointing them to the sidebar for navigation.
"""

import streamlit as st

# ----------------------------------------------------------------
# Page config
# ----------------------------------------------------------------
st.set_page_config(
    page_title="AL Zamin Bakers & Fast Food | Order Automation",
    page_icon="🍔",
    layout="centered",
)

# ----------------------------------------------------------------
# Custom CSS - orange / cream branded theme (shared across all pages)
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #FFF8ED 0%, #FFF1DC 100%);
    }

    /* Header */
    .az-header {
        text-align: center;
        padding: 2.2rem 1.5rem 1.8rem 1.5rem;
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(255, 107, 53, 0.25);
        margin-bottom: 1.8rem;
    }
    .az-header h1 {
        color: #FFF8ED;
        font-size: 2.3rem;
        margin-bottom: 0.3rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .az-header p {
        color: #FFEBD6;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Card containers */
    .az-card {
        background: #FFFDF8;
        border-radius: 18px;
        padding: 1.8rem 2rem;
        box-shadow: 0 6px 18px rgba(210, 130, 50, 0.15);
        border: 1px solid #FFE3C2;
        margin-bottom: 1.6rem;
        text-align: center;
    }
    .az-card h3 {
        color: #D2691E;
        margin-top: 0;
        margin-bottom: 0.8rem;
        font-weight: 700;
    }
    .az-card p {
        color: #5A4636;
        font-size: 1rem;
        line-height: 1.6rem;
        margin-bottom: 0;
    }

    /* Sidebar hint banner */
    .az-hint {
        text-align: center;
        background: #FFF3E1;
        border-left: 5px solid #FF8C42;
        border-radius: 12px;
        padding: 0.9rem 1.2rem;
        color: #8B4513;
        font-weight: 600;
        margin-bottom: 1.8rem;
    }

    /* Module list */
    .az-module {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.7rem 1rem;
        background: #FFF3E1;
        border-radius: 12px;
        margin-bottom: 0.6rem;
        border-left: 5px solid #FF8C42;
        color: #2E2620;
        font-weight: 600;
    }

    /* Footer */
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
# Header
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-header">
        <h1>🍔 AL Zamin Bakers &amp; Fast Food 🥐</h1>
        <p>Order Automation System — Home</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Sidebar navigation hint
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-hint">
        👈 Use the sidebar to access all modules.
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Welcome card
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-card">
        <h3>👋 Welcome</h3>
        <p>
            This is the home of the AL Zamin Bakers &amp; Fast Food Order
            Automation System — a simple, friendly way to turn free-text
            orders into structured records, track daily sales, and keep
            everything organized in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# What you'll find in the sidebar
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-card">
        <h3>🧭 What's in the sidebar</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="az-module">📦 Order Input — type an order and save it automatically</div>
    <div class="az-module">📊 Daily Sales Report — see today's totals, top items, and top customers</div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="az-footer">
        🍔🥐 <b>AL Zamin Bakers &amp; Fast Food</b> — Order Automation System<br>
        Crafted with care, served with speed.
    </div>
    """,
    unsafe_allow_html=True,
)