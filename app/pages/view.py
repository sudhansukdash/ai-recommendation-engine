# This script handles the view all in the categories section of the homepage
import streamlit as st
import os
import sys
import time

# Security Check
if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
    st.switch_page("main.py")

# If someone somehow lands here without picking a category, send them home
if 'view_category' not in st.session_state or not st.session_state['view_category']:
    st.switch_page("pages/home.py")

st.set_page_config(page_title="Explore Categories", layout="wide", initial_sidebar_state="collapsed")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
from app.components import render_navbar
render_navbar(show_welcome=False)
# Grab Data
products_df = st.session_state['products_df']
cat = st.session_state['view_category']

# Helper functions
def format_indian_currency(amount):
    s = str(int(amount))
    if len(s) <= 3: return s
    return f"{','.join([s[:-3][max(i-2, 0):i] for i in range(len(s[:-3]), 0, -2)][::-1])},{s[-3:]}"

def get_image_path(product_id):
    return os.path.join(PROJECT_ROOT, "data", "images", f"{product_id}.jpg")

def log_interaction(product_id, weight):
    st.session_state['interactions'].append({'pr_id': product_id, 'weight': weight, 'time': time.time()})

def render_product_card(product, section_prefix="cat", distance=None):
    with st.container(border=True):
        if distance is not None:
            st.markdown(f"<div style='text-align: right; color: #a9a9a9; font-size: 13px; font-weight: normal; letter-spacing: 0.5px; margin-bottom: 5px;'>Dist: {distance}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: right; font-size: 11px; margin-bottom: 5px; color: transparent;'>-</div>", unsafe_allow_html=True)
            
        st.image(get_image_path(product['pr_id']), use_container_width=True)
        
        name = product['pr_name']
        display_name = name[:22] + "..." if len(name) > 22 else name
        
        st.markdown(f"<p style='font-size: 14px; margin-bottom: 0px; margin-top: 10px;'><b>{display_name}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #2e8b57; font-size: 16px; margin-top: 0px;'><b>₹ {format_indian_currency(product['pr_cost'])}</b></p>", unsafe_allow_html=True)
        
        unique_key = f"btn_{section_prefix}_{product['pr_id']}"
        
        if st.button("View Product", key=unique_key, use_container_width=True):
            st.session_state['selected_product'] = product['pr_id']
            log_interaction(product['pr_id'], 1) 
            st.switch_page("pages/product_details.py")

# Page layout
st.markdown("<br>", unsafe_allow_html=True)

if st.button("← Back to Home"):
    st.session_state['view_category'] = None
    st.switch_page("pages/home.py")

st.title(f"{cat.title().replace('_', ' ')}")
st.divider()

# Render all items for this category in a 5-column grid
items = products_df[products_df['pr_category'] == cat]

# Streamlit columns wrap naturally if you use a standard loop with indexing
cols = st.columns(5) 
for i, (_, row) in enumerate(items.iterrows()):
    with cols[i % 5]: 
        render_product_card(row, section_prefix=f"fullcat_{cat}")