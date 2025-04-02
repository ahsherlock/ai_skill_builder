from src.config.settings import supabase

def save_modules(modules):
    response = supabase.table("modules").insert(modules).execute()
    return response.data is not None

def get_module_count(user_id):
    response = supabase.table("modules").select("count", count="exact").eq("user_id", user_id).execute()
    return response.count if response.count is not None else 0

def get_paginated_modules(user_id, page, per_page):
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page - 1
    response = supabase.table("modules").select("skill, content").eq("user_id", user_id).order("created_at", desc=True).range(start_idx, end_idx).execute()
    return response.data

def get_all_skills(user_id):
    response = supabase.table("modules").select("skill").eq("user_id", user_id).execute()
    return sorted(set(module["skill"] for module in response.data)) if response.data else []