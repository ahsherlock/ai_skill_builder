import streamlit as st
from datetime import datetime
from src.ui.login import render_login_view
from src.ui.home import render_home_view
from src.ui.results import render_results_view
from src.ui.saved_modules import render_saved_modules_view

# Set page config with katana icon (replace 🗡️ with PNG path if you make one)
st.set_page_config(page_title="AI Teaching Faculty Hub", page_icon="🗡️", layout="wide")

# Add custom CSS here
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .main {background-color: #1e1e1e; color: #ffffff;}
    h1, h2, h3 {font-family: 'Orbitron', sans-serif;}
    .stButton>button {background-color: #00ebeb; color: #1e1e1e; font-weight: bold;}
    .stButton>button:hover {box-shadow: 0 0 10px #00ebeb, 0 0 20px #00ebeb; transition: all 0.3s ease;}
    .stTabs [role='tab'] {font-size: 1.2em;}
    .stTabs [role='tab']:hover {text-shadow: 0 0 5px #00ebeb;}
    hr {border: 1px solid #00ebeb;}
    @keyframes fadeIn {from {opacity: 0;} to {opacity: 1;}}
    </style>
""", unsafe_allow_html=True)

st.title("AI Teaching Faculty Hub")

# Session state initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "view" not in st.session_state:
    st.session_state.view = "Login"
if "module_page" not in st.session_state:
    st.session_state.module_page = 1

# View routing
if st.session_state.view == "Login" and not st.session_state.user:
    render_login_view()
elif st.session_state.view == "Home" and st.session_state.user:
    render_home_view()
elif st.session_state.view == "Results" and st.session_state.user:
    render_results_view()
else:
    st.error("Please log in to access the hub!")
    st.session_state.view = "Login"
    st.rerun()

# Replace your sidebar block with this
if st.session_state.user and st.session_state.view in ["Home", "Results"]:
    with st.sidebar:
        st.subheader(f"Yo, {st.session_state.user['email'] if isinstance(st.session_state.user, dict) else st.session_state.user.email}")
        if st.button("Logout", key="sidebar_logout"):
            st.session_state.user = None
            st.session_state.view = "Login"
            st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)  # Teal divider
        with st.expander("Saved Modules", expanded=False):  # Collapsible
            render_saved_modules_view()

st.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")