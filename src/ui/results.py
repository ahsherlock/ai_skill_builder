import time
import streamlit as st
from src.agents.professor import professor_agent
from src.agents.advisor import advisor_agent
from src.agents.librarian import librarian_agent
from src.agents.assistant import teaching_assistant_agent
from src.agents.quiz import generate_questions, quiz_generator_agent
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
            if "quiz_output" not in st.session_state or st.session_state.get("regen_quiz", True):
                quiz_output = quiz_generator_agent(skills)
                quiz_content = quiz_output["quiz"]
                questions = quiz_output["questions"]
                quiz_container = st.empty()

                with st.spinner("Generating your quiz questions..."):
                    for skill, difficulty, bloom_level, q_type, used_questions in quiz_output["generator"]:
                        question_data = generate_questions(skill, difficulty, bloom_level, q_type, used_questions)
                        used_questions.add(question_data["question"])
                        options_str = "\n- " + "\n- ".join(question_data["options"])
                        quiz_content += (
                            f"**{question_data['question']}** ({difficulty}, {question_data['points']} points, Bloom's {question_data['bloom_level']})\n"
                            f"{options_str}\n\n"
                        )
                        questions.append((
                            question_data["question"],
                            skill,
                            question_data["correct_answer"],
                            question_data["points"],
                            question_data["difficulty"],
                            question_data["options"],
                            question_data["bloom_level"]
                        ))
                        quiz_container.text_area("Quiz", quiz_content, height=500)
                        time.sleep(1)
                st.session_state.quiz_output = {"quiz": quiz_content, "questions": questions}
                st.session_state.regen_quiz = False
            else:
                quiz_output = st.session_state.quiz_output
                st.text_area("Quiz", quiz_output["quiz"], height=500)

            with st.form(key="quiz_form"):
                responses = {
                    q[0]: st.radio(
                        f"Select answer for: {q[0]} (Bloom's {q[6]})",
                        options=q[5],
                        key=f"quiz_radio_{i}",
                        index=None
                    )
                    for i, q in enumerate(quiz_output["questions"])
                }
                if st.form_submit_button("Submit Quiz Answers"):
                    with st.spinner("Analyzing your quiz..."):
                        analysis = quiz_analyzer_agent(skills, responses, quiz_output["questions"])
                        st.session_state.analysis = analysis  # Store for regen option

            if "analysis" in st.session_state:
                analysis = st.session_state.analysis
                st.write("🔍 Quiz Analyzer Agent: Skill Assessment Results")
                st.write(f"**Total Score**: {analysis['total_score']:.1f}%")
                st.write("**Proficiency by Skill**:")
                for skill, score in analysis["proficiency"].items():
                    st.write(f"- {skill}: {score:.1f}%")
                if analysis["gaps"]:
                    st.write("**Skill Gaps (< 70%)**: {', '.join(analysis['gaps'])}")
                st.write("**Struggle Points (< 70%)**:")
                for skill, bloom_scores in analysis["struggle_points"].items():
                    if bloom_scores:
                        st.write(f"- {skill}:")
                        for bloom_level, score in bloom_scores.items():
                            st.write(f"  - {bloom_level}: {score}%")

                if analysis["gaps"]:
                    if st.button("Regenerate Learning Path with Struggle Points"):
                        st.session_state.skills = analysis["gaps"]  # Use gaps as new skills
                        st.session_state.regen_quiz = True  # Trigger quiz regen
                        st.session_state.analysis = None  # Clear old analysis
                        st.rerun()  # Restart flow with gaps
                else:
                    st.write("No significant gaps—keep mastering!")
    if st.button("Back to Home"):
        st.session_state.view = "Home"