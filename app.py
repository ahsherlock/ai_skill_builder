
import streamlit as st
from datetime import datetime
from src.ui.login import render_login_view
from src.ui.home import render_home_view
from src.ui.results import render_results_view
from src.ui.saved_modules import render_saved_modules_view

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
elif st.session_state.view == "Home":
    render_home_view()
elif st.session_state.view == "Results":
    render_results_view()

# Saved Modules can be accessed from Home or Results
if st.session_state.user and st.session_state.view in ["Home", "Results"]:
    render_saved_modules_view()

st.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")