import requests
import json
from src.config.settings import GEMINI_API_KEY

def teaching_assistant_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    prompt = f"Generate exercises for {topic}. Include questions and solutions in markdown format."
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini error in Assistant: {e}")
        return f"# {topic} Exercises\n## Exercise 1\nQuestion: ...\nSolution: ..."