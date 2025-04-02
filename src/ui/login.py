import streamlit as st
from src.config.settings import supabase

def render_login_view():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user and response.user.email_confirmed_at:
                st.session_state.user = response.user
                st.session_state.view = "Home"
                st.success("Logged in successfully!")
            elif response.user:
                st.error("Please confirm your email before logging in.")
            else:
                st.error("Invalid credentials")

    with tab2:
        reg_email = st.text_input("New Email")
        reg_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            response = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
            if response.user:
                st.success("Registration successful! Please check your email to confirm your account.")
            else:
                st.error("Registration failed")