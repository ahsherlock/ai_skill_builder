import streamlit as st
import pandas as pd
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
    skills = st.session_state.get("skills")

    if topic:
        with tabs[0]:
            st.write("🧠 Professor Agent: Knowledge Base")
            st.text_area("Knowledge Base", professor_agent(topic), height=200)

        with tabs[1]:
            st.write("🗺️ Academic Advisor Agent: Learning Path")
            st.text_area("Learning Path", advisor_agent(topic), height=200)

        with tabs[2]:
            st.write("📚 Research Librarian Agent: Resources")
            st.text_area("Resources", librarian_agent(topic), height=200)

        with tabs[3]:
            st.write("✍️ Teaching Assistant Agent: Exercises")
            st.text_area("Exercises", teaching_assistant_agent(topic), height=200)

    if skills:
        with tabs[4]:
            st.write("✍️ Quiz Generator Agent: Skill Assessment Quiz")
            quiz_output = quiz_generator_agent(skills)
            st.text_area("Quiz", quiz_output["quiz"], height=250)

            st.subheader("Take the Quiz")
            with st.form(key="quiz_form"):
                quiz_responses = {}
                for question, _, _, _, difficulty in quiz_output["questions"]:
                    quiz_responses[question] = st.text_input(f"[{difficulty}] {question}", "")
                submit_button = st.form_submit_button(label="Submit Quiz Answers")

            if submit_button:
                analysis = quiz_analyzer_agent(skills, quiz_responses, quiz_output["questions"])
                st.write("🔍 Quiz Analyzer Agent: Skill Assessment Results")
                st.write(f"Overall Proficiency: {analysis['total_score']:.2f}%")
                st.write("Skill Proficiency Breakdown:")
                for skill, score in analysis["proficiency"].items():
                    st.write(f"- {skill}: {score:.2f}%")
                
                st.subheader("Proficiency Visualization")
                proficiency_data = pd.DataFrame({
                    "Skill": list(analysis["proficiency"].keys()),
                    "Proficiency (%)": list(analysis["proficiency"].values())
                })
                st.bar_chart(proficiency_data.set_index("Skill"))

                st.write("Prioritized Skill Gaps:", analysis["gaps"])

                st.subheader("Learning Modules")
                modules = []
                for gap in analysis["gaps"]:
                    if gap != "No significant gaps detected":
                        module_content = module_generator_agent(gap)
                        with st.expander(f"Module for {gap}"):
                            st.text_area(f"Module_{gap}", module_content, height=150)
                            st.download_button(
                                label=f"Download {gap} Module",
                                data=module_content,
                                file_name=f"{gap}_module.txt",
                                mime="text/plain"
                            )
                        modules.append({"user_id": st.session_state.user.id, "skill": gap, "content": module_content})

                if modules:
                    if st.button("Save All Modules to Account"):
                        if save_modules(modules):
                            st.success("Modules saved to your account!")
                        else:
                            st.error("Failed to save modules")

    if st.button("Back to Home"):
        st.session_state.view = "Home"