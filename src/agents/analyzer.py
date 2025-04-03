import requests
import json
from src.config.settings import GEMINI_API_KEY
import time

def quiz_analyzer_agent(skills, quiz_responses, questions):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = (
        "Analyze these quiz responses for skills: {}\n\n"
        "Questions, options, correct answers, and Bloom's levels:\n{}\n\n"
        "User responses:\n{}\n\n"
        "For True/False: full points (1, 3, 5) for correct, 0 for wrong. "
        "For MCQs (3 options): 0 for completely wrong, half for kind of wrong, full for correct. "
        "For Hard MCQs (6 options): 0, 1, 2, 3, 4, 5 points from completely wrong to absolutely correct. "
        "Return JSON with: total_score (percentage), proficiency (dict of skill:percentage), "
        "gaps (skills < 70%), and struggle_points (dict of skill:bloom_level:percentage for < 70%)."
    ).format(
        ", ".join(skills),
        "\n".join([f"Q: {q[0]}\nOptions: {', '.join(q[5])}\nA: {q[2]}\nBloom: {q[6]}" for q in questions]),
        "\n".join([f"Q: {k}\nA: {v}" for k, v in quiz_responses.items()])
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            analysis = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
            return analysis
        except Exception as e:
            print(f"Gemini error in Quiz Analyzer (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    
    # Fallback scoring
    total_points = sum(q[3] for q in questions)
    earned_points = 0
    skill_scores = {skill: {"points": 0, "total": 0} for skill in skills}
    struggle_points = {skill: {} for skill in skills}
    bloom_scores = {skill: {level: {"points": 0, "total": 0} for level in ["Remembering", "Understanding", "Applying", "Analyzing", "Evaluating", "Creating"]} for skill in skills}

    for q in questions:
        question, skill, correct, points, difficulty, options, bloom_level = q
        user_answer = quiz_responses.get(question, "")
        if len(options) == 2:  # T/F
            earned = points if user_answer == correct else 0
        elif len(options) == 3:  # Easy/Medium MCQ
            earned = points if user_answer == correct else (points / 2 if user_answer == options[1] else 0)
        else:  # Hard MCQ (6 options)
            earned = [0, 1, 2, 3, 4, 5][options.index(user_answer)] if user_answer in options else 0
        earned_points += earned
        skill_scores[skill]["points"] += earned
        skill_scores[skill]["total"] += points
        bloom_scores[skill][bloom_level]["points"] += earned
        bloom_scores[skill][bloom_level]["total"] += points

    total_score = (earned_points / total_points) * 100 if total_points > 0 else 0
    proficiency = {skill: (scores["points"] / scores["total"] * 100) if scores["total"] > 0 else 0 for skill, scores in skill_scores.items()}
    gaps = [skill for skill, score in proficiency.items() if score < 70]

    # Calculate struggle points
    for skill in skills:
        for bloom_level in bloom_scores[skill]:
            total = bloom_scores[skill][bloom_level]["total"]
            if total > 0:
                score = (bloom_scores[skill][bloom_level]["points"] / total) * 100
                if score < 70:
                    struggle_points[skill][bloom_level] = round(score, 1)

    return {"total_score": total_score, "proficiency": proficiency, "gaps": gaps, "struggle_points": struggle_points}