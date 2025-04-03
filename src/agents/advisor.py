import requests
import json
from src.config.settings import GEMINI_API_KEY

def advisor_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = f"Design a learning path for {topic}. Include milestones and prerequisites in markdown format."
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini error in Advisor: {e}")
        return f"# {topic} Learning Path\n## Milestones\n1. Basics (1 week)\n2. Intermediate (2 weeks)\n## Prerequisites\nNone"