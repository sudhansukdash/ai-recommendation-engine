#This is where we define the navigation bar at the top which we use in our app 
import streamlit as st

# Renders a consistent top navigation bar, optionally hiding the welcome text. By default the welcome text is hidden, we can pass the argument show_welcome=False to hide the welcome txt
def render_navbar(show_welcome=True): 
    # Hide default Streamlit styling and inject custom CSS for the Red Logout Button
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none !important;}
            [data-testid="stSidebar"] {display: none !important;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Forces the 'primary' button to be a crisp danger-red */
            button[kind="primary"] {
                background-color: #dc3545 !important;
                border-color: #dc3545 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Fetch the logged-in user's name (fallback to 'Shopper' just in case)
    user_name = st.session_state.get('user_name', 'Shopper')
    
    # Container for the navbar to keep it structured
    with st.container():
        # 5 parts for the left side (Welcome text OR blank space), 1 part for each button
        c1, c2, c3, c4, c5 = st.columns([5, 1, 1, 1, 1])
        
        with c1:
            if show_welcome:
                # Using HTML for the header removes weird Streamlit padding
                st.markdown(f"<h2 style='margin-bottom: 0; padding-top: 5px;'>Welcome, {user_name}!</h2>", unsafe_allow_html=True)
            else:
                # An empty placeholder pushes the buttons to the right for a clean "slim" look
                st.empty()
                
        with c2:
            if st.button("Home", use_container_width=True):
                # Clear contextual states so the user actually goes to the main storefront
                st.session_state['view_category'] = None
                st.session_state['selected_product'] = None
                st.switch_page("pages/home.py")
                
        with c3:
            
            if st.button(f"Cart", use_container_width=True):
                st.switch_page("pages/cart.py")
                
        with c4:
            if st.button("Orders", use_container_width=True):
                st.switch_page("pages/orders.py")
                
        with c5:
            if st.button("Logout", type="primary", use_container_width=True):
                # 1. Reset Lists & Sets
                st.session_state['cart'] = []
                st.session_state['orders'] = []
                st.session_state['interactions'] = []
                st.session_state['blacklist'] = set()
                
                # 2. Reset Text & ID Pointers
                st.session_state['user_id'] = None
                st.session_state['user_name'] = None
                st.session_state['selected_product'] = None
                st.session_state['view_category'] = None
                st.session_state['search_query'] = ""
                
                # 3. Reset Integer Offsets back to 0
                st.session_state['home_rec_offset'] = 0
                st.session_state['related_offset'] = 0
                
                # 4. Kick them back to the login page
                st.switch_page("main.py")
                
    st.divider() # Line separating navbar from content