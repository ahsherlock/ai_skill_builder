import requests
import json
from src.config.settings import GEMINI_API_KEY

def quiz_analyzer_agent(skills, quiz_responses, questions):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    prompt = (
        "Analyze these quiz responses for skills: {}\n\n"
        "Questions and correct answers:\n{}\n\n"
        "User responses:\n{}\n\n"
        "Return a JSON object with total_score (percentage), proficiency (dict of skill:percentage), and gaps (list of skills needing work)."
    ).format(
        ", ".join(skills),
        "\n".join([f"Q: {q[0]}\nA: {q[2]}" for q in questions]),
        "\n".join([f"Q: {k}\nA: {v}" for k, v in quiz_responses.items()])
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        analysis = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        return analysis
    except Exception as e:
        print(f"Gemini error in Quiz Analyzer: {e}")
        # Fallback logic
        total_points = sum(q[3] for q in questions)
        earned_points = sum(q[3] if quiz_responses.get(q[0], "").lower() == q[2].lower() else q[3] * 0.5 if q[2].lower() in quiz_responses.get(q[0], "").lower() else 0 for q in questions)
        total_score = (earned_points / total_points) * 100 if total_points > 0 else 0
        proficiency = {skill: total_score for skill in skills}
        gaps = [skill for skill in skills if total_score < 70]
        return {"total_score": total_score, "proficiency": proficiency, "gaps": gaps}