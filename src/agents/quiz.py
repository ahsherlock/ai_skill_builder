import requests
import json
from src.config.settings import GEMINI_API_KEY
import random
import time

def generate_questions(skill, difficulty, bloom_level, question_type="mcq", used_questions=None):
    if used_questions is None:
        used_questions = set()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    bloom_prompts = {
        "Remembering": f"Recall a basic fact about {skill}",
        "Understanding": f"Explain a concept of {skill}",
        "Applying": f"Use {skill} in a simple scenario",
        "Analyzing": f"Break down a part of {skill}",
        "Evaluating": f"Judge an aspect of {skill}",
        "Creating": f"Design something using {skill}"
    }
    if question_type == "tf":
        prompt = (
            f"Generate a unique {difficulty} True/False question for {skill} at Bloom's {bloom_level} level: {bloom_prompts[bloom_level]}. "
            f"Different from these: {', '.join(used_questions)}. "
            "Return in JSON with 'question', 'options' (['True', 'False']), 'correct_answer' (True or False), "
            "'points' (1 for Easy, 3 for Medium, 5 for Hard), 'difficulty', and 'bloom_level'."
        )
    else:
        options_count = 6 if difficulty == "Hard" else 3
        prompt = (
            f"Generate a unique {difficulty} multiple-choice question for {skill} at Bloom's {bloom_level} level: {bloom_prompts[bloom_level]}. "
            f"Different from these: {', '.join(used_questions)}. "
            f"Return in JSON with 'question', 'options' (list of {options_count}: "
            f"{'completely wrong, mostly wrong, kind of wrong, sort of correct, mostly correct, absolutely correct' if difficulty == 'Hard' else 'completely wrong, kind of wrong, correct'}), "
            "'correct_answer' (the correct option text), 'points' (1 for Easy, 3 for Medium, 5 for Hard), 'difficulty', and 'bloom_level'."
        )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=30)  # Up to 30s
            response.raise_for_status()
            result = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
            print(f"Quiz question generated for {skill} ({difficulty}, {bloom_level}): {result['question']}")
            return {
                "question": result.get("question", f"What is {skill}?"),
                "options": result.get("options", ["True", "False"] if question_type == "tf" else ["A", "B", "C"]),
                "correct_answer": result.get("correct_answer", "True" if question_type == "tf" else "C"),
                "points": result.get("points", 1 if difficulty == "Easy" else 3 if difficulty == "Medium" else 5),
                "difficulty": result.get("difficulty", difficulty),
                "bloom_level": result.get("bloom_level", bloom_level)
            }
        except Exception as e:
            print(f"Gemini error in Quiz (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))  # 5s, 10s
            else:
                # Fallback
                if question_type == "tf":
                    fallback_q = random.choice([
                        f"Is {skill} a core part of {bloom_level.lower()}? ({difficulty})",
                        f"Does {skill} support {bloom_level.lower()} tasks? ({difficulty})",
                        f"Is {skill} linked to {bloom_level.lower()} skills? ({difficulty})"
                    ])
                    while fallback_q in used_questions:
                        fallback_q = f"Does {skill} tie into {bloom_level.lower()}? ({difficulty})"
                    return {
                        "question": fallback_q,
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "points": 1 if difficulty == "Easy" else 3 if difficulty == "Medium" else 5,
                        "difficulty": difficulty,
                        "bloom_level": bloom_level
                    }
                else:
                    options = (
                        ["Unrelated", "Partially related", "Essential"] if difficulty != "Hard" else
                        ["Totally off", "Mostly off", "Slightly off", "Somewhat true", "Largely true", "Spot on"]
                    )
                    fallback_q = random.choice([
                        f"What’s a {bloom_level.lower()} use of {skill}? ({difficulty})",
                        f"How does {skill} aid {bloom_level.lower()}? ({difficulty})",
                        f"Why is {skill} key to {bloom_level.lower()}? ({difficulty})"
                    ])
                    while fallback_q in used_questions:
                        fallback_q = f"How’s {skill} used in {bloom_level.lower()}? ({difficulty})"
                    return {
                        "question": fallback_q,
                        "options": options,
                        "correct_answer": options[-1],
                        "points": 1 if difficulty == "Easy" else 3 if difficulty == "Medium" else 5,
                        "difficulty": difficulty,
                        "bloom_level": bloom_level
                    }

def quiz_generator_agent(skills, questions_per_skill=20):
    quiz_content = "Take this SkillBase Quiz to test your knowledge (select one option per question):\n\n"
    questions = []
    bloom_difficulty_map = {
        "Easy": ["Remembering", "Understanding"],
        "Medium": ["Applying", "Analyzing"],
        "Hard": ["Evaluating", "Creating"]
    }
    difficulties = ["Easy"] * 8 + ["Medium"] * 8 + ["Hard"] * 4
    used_questions = set()
    return {"quiz": quiz_content, "questions": questions, "generator": question_generator(skills, difficulties, bloom_difficulty_map, used_questions, questions_per_skill)}

def question_generator(skills, difficulties, bloom_difficulty_map, used_questions, questions_per_skill):
    for skill in skills:
        random.shuffle(difficulties)
        for i, difficulty in enumerate(difficulties[:questions_per_skill]):
            bloom_level = random.choice(bloom_difficulty_map[difficulty])
            q_type = "tf" if (difficulty == "Easy" and random.random() < 0.7) or (difficulty == "Medium" and random.random() < 0.4) else "mcq"
            yield skill, difficulty, bloom_level, q_type, used_questions
