import streamlit as st
import logging
from src.db.supabase_client import get_module_count, get_paginated_modules, get_all_skills
from src.config.settings import MODULES_PER_PAGE

# Configure logging
logger = logging.getLogger(__name__)

def render_saved_modules_view():
    if st.button("View Saved Modules"):
        st.subheader("Saved Modules")
        
        # Initialize module_page if not in session state
        if "module_page" not in st.session_state:
            st.session_state.module_page = 1
            
        page = st.session_state.module_page
        
        try:
            # Get user ID safely
            user_id = getattr(st.session_state.get("user", {}), "id", None)
            if not user_id:
                st.warning("User information not found. Please log in again.")
                return
                
            # Get total count and paginated modules
            total_modules = get_module_count(user_id)
            total_pages = max(1, (total_modules + MODULES_PER_PAGE - 1) // MODULES_PER_PAGE)
            modules = get_paginated_modules(user_id, page, MODULES_PER_PAGE)

            if modules:
                # Skill filter
                skill_options = ["All"] + get_all_skills(user_id)
                selected_skill = st.selectbox("Filter by Skill", skill_options)
                
                filtered_modules = [m for m in modules if selected_skill == "All" or m.get("skill") == selected_skill]
                
                if filtered_modules:
                    for module in filtered_modules:
                        skill = module.get("skill", "Unknown")
                        content = module.get("content", "Content not available")
                        with st.expander(f"Skill: {skill}"):
                            st.text_area(f"Saved_{skill}", content, height=150)
                            st.download_button(
                                label=f"Download {skill} Module",
                                data=content,
                                file_name=f"{skill}_module.txt",
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
                            st.rerun()
                with col2:
                    st.write(f"Page {page} of {total_pages}")
                with col3:
                    if page < total_pages:
                        if st.button("Next"):
                            st.session_state.module_page += 1
                            st.rerun()
            else:
                st.info("No saved modules found. Create some skill modules to see them here.")
        except Exception as e:
            logger.error(f"Error in saved modules view: {e}")
            st.error(f"Failed to load saved modules: {str(e)}")
            st.info("Try reloading the page or logging in again.")