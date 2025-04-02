import requests
import json
from src.config.settings import XAI_API_KEY, XAI_API_ENDPOINT

def quiz_generator_agent(skills, questions_per_skill=3):
    def generate_questions(skill, difficulty):
        prompt = f"Generate a {difficulty} quiz question about {skill}. Return in JSON format with 'question', 'correct_answer', 'points', and 'difficulty' fields."
        headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "max_tokens": 150, "temperature": 0.7}
        try:
            response = requests.post(XAI_API_ENDPOINT, headers=headers, json=payload)
            question_data = json.loads(response.json()["choices"][0]["text"].strip())
            return question_data
        except Exception:
            return {
                "question": f"What is {skill} ({difficulty})?",
                "correct_answer": f"{skill} is a key concept.",
                "points": 10 if difficulty == "Easy" else 15 if difficulty == "Medium" else 25,
                "difficulty": difficulty
            }

    quiz_content = f"Quiz on {', '.join(skills)}\n"
    selected_questions = []
    question_index = 1

    for skill in skills:
        for difficulty in ["Easy", "Medium", "Hard"]:
            if len([q for q in selected_questions if q[1] == skill]) < questions_per_skill:
                question_data = generate_questions(skill, difficulty)
                quiz_content += f"{question_index}. [{difficulty}] {question_data['question']}\n"
                selected_questions.append((
                    question_data["question"],
                    skill,
                    question_data["correct_answer"],
                    question_data["points"],
                    question_data["difficulty"]
                ))
                question_index += 1

    return {"quiz": quiz_content, "questions": selected_questions}