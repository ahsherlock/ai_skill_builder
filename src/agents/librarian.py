import requests
import json
from src.config.settings import GEMINI_API_KEY

def librarian_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = f"Compile a list of resources for {topic}. Include articles with URLs and descriptions in markdown format."
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini error in Librarian: {e}")
        return f"# {topic} Resources\n## Articles\n- [Link 1](url) - Beginner\n- [Link 2](url) - Advanced"