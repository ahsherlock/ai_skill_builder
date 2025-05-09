import logging
from src.config.settings import supabase
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory fallback storage when Supabase is unavailable
memory_modules = []

def save_modules(modules):
    """
    Save a list of module dicts ({user_id, skill, content}) to Supabase 'modules' table.
    Falls back to in-memory storage if Supabase is unavailable.
    Returns True if successful, False if not.
    """
    try:
        # Insert modules into 'modules' table
        response = supabase.table("modules").insert(modules).execute()
        if response.data:
            logger.info(f"Saved {len(response.data)} modules to Supabase!")
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving modules to Supabase: {e}")
        # Fallback to in-memory storage
        global memory_modules
        for module in modules:
            # Add timestamp for sorting
            module_with_timestamp = module.copy()
            module_with_timestamp["created_at"] = time.time()
            memory_modules.append(module_with_timestamp)
        logger.info(f"Saved {len(modules)} modules to in-memory storage instead")
        return True

def get_module_count(user_id):
    try:
        response = supabase.table("modules").select("count", count="exact").eq("user_id", user_id).execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        logger.error(f"Error getting module count from Supabase: {e}")
        # Fallback to in-memory storage
        return len([m for m in memory_modules if m.get("user_id") == user_id])

def get_paginated_modules(user_id, page, per_page):
    try:
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page - 1
        response = supabase.table("modules").select("skill, content").eq("user_id", user_id).order("created_at", desc=True).range(start_idx, end_idx).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting paginated modules from Supabase: {e}")
        # Fallback to in-memory storage
        user_modules = [m for m in memory_modules if m.get("user_id") == user_id]
        # Sort by created_at timestamp in descending order
        sorted_modules = sorted(user_modules, key=lambda x: x.get("created_at", 0), reverse=True)
        # Get the page slice
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated = sorted_modules[start_idx:end_idx]
        # Return only the skill and content fields
        return [{"skill": m.get("skill"), "content": m.get("content")} for m in paginated]

def get_all_skills(user_id):
    try:
        response = supabase.table("modules").select("skill").eq("user_id", user_id).execute()
        return sorted(set(module["skill"] for module in response.data)) if response.data else []
    except Exception as e:
        logger.error(f"Error getting all skills from Supabase: {e}")
        # Fallback to in-memory storage
        user_modules = [m for m in memory_modules if m.get("user_id") == user_id]
        return sorted(set(module.get("skill") for module in user_modules))