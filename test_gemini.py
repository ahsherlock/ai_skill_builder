import requests
import json

GEMINI_API_KEY = "AIzaSyCOvC0Gobm5f0LaLPFvUa-aSBmD6ldOaFE"  # Paste your key
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
prompt = "Generate an Easy quiz question about Python. Return in JSON with 'question', 'correct_answer', 'points', and 'difficulty' fields."
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"response_mime_type": "application/json"}
}
response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
print(response.status_code)
print(response.text)