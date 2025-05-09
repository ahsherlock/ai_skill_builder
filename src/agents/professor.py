import requests
import json
from src.config.settings import GEMINI_API_KEY
import time

def generate_knowledge_base(skill):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Create a detailed knowledge base for the skill: {skill}. "
        "Include: 1. Introduction (overview), 2. Key Concepts (list), 3. Detailed explination of each Key Concept in list, 4. Examples (code/text). "
        "Return in markdown format as a single string."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4000
        }
    }
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            print(f"Knowledge base generated for {skill}")
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Gemini error in Professor (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    # Fallback
    return f"# {skill}\n## Introduction\nOverview of {skill}.\n## Key Concepts\n- Basics\n## Examples\n- Example 1"

def professor_agent(skills):
    knowledge_base = ""
    for skill in skills:
        knowledge_base += generate_knowledge_base(skill) + "\n\n"
    return knowledge_base.rstrip()