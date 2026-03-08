# This script handles the product details page of our app
import streamlit as st
import os
import sys
import time


# Security checks
if 'user_id' not in st.session_state or st.session_state['user_id'] is None:
    st.switch_page("main.py")

if 'selected_product' not in st.session_state or not st.session_state['selected_product']:
    st.switch_page("pages/home.py")

# Grab data first to use in page config
pid = st.session_state['selected_product']
products_df = st.session_state['products_df']

if pid in products_df.index:
    p = products_df.loc[pid]
    st.set_page_config(page_title=f"{p['pr_name']}", layout="wide", initial_sidebar_state="collapsed")
else:
    st.set_page_config(page_title="Product Not Found", layout="wide", initial_sidebar_state="collapsed")

# Pagination State Initialization
if 'related_offset' not in st.session_state: 
    st.session_state['related_offset'] = 0

# 2. BACKEND SETUP
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
from app.components import render_navbar

# SUCCESS OVERLAY PLACEHOLDER
# This must be at the top level to render correctly
success_overlay = st.empty()

render_navbar(show_welcome=False)

from utils.recommender import get_similar_products
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

# Back button
st.markdown("<div style='margin-top: -30px;'></div>", unsafe_allow_html=True)
if st.button("← Back to Shopping"):
    st.session_state['selected_product'] = None
    st.session_state['related_offset'] = 0 
    st.switch_page("pages/home.py")

if pid in products_df.index:
    # Top section: Product name, cost, rating, descriptions, etc.
    c1, c2 = st.columns([1, 1.2])
    with c1: 
        st.image(get_image_path(pid), use_container_width=True)
    with c2:
        cat_display = p['pr_category'].title().replace('_', ' ')
        st.markdown(f"<p style='color: #444444; font-weight: bold; margin-bottom: -10px;'>{cat_display}</p>", unsafe_allow_html=True)
        
        st.title(p['pr_name'])
        
        rating = p.get('pr_rating', 4.5)
        st.markdown(f"""
            <div style='background-color: #f1f1f1; padding: 5px 12px; border-radius: 15px; display: inline-block; margin-bottom: 20px;'>
                <span style='color: #fbba00; font-size: 18px;'>★</span> 
                <span style='font-weight: bold; font-size: 16px;'>{rating}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<h2 style='margin-top: -10px;'>₹ {format_indian_currency(p['pr_cost'])}</h2>", unsafe_allow_html=True)
        
        description_text = p.get('pr_description', 'Experience premium quality and seamless design with this top-tier product.')
        st.markdown(f"<p style='color: #666; line-height: 1.6; margin-top: 10px;'>{description_text}</p>", unsafe_allow_html=True)
        
        st.write("")
        
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🛒 Add to Cart", use_container_width=True):
                st.session_state['cart'].append(pid)
                log_interaction(pid, 3) 
                st.toast("✅ Added to Cart!") 
        with b2:
            if st.button("⚡ Buy Now", type="primary", use_container_width=True):
                # Log the backend data
                st.session_state['orders'].append({"id": pid, "name": p['pr_name'], "price": p['pr_cost']})
                log_interaction(pid, 5) 
                
                # Custom success message after checkout
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
                html_content += "<p class='success-message'>Your purchase was completed.</p>"
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
                
                # Wait for the animation to complete
                time.sleep(2.8)
                
                # Redirect Home
                st.session_state['selected_product'] = None
                st.switch_page("pages/home.py")
    st.divider()
    
    # People Also Bought
    c_title, c_prev, c_next = st.columns([8, 1, 1])
    with c_title: st.subheader("🌟 People also bought")
    
    related_results = get_similar_products(pid, matrix, model, st.session_state['blacklist'])
    
    if related_results:
        with c_prev:
            if st.button("◀", key="rel_prev"): 
                st.session_state['related_offset'] = max(0, st.session_state['related_offset'] - 5)
        with c_next:
            if st.button("▶", key="rel_next"): 
                if st.session_state['related_offset'] + 5 < len(related_results): 
                    st.session_state['related_offset'] += 5
                    
        off = st.session_state['related_offset']
        current_batch = related_results[off : off + 5]
        
        cols = st.columns(5)
        for i, item in enumerate(current_batch):
            r_pid = item['id'] if isinstance(item, dict) else item
            r_dist = item['distance'] if isinstance(item, dict) else None
            
            if r_pid in products_df.index:
                rp = products_df.loc[r_pid]
                with cols[i]: 
                    with st.container(border=True):
                        if r_dist is not None:
                            st.markdown(f"<div style='text-align: right; color: #a9a9a9; font-size: 13px; letter-spacing: 0.5px;'>Dist: {r_dist}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

                        st.image(get_image_path(r_pid), use_container_width=True)
                        display_name = rp['pr_name'][:20] + "..." if len(rp['pr_name']) > 20 else rp['pr_name']
                        
                        unique_rel_key = f"rel_from_{pid}_to_{r_pid}"
                        if st.button("View Product", key=unique_rel_key, use_container_width=True):
                            st.session_state['selected_product'] = r_pid
                            st.session_state['related_offset'] = 0 
                            log_interaction(r_pid, 1)
                            st.rerun() 
                        
                        st.markdown(f"**₹ {format_indian_currency(rp['pr_cost'])}**")
    
    st.divider()
    
    # Reviews (placeholder + add review(test))
    st.subheader("💬 Customer Reviews")
    c_rev, c_form = st.columns([2, 1])
    
    with c_rev:
        st.markdown("""
            <div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2e8b57;'>
                <p style='margin-bottom: 0px;'><b>Ahmed Gorah</b> <span style='color: #2e8b57; font-size: 12px;'>✔ Verified Purchase</span></p>
                <p style='color: #fbba00; margin-top: 0px;'>★★★★★</p>
                <p style='color: #444;'>The quality is impressive. The recommendation brought me here and it's exactly what I was looking for. Highly recommended!!!</p>
            </div>
        """, unsafe_allow_html=True)
        st.info("Additional reviews will appear here as users provide feedback.")
        
    def handle_review_submit():
        if st.session_state.get("test_review_input", "").strip():
            st.toast("✅ Review submitted (Test Mode)")
        else:
            st.toast("⚠️ Review cannot be empty.")
        st.session_state["test_review_input"] = ""

    with c_form:
        st.write("**Write a review**")
        st.text_area("Share your thoughts", key="test_review_input", label_visibility="collapsed", placeholder="What did you like about this product?")
        st.button("Submit Review", use_container_width=True, on_click=handle_review_submit)

else:
    st.error("Product not found in the database.")