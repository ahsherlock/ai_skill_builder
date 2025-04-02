import streamlit as st
from src.agents.professor import professor_agent
from src.agents.advisor import advisor_agent
from src.agents.librarian import librarian_agent
from src.agents.assistant import teaching_assistant_agent
from src.agents.quiz import quiz_generator_agent
from src.agents.analyzer import quiz_analyzer_agent
from src.agents.module import module_generator_agent
from src.db.supabase_client import save_modules

def render_results_view():
    st.subheader("Your AI Teaching Team Results")
    tabs = st.tabs(["Knowledge Base", "Learning Path", "Resources", "Exercises", "Skill Assessment"])
    topic = st.session_state.get("topic")
    skills = st.session_state.get("skills") or ([topic] if topic else ["General"])
    print(f"Topic: {topic}, Skills: {skills}")

    if topic:
        with tabs[0]:
            st.write("🧠 Professor Agent: Knowledge Base")
            kb_output = professor_agent(topic)
            print(f"KB Output: {kb_output}")
            st.text_area("Knowledge Base", kb_output, height=200)
        with tabs[1]:
            st.write("🗺️ Academic Advisor Agent: Learning Path")
            lp_output = advisor_agent(topic)
            print(f"LP Output: {lp_output}")
            st.text_area("Learning Path", lp_output, height=200)
        with tabs[2]:
            st.write("📚 Research Librarian Agent: Resources")
            res_output = librarian_agent(topic)
            print(f"Res Output: {res_output}")
            st.text_area("Resources", res_output, height=200)
        with tabs[3]:
            st.write("✍️ Teaching Assistant Agent: Exercises")
            ex_output = teaching_assistant_agent(topic)
            print(f"Ex Output: {ex_output}")
            st.text_area("Exercises", ex_output, height=200)

    if skills:
        with tabs[4]:
            st.write("✍️ Quiz Generator Agent: Skill Assessment Quiz")
            quiz_output = quiz_generator_agent(skills)
            print(f"Quiz Output: {quiz_output['quiz']}")
            st.text_area("Quiz", quiz_output["quiz"], height=250)

            with st.form(key="quiz_form"):
                # Add unique keys using question index
                responses = {
                    q[0]: st.text_input(f"Answer: {q[0]}", key=f"quiz_input_{i}")
                    for i, q in enumerate(quiz_output["questions"])
                }
                if st.form_submit_button("Submit Quiz Answers"):
                    analysis = quiz_analyzer_agent(skills, responses, quiz_output["questions"])
                    st.write("🔍 Quiz Analyzer Agent: Skill Assessment Results")
                    st.json(analysis)

                    if analysis["gaps"]:
                        st.write("Generating modules for skill gaps...")
                        modules = [{"user_id": st.session_state.user.id, "skill": gap, "content": module_generator_agent(gap)} for gap in analysis["gaps"]]
                        if save_modules(modules):
                            st.success("Modules saved successfully!")
                        else:
                            st.error("Failed to save modules.")
                    else:
                        st.write("No significant gaps detected—keep mastering!")

    if st.button("Back to Home"):
        st.session_state.view = "Home"