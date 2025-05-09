import streamlit as st
import json
from src.agents.quiz import quiz_generator_agent
from src.agents.analyzer import quiz_analyzer_agent
from src.agents.advisor import advisor_agent
from src.agents.assistant import assistant_agent
from src.agents.librarian import librarian_agent
from src.agents.module import module_generator_agent
from src.agents.professor import professor_agent
from src.db.supabase_client import save_modules
import time

def render_results_view():
    topic = st.session_state.get("topic")
    skills = st.session_state.get("skills", [])
    tabs = st.tabs(["📚 Knowledge Base", "🗺️ Learning Path", "📖 Resources", "🏋️ Exercises", "✍️ Skill Assessment"])

    with tabs[0]:
        st.write("📚 Professor Agent: Knowledge Base")
        if "knowledge_base" not in st.session_state:
            with st.spinner("Building your knowledge base..."):
                try:
                    st.session_state.knowledge_base = professor_agent(skills or [topic])
                except Exception as e:
                    st.error(f"Error building knowledge base: {str(e)}")
                    st.session_state.knowledge_base = f"# Knowledge Base for {', '.join(skills or [topic])}\n\nError generating content. Please try again later."
        
        # Safely display the knowledge base
        try:
            st.markdown(st.session_state.knowledge_base)
        except:
            st.error("Error displaying knowledge base content.")
            st.text(str(st.session_state.knowledge_base)[:1000] + "...")

    with tabs[1]:
        st.write("🗺️ Advisor Agent: Learning Path")
        if "learning_path" not in st.session_state:
            with st.spinner("Mapping your path..."):
                st.session_state.learning_path = advisor_agent(skills or [topic])
        
        learning_path = st.session_state.learning_path
        
        # Safety check - ensure learning_path is a dictionary
        if not learning_path:
            st.error("Learning path could not be generated. Please try again.")
            st.session_state.learning_path = None
            return
            
        # Make sure learning_path is a dictionary    
        if not isinstance(learning_path, dict):
            try:
                # Try to convert to dictionary if it's a string
                if isinstance(learning_path, str):
                    learning_path = json.loads(learning_path)
                else:
                    st.error("Learning path is in an invalid format. Please try again.")
                    st.session_state.learning_path = None
                    return
            except:
                st.error("Learning path data is corrupted. Please try again.")
                st.session_state.learning_path = None
                return
            
        # Introduction
        st.markdown("## Introduction")
        st.markdown(learning_path.get("introduction", ""))
        
        # Skill Components
        st.markdown("## Skill Components")
        skill_components = learning_path.get("skill_components", [])
        if skill_components and isinstance(skill_components, list):
            for component in skill_components:
                st.markdown(f"- {component}")
        else:
            st.markdown("No skill components found.")
        
        # Learning Path
        st.markdown("## Learning Path")
        learning_paths = learning_path.get("learning_path", [])
        if learning_paths and isinstance(learning_paths, list):
            for path in learning_paths:
                if not isinstance(path, dict):
                    continue
                st.markdown(f"### {path.get('level', '')}")
                st.markdown(path.get('description', ''))
                st.markdown("**Resources:**")
                resources = path.get('resources', [])
                if resources and isinstance(resources, list):
                    for resource in resources:
                        st.markdown(f"- {resource}")
                else:
                    st.markdown("No resources found.")
        else:
            st.markdown("No learning path information found.")
        
        # Challenges
        st.markdown("## Common Challenges and Solutions")
        challenges = learning_path.get("challenges", [])
        if challenges and isinstance(challenges, list):
            for challenge in challenges:
                if isinstance(challenge, dict):
                    st.markdown(f"**{challenge.get('challenge', '')}:** {challenge.get('solution', '')}")
        else:
            st.markdown("No challenges found.")
        
        # Practice Exercises
        st.markdown("## Practice Exercises")
        exercises = learning_path.get("practice_exercises", [])
        if exercises and isinstance(exercises, list):
            for exercise in exercises:
                st.markdown(f"- {exercise}")
        else:
            st.markdown("No practice exercises found.")
        
        # Progress Metrics
        st.markdown("## Progress Metrics")
        metrics = learning_path.get("progress_metrics", [])
        if metrics and isinstance(metrics, list):
            for metric in metrics:
                st.markdown(f"- {metric}")
        else:
            st.markdown("No progress metrics found.")
        
        # Time Commitment
        st.markdown("## Time Commitment")
        st.markdown(learning_path.get("time_commitment", ""))
        
        # Show raw JSON in expandable section
        with st.expander("View Raw JSON"):
            st.json(learning_path)

    with tabs[2]:
        st.write("📖 Librarian Agent: Resources")
        if "resources" not in st.session_state:
            with st.spinner("Gathering resources..."):
                try:
                    st.session_state.resources = librarian_agent(skills or [topic])
                except Exception as e:
                    st.warning(f"Error gathering resources: {str(e)}")
                    st.session_state.resources = {}
        
        # Get learning path resources
        learning_path_resources = []
        if "learning_path" in st.session_state and isinstance(st.session_state.learning_path, dict):
            for path in st.session_state.learning_path.get("learning_path", []):
                if isinstance(path, dict) and "level" in path and "resources" in path:
                    level = path.get("level", "")
                    for resource in path.get("resources", []):
                        if resource and isinstance(resource, str):
                            learning_path_resources.append({
                                "title": resource,
                                "url": "",
                                "level": level
                            })
        
        # Function to safely process JSON
        def safely_load_json(json_str):
            try:
                # Handle common JSON formatting issues
                json_str = json_str.strip()
                if json_str.startswith("```json"):
                    json_str = json_str.split("```json", 1)[1]
                if json_str.endswith("```"):
                    json_str = json_str.rsplit("```", 1)[0]
                
                # Fix trailing commas (invalid in JSON)
                import re
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                return json.loads(json_str.strip())
            except Exception as e:
                print(f"JSON parsing error: {e}")
                return None
        
        # Display all resources in a well-formatted way
        st.markdown("## 📚 All Learning Resources")
        
        # Ensure resources is a dictionary
        if not isinstance(st.session_state.resources, dict):
            try:
                # Try to convert to dictionary if it's a string
                if isinstance(st.session_state.resources, str):
                    parsed = safely_load_json(st.session_state.resources)
                    if parsed:
                        st.session_state.resources = parsed
                    else:
                        st.session_state.resources = {skill: [] for skill in (skills or [topic])}
                else:
                    st.session_state.resources = {skill: [] for skill in (skills or [topic])}
            except:
                st.session_state.resources = {skill: [] for skill in (skills or [topic])}
                st.session_state.resources = {skill: [] for skill in (skills or [topic])}
        
        # Display resources from librarian agent
        if st.session_state.resources:
            try:
                skill_keys = list(st.session_state.resources.keys())
                if skill_keys:
                    tabs_skills = st.tabs(skill_keys)
                    
                    for i, (skill, resources) in enumerate(st.session_state.resources.items()):
                        with tabs_skills[i]:
                            st.markdown(f"### Resources for {skill}")
                        
                        if isinstance(resources, list):
                            # Group resources by level
                            resources_by_level = {
                                "Beginner": [],
                                "Intermediate": [],
                                "Advanced": [],
                                "All levels": [],
                                "Other": []
                            }
                            
                            for resource in resources:
                                if isinstance(resource, dict):
                                    level = resource.get("level", "Other")
                                    if level not in resources_by_level:
                                        resources_by_level["Other"].append(resource)
                                    else:
                                        resources_by_level[level].append(resource)
                            
                            # Display resources by level
                            for level, level_resources in resources_by_level.items():
                                if level_resources:
                                    with st.expander(f"{level} ({len(level_resources)} resources)", expanded=(level == "Beginner")):
                                        for j, resource in enumerate(level_resources):
                                            title = resource.get("title", f"Resource {j+1}")
                                            url = resource.get("url", "")
                                            description = resource.get("description", "")
                                            format_type = resource.get("format", "")
                                            cost = resource.get("cost", "")
                                            time = resource.get("time_commitment", "")
                                            
                                            # Title with link
                                            if url:
                                                st.markdown(f"#### {j+1}. [{title}]({url})")
                                            else:
                                                st.markdown(f"#### {j+1}. {title}")
                                            
                                            # Resource details
                                            col1, col2, col3 = st.columns([1,1,1])
                                            with col1:
                                                st.markdown(f"**Format:** {format_type}")
                                            with col2:
                                                st.markdown(f"**Cost:** {cost}")
                                            with col3:
                                                st.markdown(f"**Time:** {time}")
                                            
                                            # Description
                                            if description:
                                                st.markdown(f"{description}")
                                        
                                            st.markdown("---")
                            else:
                                st.markdown("No resources available for this skill.")
            except Exception as e:
                st.error(f"Error displaying resources: {str(e)}")
                st.warning("No skills found in the resources or resources are in an invalid format.")
                st.session_state.resources = {skill: [] for skill in (skills or [topic])}
        else:
            st.warning("No resources were generated by the librarian agent. Try selecting different skills or try again later.")
            # Add a button to retry
            if st.button("Retry generating resources"):
                st.session_state.resources = None
                st.rerun()
            
        # Display learning path resources
        if learning_path_resources:
            with st.expander("Additional Resources from Learning Path", expanded=True):
                st.markdown("### Resources from Learning Path")
                
                # Group by level
                levels = {}
                for res in learning_path_resources:
                    level = res.get("level", "Other")
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(res)
                
                # Display by level
                for level, resources in levels.items():
                    st.markdown(f"#### {level} Level")
                    
                    # Create a grid layout for resources
                    cols = st.columns(2)
                    for i, res in enumerate(resources):
                        with cols[i % 2]:
                            title = res.get("title", f"Resource {i+1}")
                            url = res.get("url", "")
                            
                            if url:
                                st.markdown(f"**[{title}]({url})**")
                            else:
                                st.markdown(f"**{title}**")
                            
                            # Add a divider except for the last item
                            if i < len(resources) - 1:
                                st.markdown("---")
        
        # Resource finder tip
        with st.expander("How to find more resources"):
            st.markdown("""
            ### Tips for finding quality learning resources:
            
            1. **Search specific sites**: Try adding "site:coursera.org" or "site:freecodecamp.org" to your Google searches
            2. **Check GitHub**: Look for repositories with "awesome-" prefix, like "awesome-python"
            3. **Use platforms like**: Coursera, edX, Udemy, Pluralsight, LinkedIn Learning, or O'Reilly
            4. **Find documentation**: Official documentation is often the best resource
            
            #### Recommended Learning Platforms:
            | Platform | Best For | Cost |
            | --- | --- | --- |
            | [Codecademy](https://www.codecademy.com/) | Interactive coding practice | Freemium |
            | [FreeCodeCamp](https://www.freecodecamp.org/) | Full stack development | Free |
            | [Khan Academy](https://www.khanacademy.org/) | Computer science fundamentals | Free |
            | [HackerRank](https://www.hackerrank.com/) | Coding challenges | Free |
            | [LeetCode](https://leetcode.com/) | Interview prep | Freemium |
            | [Coursera](https://www.coursera.org/) | University-level courses | Freemium |
            | [edX](https://www.edx.org/) | Academic courses | Freemium |
            
            #### Pro Tip: 
            Create a learning plan that combines different resource types: video courses for introduction, interactive platforms for practice, documentation for reference, and projects for application.
            """)
            
            # Add a checklist for tracking resource use
            st.markdown("#### Resource Tracking:")
            st.checkbox("I've bookmarked all useful resources")
            st.checkbox("I've created a learning schedule")
            st.checkbox("I've joined relevant online communities")

    with tabs[3]:
        st.write("🏋️ Assistant Agent: Exercises")
        if "exercises" not in st.session_state or st.session_state.exercises is None or st.session_state.get("regen_exercises", False):
            with st.spinner("Generating exercises..."):
                try:
                    st.session_state.exercises = assistant_agent(skills or [topic])
                    st.session_state.regen_exercises = False
                except Exception as e:
                    st.error(f"Error generating exercises: {str(e)}")
                    st.session_state.exercises = {skill: f"### Exercises for {skill}\n1. Practice basic {skill} concepts\n2. Build a simple project using {skill}\n3. Create documentation for your {skill} project" for skill in (skills or [topic])}
        
        # Safely display exercises
        if st.session_state.exercises:
            try:
                # Check if exercises is a dictionary
                if isinstance(st.session_state.exercises, dict):
                    st.markdown("\n\n".join(f"### {skill}\n{ex_text}" for skill, ex_text in st.session_state.exercises.items()))
                else:
                    st.markdown(str(st.session_state.exercises))
            except:
                st.error("Error displaying exercises.")
                st.text(str(st.session_state.exercises)[:1000] + "...")
        else:
            st.write("No exercises generated yet—try again!")

    with tabs[4]:
        st.write("✍️ Quiz Time—Test Your Edge")
        if "quiz_output" not in st.session_state or st.session_state.get("regen_quiz", False):
            with st.spinner("Crafting your quiz (this might take a sec)..."):
                try:
                    st.session_state.quiz_output = quiz_generator_agent(skills or [topic])
                    st.session_state.regen_quiz = False
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
                    st.session_state.quiz_output = {
                        "quiz": f"# Quiz for {', '.join(skills or [topic])}\n\n1. What is the primary purpose of {skills[0] if skills else topic}?\n2. Name three core concepts in {skills[0] if skills else topic}.",
                        "questions": [
                            (f"What is the primary purpose of {skills[0] if skills else topic}?", "Easy", "Remember", "Multiple Choice", None, ["a) Wrong answer", "b) Wrong answer", "c) Wrong answer", "d) Correct answer"], "d"),
                            (f"Name three core concepts in {skills[0] if skills else topic}?", "Medium", "Understand", "Multiple Choice", None, ["a) Wrong answer", "b) Wrong answer", "c) Wrong answer", "d) Correct answer"], "d")
                        ]
                    }
        
        # Safely display quiz
        try:
            if isinstance(st.session_state.quiz_output, dict) and "quiz" in st.session_state.quiz_output:
                st.text_area("Quiz", st.session_state.quiz_output["quiz"], height=600)
            else:
                st.error("Quiz data is not in the expected format.")
                st.text_area("Quiz", str(st.session_state.quiz_output), height=600)
        except:
            st.error("Error displaying quiz content.")

        with st.form(key="quiz_form"):
            responses = {
                q[0]: st.radio(f"{q[0]} (Bloom's {q[2]})", q[5], key=f"quiz_radio_{i}", index=None)
                for i, q in enumerate(st.session_state.quiz_output["questions"])
            }
            if st.form_submit_button("Grade Me", use_container_width=True):
                with st.spinner("Analyzing your skills..."):
                    analysis = quiz_analyzer_agent(skills or [topic], responses, st.session_state.quiz_output["questions"])
                    st.session_state.analysis = analysis

        if "analysis" in st.session_state:
            analysis = st.session_state.analysis
            st.markdown(f"<h2 style='color: #00ebeb; animation: fadeIn 1s;'>Score: {analysis['total_score']:.1f}%</h2>", unsafe_allow_html=True)
            st.progress(analysis["total_score"] / 100)

            if analysis["feedback"]:
                st.write("**Your Mistakes—Learn from ‘Em**:")
                for q_text, fb in analysis["feedback"].items():
                    st.markdown(
                        f"**{q_text}**<br>"
                        f"- You picked: '{next(q['user_answer'] for q in analysis['graded_questions'] if q['question'] == q_text)}'<br>"
                        f"- Why wrong: {fb.get('why_wrong', 'No explanation available')}<br>"
                        f"- Correct: '{next(q['correct_answer'] for q in analysis['graded_questions'] if q['question'] == q_text)}'<br>"
                        f"- Why correct: {fb.get('why_correct', 'No explanation available')}",
                        unsafe_allow_html=True
                    )

            st.write(f"**{skills[0]} Subskill Breakdown**:")
            for subskill, score in analysis["proficiency"].items():
                st.write(f"- {subskill}: {score:.1f}%")

            if analysis["struggle_points"]:
                st.write("**Struggle Points**:")
                for subskill, score in analysis["struggle_points"].items():
                    st.markdown(f"- {subskill}: {score:.1f}%", unsafe_allow_html=True)

            if analysis["gaps"]:
                st.write("**Knowledge Gaps**:")
                st.write(", ".join(analysis["gaps"]))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Regen All Gaps", use_container_width=True):
                        st.session_state.skills = analysis["gaps"]
                        st.session_state.regen_quiz = True
                        st.session_state.regen_exercises = True
                        st.session_state.analysis = None
                        st.session_state.knowledge_base = None
                        st.session_state.learning_path = None
                        st.session_state.resources = None
                        st.session_state.exercises = None
                        st.rerun()
                with col2:
                    struggle_subskills = list(analysis["struggle_points"].keys())
                    selected = st.selectbox("Focus on one:", struggle_subskills)
                    if st.button("Regen This Subskill", use_container_width=True):
                        st.session_state.skills = [selected]
                        st.session_state.regen_quiz = True
                        st.session_state.regen_exercises = True
                        st.session_state.analysis = None
                        st.session_state.knowledge_base = None
                        st.session_state.learning_path = None
                        st.session_state.resources = None
                        st.session_state.exercises = None
                        st.rerun()
            # Generate Modules for Gaps
            if analysis["gaps"] and "modules" not in st.session_state:
                with st.spinner("Generating modules for skill gaps..."):
                    # Get user ID safely
                    user_id = None
                    if hasattr(st.session_state.user, 'id'):
                        user_id = st.session_state.user.id
                    elif isinstance(st.session_state.user, dict):
                        user_id = st.session_state.user.get('id')
                    
                    if user_id:
                        modules = [{"user_id": user_id, "skill": gap, "content": module_generator_agent(gap)} for gap in analysis["gaps"]]
                        if save_modules(modules):
                            st.session_state.modules = modules
                            st.success("Modules saved successfully!")
                        else:
                            st.error("Failed to save modules.")
                    else:
                        st.warning("User ID not found. Modules will not be saved.")
                        st.session_state.modules = [{"skill": gap, "content": module_generator_agent(gap)} for gap in analysis["gaps"]]
            if "modules" in st.session_state:
                st.write("### Learning Modules for Gaps")
                for module in st.session_state.modules:
                    st.markdown(f"#### {module['skill']}\n{module['content']}")