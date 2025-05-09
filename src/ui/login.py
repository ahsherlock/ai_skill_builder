import streamlit as st
from src.config.settings import supabase
import uuid

def render_login_view():
    st.subheader("Login to SkillBase")
    
    # Option to bypass login for testing purposes
    if st.checkbox("Bypass login for testing"):
        if st.button("Continue as test user"):
            # Create a mock user with a random ID
            mock_user = {
                "id": str(uuid.uuid4()),
                "email": "test@example.com",
                "user_metadata": {
                    "name": "Test User"
                }
            }
            st.session_state.user = mock_user
            st.session_state.view = "Home"
            st.success("Logged in as test user!")
            st.rerun()
    
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
                st.info("If login service is unavailable, use the 'Bypass login for testing' option above.")