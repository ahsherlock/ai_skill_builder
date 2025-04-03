import streamlit as st
from src.agents.resume import resume_scanner_agent, split_skills
from src.config.settings import supabase

def render_home_view():
    st.write(f"Welcome, {st.session_state.user.email}!")
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.view = "Login"
        st.rerun()

    option = st.selectbox("Choose your starting point:", ["Enter a Topic", "Upload a Resume"])

    with st.form(key="home_form", clear_on_submit=False):
        topic = None
        skills = None

        if option == "Enter a Topic":
            topic_input = st.text_input("What topic would you like to learn about?")
            if topic_input:
                topic_list = split_skills(topic_input)
                if len(topic_list) > 1:
                    st.write("Detected multiple topics/skills:")
                    selected_topics = st.multiselect("Choose topics to include:", topic_list, default=topic_list)
                    skills = selected_topics if selected_topics else None
                else:
                    topic = topic_list[0]
        elif option == "Upload a Resume":
            resume_file = st.file_uploader("Upload your resume (PDF, Word, or TXT)", type=["pdf", "docx", "txt"])
            if resume_file:
                file_type = resume_file.name.split(".")[-1].lower()
                initial_skills = resume_scanner_agent(resume_file, file_type)
                st.write("Detected Skills & Topics from Resume:")
                selected_skills = st.multiselect("Choose skills/topics to include:", initial_skills, default=initial_skills)
                skills = selected_skills if selected_skills else None

        # Form submit button
        submit_button = st.form_submit_button(label="Generate Learning Experience")

        # Handle submission (Enter or click)
        if submit_button:
            if topic or skills:
                st.session_state.topic = topic
                st.session_state.skills = skills
                st.session_state.view = "Results"
                st.rerun()  # Immediate switch to Results
            else:
                st.error("Please provide a topic or select skills.")