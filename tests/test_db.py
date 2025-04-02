import pytest
from src.db.supabase_client import save_modules

def test_save_modules():
    # Mock test (requires Supabase setup or mocking)
    modules = [{"user_id": "test-user", "skill": "Test", "content": "Test content"}]
    assert save_modules(modules)  # Adjust based on actual test setup