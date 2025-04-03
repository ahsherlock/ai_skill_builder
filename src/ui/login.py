import streamlit as st
from src.config.settings import supabase

def render_login_view():
    st.subheader("Login to SkillBase")
    with st.form(key="login_form", clear_on_submit=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button(label="Login")
        
        if login_button:
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = response.user
                st.session_state.view = "Home"
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")