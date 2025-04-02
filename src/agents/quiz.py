import json
import requests
from src.config.settings import GEMINI_API_KEY

def generate_questions(skill, difficulty, api_choice="gemini"):
    if api_choice == "gemini" and GEMINI_API_KEY:
        prompt = f"Generate a {difficulty} quiz question about {skill}. Return in JSON with 'question', 'correct_answer', 'points', and 'difficulty' fields."
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
            response.raise_for_status()
            raw_data = response.json()
            print(f"Gemini Raw: {raw_data}")  # Log to terminal
            result = json.loads(raw_data["candidates"][0]["content"]["parts"][0]["text"])
            print(f"Parsed Result: {result}")  # Log parsed output
            return result
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                "question": f"What is {skill} ({difficulty})?",
                "correct_answer": f"{skill} is a key concept.",
                "points": 10 if difficulty == "Easy" else 15 if difficulty == "Medium" else 25,
                "difficulty": difficulty
            }

def quiz_generator_agent(skills, questions_per_skill=3):
    quiz_content = "Take this SkillBase Quiz to test your knowledge:\n\n"
    questions = []
    difficulties = ["Easy", "Medium", "Hard"]
    for skill in skills:
        for i in range(questions_per_skill):
            difficulty = difficulties[i % len(difficulties)]
            question_data = generate_questions(skill, difficulty, "gemini")
            quiz_content += f"**{question_data['question']}** ({difficulty}, {question_data['points']} points)\n\n"
            questions.append((question_data["question"], skill, question_data["correct_answer"], question_data["points"], difficulty))
    return {"quiz": quiz_content, "questions": questions}