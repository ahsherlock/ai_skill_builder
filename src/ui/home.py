import streamlit as st
from src.agents.resume import resume_scanner_agent, split_skills
from src.config.settings import supabase

def render_home_view():
    # Replace your welcome line
    user_email = getattr(st.session_state.user, 'email', None)
    if not user_email and isinstance(st.session_state.user, dict):
        user_email = st.session_state.user.get('email', 'Skilled One')
    st.markdown(f"### Yo, {user_email}, ready to sharpen your blade?")
    
    # Add columns for radio
    col1, col2 = st.columns([2, 1])
    with col1:
        option = st.radio("Pick your path:", ["Enter a Topic", "Upload a Resume"], horizontal=True)
    
    # Store parsed resume skills in session state
    if "parsed_resume_skills" not in st.session_state:
        st.session_state.parsed_resume_skills = []
    
    # Handle topic input
    if option == "Enter a Topic":
        with st.form(key="topic_form", clear_on_submit=False):
            topic_input = st.text_input("What's your skill grind?", placeholder="e.g., Python, Java", key="topic_input")
            
            submit_topic = st.form_submit_button("Forge My Path", use_container_width=True)
            
            if submit_topic:
                if topic_input:
                    topic_list = split_skills(topic_input)
                    if len(topic_list) > 1:
                        st.session_state.skills = topic_list
                        st.session_state.topic = None
                    else:
                        st.session_state.topic = topic_list[0]
                        st.session_state.skills = None
                    
                    st.session_state.view = "Results"
                    st.rerun()
                else:
                    st.error("Gimme a topic or skills to work with!")
    
    # Handle resume upload
    elif option == "Upload a Resume":
        # File uploader outside the form
        resume_file = st.file_uploader("Drop your resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="resume_upload")
        
        if resume_file:
            # Process the resume file to extract skills
            if st.button("Analyze Resume", key="analyze_resume"):
                with st.spinner("Analyzing your resume..."):
                    file_type = resume_file.name.split(".")[-1].lower()
                    extracted_skills = resume_scanner_agent(resume_file, file_type)
                    st.session_state.parsed_resume_skills = extracted_skills
            
            # Display extracted skills if available
            if st.session_state.parsed_resume_skills:
                st.success(f"Found {len(st.session_state.parsed_resume_skills)} skills in your resume!")
                
                # Form for selecting skills and submitting
                with st.form(key="skills_form"):
                    st.markdown("### Select skills you want to focus on:")
                    selected_skills = st.multiselect(
                        "Choose which skills to develop:",
                        st.session_state.parsed_resume_skills,
                        default=[],
                        key="selected_skills"
                    )
                    
                    submit_skills = st.form_submit_button("Forge My Path with Selected Skills", use_container_width=True)
                    
                    if submit_skills:
                        if selected_skills:
                            st.session_state.skills = selected_skills
                            st.session_state.topic = None
                            st.session_state.view = "Results"
                            st.rerun()
                        else:
                            st.error("Please select at least one skill from your resume to continue")