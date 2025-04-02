import streamlit as st
from src.agents.resume import resume_scanner_agent
from src.config.settings import supabase

def render_home_view():
    st.write(f"Welcome, {st.session_state.user.email}!")
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.view = "Login"

    option = st.selectbox("Choose your starting point:", ["Enter a Topic", "Upload a Resume"])
    topic = None
    skills = None

    if option == "Enter a Topic":
        topic = st.text_input("What topic would you like to learn about?")
    elif option == "Upload a Resume":
        resume_file = st.file_uploader("Upload your resume (text file)", type=["txt"])
        if resume_file:
            resume_text = resume_file.read().decode("utf-8")
            skills = resume_scanner_agent(resume_text)
            st.write("Detected Skills:", skills)

    if st.button("Generate Learning Experience"):
        if topic or skills:
            st.session_state.topic = topic
            st.session_state.skills = skills
            st.session_state.view = "Results"