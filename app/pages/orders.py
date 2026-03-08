# This script handles the order history page of our app
import streamlit as st
import os
import sys

# Security check
if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
    st.switch_page("main.py")

st.set_page_config(page_title="Order History", layout="wide", initial_sidebar_state="collapsed")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from app.components import render_navbar

render_navbar(show_welcome=False)

def get_image_path(product_id):
    return os.path.join(PROJECT_ROOT, "data", "images", f"{product_id}.jpg")

def format_indian_currency(amount):
    s = str(int(amount))
    if len(s) <= 3: return s
    return f"{','.join([s[:-3][max(i-2, 0):i] for i in range(len(s[:-3]), 0, -2)][::-1])},{s[-3:]}"


st.markdown("<div style='margin-top: -20px;'></div>", unsafe_allow_html=True)
st.title("My Orders")

if not st.session_state['orders']: 
    st.info("No orders yet. Start shopping to see your history!")
else:
   
      for o in reversed(st.session_state['orders']):
        
        with st.container():
            # A 3-column layout: Image, Details, Status
            c_img, c_details, c_status = st.columns([1, 4, 2])
            
            with c_img:
                # Dynamically fetch the image using the saved product ID
                st.image(get_image_path(o['id']), use_container_width=True)
                
            with c_details:
                st.markdown(f"<h4 style='margin-bottom: 0px; margin-top: 10px;'>{o['name']}</h4>", unsafe_allow_html=True)
                
                # Added a fake Order ID using the product ID for realism
                order_id_snippet = str(o['id'])[:8].upper()
                st.caption(f"Order ID: #ORD-{order_id_snippet}-99X")
                
                st.markdown(f"**₹ {format_indian_currency(o['price'])}**")
                
            with c_status:
                st.markdown("<br>", unsafe_allow_html=True)
                # Replaced st.success with a sleek, custom HTML badge
                st.markdown("""
                    <div style='background-color: #d4edda; color: #155724; padding: 6px 12px; border-radius: 4px; display: inline-block; font-size: 14px; font-weight: 600;'>
                        ✔ Delivered
                    </div>
                """, unsafe_allow_html=True)
                
        # Use a simple line to separate orders instead of drawing boxes around them
        st.divider()