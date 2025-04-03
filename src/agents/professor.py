import requests
import json
from src.config.settings import GEMINI_API_KEY

def professor_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = f"Create a detailed knowledge base for {topic}. Include an introduction and examples in markdown format."
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini error in Professor: {e}")
        return f"# {topic} Knowledge Base\n## Introduction\nDetailed explanation here...\n## Examples\nExample 1: ..."