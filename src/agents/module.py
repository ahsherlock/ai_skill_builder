import requests
import json
from src.config.settings import GEMINI_API_KEY

def module_generator_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    prompt = f"Generate a learning module for {topic}. Include a title, focus area, and detailed content in markdown format."
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        module_content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return module_content
    except Exception as e:
        print(f"Gemini error in Module Generator: {e}")
        return f"# Learning Module for {topic}\n## Focus Area\nGeneral overview\n## Content\nPlaceholder content..."