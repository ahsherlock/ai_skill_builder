import requests
import json
from src.config.settings import GEMINI_API_KEY
import time

def module_generator_agent(topic):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = (
        f"Generate a learning module for {topic} using Bloom's Taxonomy. Include markdown sections for: "
        "1. Remembering (key facts), 2. Understanding (explanations), 3. Applying (simple examples), "
        "4. Analyzing (breakdown of concepts), 5. Evaluating (judging approaches), 6. Creating (design task). "
        "Return in markdown format."
    )
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Gemini error in Module Generator (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(2 ** attempt)
    return (
        f"# Learning Module for {topic}\n"
        f"## Remembering\nKey facts about {topic}...\n"
        f"## Understanding\nExplaining {topic} basics...\n"
        f"## Applying\nSimple {topic} example...\n"
        f"## Analyzing\nBreaking down {topic}...\n"
        f"## Evaluating\nJudging {topic} approaches...\n"
        f"## Creating\nDesign a {topic} solution..."
    )