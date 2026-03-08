#This is the front door of entire application. It acts as the router, the database loader, and the login/signup page 
import streamlit as st
import pandas as pd
import pickle
import os
import time

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Recomify", layout="centered", initial_sidebar_state="collapsed")

# Remove the sidebar completely and use a navigation bar at the top defined in components
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {display: none !important;}
        [data-testid="stSidebar"] {display: none !important;}
    </style>
    """, 
    unsafe_allow_html=True
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define global server memory as we are not using any database the live interactions and all user details are stored temporarily in the RAM until the app is closed.
# This cache lives in the server's RAM and is shared across ALL users and tabs.
@st.cache_resource
def get_global_store():
    return {
        "temp_users": [],       # Stores new signups globally
        "carts": {},            # {user_id: [item1, item2]}
        "orders": {},           # {user_id: [order1, order2]}
        "interactions": {},     # {user_id: [interaction1, interaction2]}
        "blacklists": {}        # {user_id: set(blacklisted_items)}
    }

global_store = get_global_store()

@st.cache_resource # Used cache to load all resource at once at the start
def load_data():
    paths = {
        "interactions": os.path.join(BASE_DIR, "data", "processed", "interactions_final.csv"),
        "products": os.path.join(BASE_DIR, "data", "processed", "products_final.csv"),
        "users": os.path.join(BASE_DIR, "data", "processed", "users_clean.csv"),
        "matrix": os.path.join(BASE_DIR, "data", "models", "matrix.pkl"),
        "model": os.path.join(BASE_DIR, "data", "models", "model.pkl"),
    }
    
    interactions_df = pd.read_csv(paths["interactions"])
    products_df = pd.read_csv(paths["products"])
    products_df.set_index('pr_id', drop=False, inplace=True)
    
    users_df = pd.read_csv(paths["users"]) 
    with open(paths["matrix"], 'rb') as f: matrix = pickle.load(f)
    with open(paths["model"], 'rb') as f: model = pickle.load(f)

    return interactions_df, products_df, users_df, matrix, model

if 'data_loaded' not in st.session_state:
    try:
        interactions_df, products_df, users_df, matrix, model = load_data()
        st.session_state['interactions_df'] = interactions_df
        st.session_state['products_df'] = products_df
        st.session_state['users_df'] = users_df
        st.session_state['matrix'] = matrix
        st.session_state['model'] = model
        st.session_state['data_loaded'] = True
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

# Error handling, if some of the data of user not available, this prevents the system from breaking
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'user_name' not in st.session_state: st.session_state['user_name'] = None

if 'login_email' not in st.session_state: st.session_state['login_email'] = ""
if 'login_password' not in st.session_state: st.session_state['login_password'] = ""

if 'suggested_user' not in st.session_state: 
    st.session_state['suggested_user'] = st.session_state['users_df'].sample(1).iloc[0]

# Helper functions
def refresh_user():
    st.session_state['suggested_user'] = st.session_state['users_df'].sample(1).iloc[0]

def fill_login(email, password):
    st.session_state['login_email'] = email
    st.session_state['login_password'] = str(password)

def initialize_user_data(uid):
    """Pulls the user's data from the global store into their local session."""
    if uid not in global_store["carts"]:
        global_store["carts"][uid] = []
        global_store["orders"][uid] = []
        global_store["interactions"][uid] = []
        global_store["blacklists"][uid] = set()
        
    # Link local session variables to the global memory dictionaries
    st.session_state['cart'] = global_store["carts"][uid]
    st.session_state['orders'] = global_store["orders"][uid]
    st.session_state['interactions'] = global_store["interactions"][uid]
    st.session_state['blacklist'] = global_store["blacklists"][uid]

# The LOGIN PAGE
if st.session_state['user_id'] is None:
    st.title("Welcome to Recomify")
    st.write("Please log in to access your personalized store.")
    
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
    
    with tab_login:
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            users_df = st.session_state['users_df']
            match = users_df[users_df['email'] == email]
            
            is_valid = False
            
            # Check Global Temp Users First
            for tu in global_store['temp_users']:
                if tu['email'] == email and tu['password'] == pwd:
                    st.session_state['user_id'] = tu['user_id']
                    st.session_state['user_name'] = tu['first_name']
                    is_valid = True
                    break
            
            # Check CSV Users
            if not is_valid and not match.empty and str(match.iloc[0]['password']) == pwd:
                st.session_state['user_id'] = match.iloc[0]['user_id']
                st.session_state['user_name'] = match.iloc[0]['first_name']
                is_valid = True
                
            if is_valid:
                initialize_user_data(st.session_state['user_id'])
                st.rerun() 
            else:
                st.error("Invalid Email or Password")
        
        # Helper card that directly fetches username and password of users from users_clean.csv for test
        st.divider()
    
        with st.container(border=True):
            u = st.session_state['suggested_user']
            st.write(f"**Try this account:** {u['first_name']}")
            st.code(f"Email: {u['email']}\nPass:  {u['password']}", language="text")
            
            c1, c2 = st.columns(2)
            with c1:
                st.button("↻ Randomize", on_click=refresh_user, use_container_width=True)
            with c2:
                st.button("⚡ Auto-Fill", on_click=fill_login, args=(u['email'], u['password']), type="primary", use_container_width=True)
                
    with tab_signup:
        new_name = st.text_input("First Name", key="new_name")
        new_email = st.text_input("Email", key="new_email")
        new_pass = st.text_input("Password", type="password", key="new_pass")
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if new_name and new_email and new_pass:
                new_id = int(time.time()) 
                
                # Save the temp users in global cache so that new users state is preserved
                global_store['temp_users'].append({
                    "user_id": new_id, "first_name": new_name, 
                    "email": new_email, "password": new_pass
                })
                
                st.session_state['user_id'] = new_id
                st.session_state['user_name'] = new_name
                initialize_user_data(new_id)
                
                st.success("Account created! Redirecting...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("Please fill in all fields.")
else:
    st.switch_page("pages/home.py")