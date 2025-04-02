import streamlit as st
from src.db.supabase_client import get_module_count, get_paginated_modules, get_all_skills
from src.config.settings import MODULES_PER_PAGE

def render_saved_modules_view():
    if st.button("View Saved Modules"):
        st.subheader("Saved Modules")
        page = st.session_state.module_page

        # Get total count and paginated modules
        total_modules = get_module_count(st.session_state.user.id)
        total_pages = (total_modules + MODULES_PER_PAGE - 1) // MODULES_PER_PAGE
        modules = get_paginated_modules(st.session_state.user.id, page, MODULES_PER_PAGE)

        if modules:
            # Skill filter
            skill_options = ["All"] + get_all_skills(st.session_state.user.id)
            selected_skill = st.selectbox("Filter by Skill", skill_options)
            
            filtered_modules = [m for m in modules if selected_skill == "All" or m["skill"] == selected_skill]
            
            if filtered_modules:
                for module in filtered_modules:
                    with st.expander(f"Skill: {module['skill']}"):
                        st.text_area(f"Saved_{module['skill']}", module["content"], height=150)
                        st.download_button(
                            label=f"Download {module['skill']} Module",
                            data=module["content"],
                            file_name=f"{module['skill']}_module.txt",
                            mime="text/plain"
                        )
            else:
                st.write("No modules match the selected skill.")

            # Pagination controls
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if page > 1:
                    if st.button("Previous"):
                        st.session_state.module_page -= 1
                        st.experimental_rerun()
            with col2:
                st.write(f"Page {page} of {total_pages}")
            with col3:
                if page < total_pages:
                    if st.button("Next"):
                        st.session_state.module_page += 1
                        st.experimental_rerun()
        else:
            st.error("No saved modules found or failed to retrieve")