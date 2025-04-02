import pytest
from src.agents.professor import professor_agent

def test_professor_agent():
    result = professor_agent("Test Topic")
    assert "# Test Topic Knowledge Base" in result