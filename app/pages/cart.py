# This script handles the cart of our app
import streamlit as st
import os
import sys
import time
from collections import Counter

# Security if user somehow landed directly using false credentials and is not present in session history or datasets, redirect to main
if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
    st.switch_page("main.py")

st.set_page_config(page_title="Cart", layout="wide", initial_sidebar_state="collapsed")


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
# Import the component navbar
from app.components import render_navbar

success_overlay = st.empty()

# We don't want a welcome message in the navbar of cart so we passed the argument as False
render_navbar(show_welcome=False)

def get_image_path(product_id):
    return os.path.join(PROJECT_ROOT, "data", "images", f"{product_id}.jpg")

def format_indian_currency(amount):
    s = str(int(amount))
    if len(s) <= 3: return s
    return f"{','.join([s[:-3][max(i-2, 0):i] for i in range(len(s[:-3]), 0, -2)][::-1])},{s[-3:]}"

# Page UI
st.title("My Cart")
products_df = st.session_state['products_df']

if not st.session_state['cart']:
    
    st.info("Cart is empty. Add a product to get started!")
else:
    total_price = 0
    
    # Use Counter to group duplicate items into {product_id: quantity}
    cart_counts = Counter(st.session_state['cart'])
    
    for pid, qty in cart_counts.items():
        if pid in products_df.index:
            p = products_df.loc[pid]
            
            # Calculate total for this specific grouped item
            item_total = p['pr_cost'] * qty
            total_price += item_total
            
            with st.container(border=True):
                # Expanded to 5 columns to neatly fit the Quantity multiplier
                c_img, c_name, c_qty, c_price, c_btn = st.columns([1, 3, 1, 2, 1])
                
                with c_img: 
                    st.image(get_image_path(pid), use_container_width=True)
                    
                with c_name: 
                    st.subheader(p['pr_name'])
                    st.caption(f"Category: {p['pr_category'].title().replace('_', ' ')}")
                    
                with c_qty:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 16px;'>Qty: <b>{qty}</b></p>", unsafe_allow_html=True)
                    
                with c_price: 
                    st.markdown("<br>", unsafe_allow_html=True)
                    if qty > 1:
                        st.markdown(f"<p style='margin-bottom: 0px; color: #666; font-size: 12px;'>₹ {format_indian_currency(p['pr_cost'])} each</p>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='margin-top: -5px;'>₹ {format_indian_currency(item_total)}</h4>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h4>₹ {format_indian_currency(item_total)}</h4>", unsafe_allow_html=True)
                    
                with c_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    # A stable key using just the Product ID. 
                    if st.button("Remove", key=f"del_{pid}"):
                        # Rebuild the cart list, ignoring this specific product entirely
                        st.session_state['cart'] = [item for item in st.session_state['cart'] if item != pid]
                        st.session_state['blacklist'].add(pid)
                        st.rerun()

    st.divider()
    
    # Checkout Footer
    c_empty, c_total, c_checkout = st.columns([4, 2, 2])
    with c_total:
        st.markdown(f"<h2>Total: ₹ {format_indian_currency(total_price)}</h2>", unsafe_allow_html=True)
        
    with c_checkout:
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        
        if st.button("Checkout All", type="primary", use_container_width=True):
            # Log behavior and update orders for every single item in the cart
            for item_id in st.session_state['cart']:
                if item_id in products_df.index:
                    prod = products_df.loc[item_id]
                    
                    st.session_state['orders'].append({
                        "id": item_id, 
                        "name": prod['pr_name'], 
                        "price": prod['pr_cost'],
                        "image": get_image_path(item_id) 
                    })
                    
                    st.session_state['interactions'].append({'pr_id': item_id, 'weight': 5, 'time': time.time()}) 
            
            # Wipe cart memory
            st.session_state['cart'] = []
            
            # Custom success dialog
            html_content = ""
            html_content += "<div class='success-container'>"
            html_content += "<div class='success-card'>"
            html_content += "<div class='check-icon-container'>"
            html_content += "<svg class='checkmark' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 52 52'>"
            html_content += "<circle class='checkmark__circle' cx='26' cy='26' r='25' fill='none'/>"
            html_content += "<path class='checkmark__check' fill='none' d='M14.1 27.2l7.1 7.2 16.7-16.8'/>"
            html_content += "</svg>"
            html_content += "</div>"
            html_content += "<h1 class='success-title'>Success!</h1>"
            html_content += "<p class='success-message'>Your order has been placed successfully.</p>"
            html_content += "<p class='redirect-message'>Redirecting you to the store...</p>"
            html_content += "</div>"
            html_content += "</div>"
            
            html_content += "<style>"
            html_content += ".success-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fadeInBackground 0.4s ease-out; }"
            html_content += ".success-card { background: rgba(255, 255, 255, 0.95); padding: 50px 70px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; border: 1px solid rgba(255,255,255,0.4); animation: slideInPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }"
            html_content += ".success-title { color: #2e8b57 !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700 !important; margin-top: 25px !important; margin-bottom: 5px !important; }"
            html_content += ".success-message { color: #333 !important; font-size: 20px !important; font-weight: 500; margin-top: 0px !important; margin-bottom: 25px !important; }"
            html_content += ".redirect-message { color: #888 !important; font-size: 14px !important; font-style: italic; }"
            html_content += ".check-icon-container { width: 100px; height: 100px; margin: 0 auto; }"
            html_content += ".checkmark__circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 2; stroke-miterlimit: 10; stroke: #2e8b57; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }"
            html_content += ".checkmark { width: 100px; height: 100px; border-radius: 50%; display: block; stroke-width: 3; stroke: #fff; stroke-miterlimit: 10; box-shadow: inset 0px 0px 0px #2e8b57; animation: fill 0.4s ease-in-out 0.4s forwards, scale .3s ease-in-out .9s backwards; }"
            html_content += ".checkmark__check { transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards; }"
            html_content += "@keyframes stroke { 100% { stroke-dashoffset: 0; } }"
            html_content += "@keyframes scale { 0%, 100% { transform: none; } 50% { transform: scale3d(1.1, 1.1, 1); } }"
            html_content += "@keyframes fill { 100% { box-shadow: inset 0px 0px 0px 50px #2e8b57; } }"
            html_content += "@keyframes fadeInBackground { from { opacity: 0; } to { opacity: 1; } }"
            html_content += "@keyframes slideInPop { from { opacity: 0; transform: translateY(50px) scale(0.9); } to { opacity: 1; transform: translateY(0) scale(1); } }"
            html_content += "</style>"
            
            success_overlay.markdown(html_content, unsafe_allow_html=True)
            
            # Given sleep to wait till the success animation is complete
            time.sleep(2.8)
            
            # Redirect to home if user buys an item
            st.switch_page("pages/home.py")