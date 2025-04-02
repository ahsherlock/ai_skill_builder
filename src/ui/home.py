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
        resume_file = st.file_uploader("Upload your resume (PDF, Word, or TXT)", type=["pdf", "docx", "txt"])
        if resume_file:
            file_type = resume_file.name.split(".")[-1].lower()
            initial_skills = resume_scanner_agent(resume_file, file_type)
            st.write("Detected Skills & Topics from Resume:")
            
            # Multi-select for user to keep/remove skills
            selected_skills = st.multiselect(
                "Choose skills/topics to include (deselect to remove):",
                options=initial_skills,
                default=initial_skills
            )
            if selected_skills:
                skills = selected_skills
            else:
                st.warning("Please select at least one skill/topic.")
                skills = None

    if st.button("Generate Learning Experience"):
        if topic or skills:
            st.session_state.topic = topic
            st.session_state.skills = skills
            st.session_state.view = "Results"
        else:
            st.error("Please provide a topic or select skills from your resume.")