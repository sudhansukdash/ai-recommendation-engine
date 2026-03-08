# This is the homepage for the app which contains different products in categories and a recommended for you section which updates dynamically based on user interests
import streamlit as st
import os
import sys
import time

# Security Check
if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
    st.switch_page("main.py")

st.set_page_config(page_title="Home", layout="wide", initial_sidebar_state="collapsed")

# Defined None or empty variables so the app doesn't break if some fields are missing
if 'selected_product' not in st.session_state: st.session_state['selected_product'] = None
if 'view_category' not in st.session_state: st.session_state['view_category'] = None
if 'search_query' not in st.session_state: st.session_state['search_query'] = ""
if 'cart' not in st.session_state: st.session_state['cart'] = []
if 'orders' not in st.session_state: st.session_state['orders'] = []
if 'interactions' not in st.session_state: st.session_state['interactions'] = []
if 'blacklist' not in st.session_state: st.session_state['blacklist'] = set()
if 'home_rec_offset' not in st.session_state: st.session_state['home_rec_offset'] = 0 

# Import the navbar
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
from app.components import render_navbar

render_navbar()

from utils.recommender import get_user_recommendations

# Grab Data from the loaded files in the main
products_df = st.session_state['products_df']
interactions_df = st.session_state['interactions_df']
matrix = st.session_state['matrix']
model = st.session_state['model']

# Helper functions
def format_indian_currency(amount):
    s = str(int(amount))
    if len(s) <= 3: return s
    return f"{','.join([s[:-3][max(i-2, 0):i] for i in range(len(s[:-3]), 0, -2)][::-1])},{s[-3:]}"

def get_image_path(product_id):
    return os.path.join(PROJECT_ROOT, "data", "images", f"{product_id}.jpg")

def log_interaction(product_id, weight):
    st.session_state['interactions'].append({'pr_id': product_id, 'weight': weight, 'time': time.time()})
    # Reset the home feed recommendations to page 1 automatically
    st.session_state['home_rec_offset'] = 0

def go_home():
    st.session_state['selected_product'] = None
    st.session_state['view_category'] = None
    st.session_state['search_query'] = "" 
    st.session_state['home_rec_offset'] = 0 

def render_product_card(product, section_prefix="home", distance=None):
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

# Search bar logic
st.markdown("<br>", unsafe_allow_html=True)
c_empty1, c_search, c_empty2 = st.columns([1, 2, 1])
with c_search:
    st.text_input(
        "Search", 
        key="search_query", 
        placeholder="Search for electronics, clothing, accessories...", 
        label_visibility="collapsed" 
    )
st.markdown("<br>", unsafe_allow_html=True)

search_val = st.session_state['search_query'].strip()

if search_val:
    c1, c2 = st.columns([8, 1])
    with c1: st.subheader(f"Results for '{search_val}'")
    with c2: st.button("Clear", on_click=go_home)
    
    results = products_df[products_df['pr_name'].str.contains(search_val, case=False, na=False)]
    
    if results.empty:
        st.info("No products found.")
    else:
        cols = st.columns(5) 
        for i, (_, row) in enumerate(results.iterrows()):
            with cols[i % 5]: render_product_card(row, section_prefix="search")

else:
    
    c_title, c_prev, c_next = st.columns([8, 1, 1])
    with c_title: st.subheader("🌟 Recommended for You")
    
    # Get the recommendations
    rec_ids = get_user_recommendations(
        user_id=st.session_state['user_id'],
        matrix=matrix,
        interactions=interactions_df,
        model=model,
        session_history=st.session_state['interactions'],
        blacklist=st.session_state['blacklist']
    )
    # Next, Previous button logic for recommended for you section
    with c_prev:
        if st.button("◀", key="home_rec_prev"): 
            st.session_state['home_rec_offset'] = max(0, st.session_state['home_rec_offset'] - 5)
    with c_next:
        if st.button("▶", key="home_rec_next"): 
            if st.session_state['home_rec_offset'] + 5 < len(rec_ids): 
                st.session_state['home_rec_offset'] += 5
                
    off = st.session_state['home_rec_offset']
    current_batch = rec_ids[off : off + 5]
    
    cols = st.columns(5) 
    for i, item_data in enumerate(current_batch): 
        if isinstance(item_data, dict):
            pid = item_data['id']
            dist = item_data['distance']
        else:
            pid = item_data
            dist = None
            
        if pid in products_df.index:
            with cols[i]: 
                render_product_card(products_df.loc[pid], section_prefix="recs", distance=dist)
            
    st.divider()
    
    # Categories
    st.markdown("<h2 style='margin-top: 40px; margin-bottom: 20px;'>🚀 Explore Categories</h2>", unsafe_allow_html=True)
    categories = sorted(products_df['pr_category'].unique())
    
    for cat in categories:
        c1, c2 = st.columns([8, 1])
        with c1: 
            st.markdown(f"<h4 style='padding-top: 8px; margin-bottom: 10px;'>{cat.title().replace('_', ' ')}</h4>", unsafe_allow_html=True)
        with c2: 
            st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True)
            
            # If user clicked View All button redirect to view page
            if st.button("View All →", key=f"all_{cat}"):
                st.session_state['view_category'] = cat
                
                st.switch_page("pages/view.py")
                
        items = products_df[products_df['pr_category'] == cat].head(5) 
        cols = st.columns(5) 
        for i, (_, row) in enumerate(items.iterrows()):
            with cols[i]: render_product_card(row, section_prefix=f"cat_{cat}")
            
        st.markdown("<br>", unsafe_allow_html=True)