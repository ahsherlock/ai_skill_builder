import json
import re
from src.config.settings import GEMINI_API_KEY
import requests
import time

def generate_subskills(main_skill):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Generate a list of 5-10 key subskills for learning '{main_skill}'. "
        "Return as a JSON array of strings, e.g., ['Variables', 'Loops', 'Classes']."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4000
        }
    }
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned_text = raw_text.strip().strip("```json").strip("```").strip()
            subskills = json.loads(cleaned_text)
            if not isinstance(subskills, list) or not all(isinstance(s, str) for s in subskills):
                raise ValueError("Subskills must be a list of strings")
            print(f"Generated subskills for {main_skill}: {subskills}")
            return subskills
        except Exception as e:
            print(f"Gemini error in Subskills (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    return [f"{main_skill} Basics", f"{main_skill} Intermediate", f"{main_skill} Advanced"]

def map_question_to_subskill(question_text, subskills):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Given these subskills: {json.dumps(subskills)}, "
        f"which subskill best matches this question: '{question_text}'? "
        "Return as a JSON object with a 'subskill' key, e.g., {'subskill': 'Variables'}."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1000,
            "response_mime_type": "application/json"
        }
    }
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"Map subskill raw response: {raw_text}")  # Debug
            
            # Extract only the JSON portion
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, raw_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group(1).strip()
            else:
                # Try to find anything that looks like a JSON object
                json_pattern2 = r'\{\s*"subskill"\s*:\s*"[^"]*"\s*\}'
                json_match2 = re.search(json_pattern2, raw_text)
                if json_match2:
                    cleaned_text = json_match2.group(0)
                else:
                    cleaned_text = raw_text.strip().strip("```json").strip("```").strip()
            
            # Try to parse the JSON
            try:
                result = json.loads(cleaned_text)
                subskill = result.get("subskill")
                if subskill and subskill in subskills:
                    return subskill
                elif subskill and (subskill == "None of the above" or subskill == "Not applicable"):
                    # Default to first subskill if none match
                    return subskills[0]
                elif subskill:
                    # Try a fuzzy match
                    for s in subskills:
                        if s.lower() in subskill.lower() or subskill.lower() in s.lower():
                            return s
                    return subskills[0]
                else:
                    return subskills[0]
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in map_question_to_subskill: {e}, text: {cleaned_text}")
                # Try to extract subskill directly from text
                subskill_pattern = r'"subskill"\s*:\s*"([^"]*)"'
                subskill_match = re.search(subskill_pattern, raw_text)
                if subskill_match:
                    extracted = subskill_match.group(1)
                    for s in subskills:
                        if s.lower() == extracted.lower() or s.lower() in extracted.lower():
                            return s
                return subskills[0]
        except Exception as e:
            print(f"Gemini error in Mapping (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    question_lower = question_text.lower()
    for subskill in subskills:
        if subskill.lower() in question_lower or any(w in question_lower for w in subskill.lower().split()):
            return subskill
    return subskills[0]

def quiz_analyzer_agent(skills, responses, questions):
    main_skill = skills[0]
    subskills = generate_subskills(main_skill)
    
    # Grade questions
    graded_questions = []
    correct_count = 0
    total_questions = len(questions)
    
    for q in questions:
        question_text, difficulty, bloom_level, q_type, _, options, correct_answer = q
        user_answer = responses.get(question_text)
        is_correct = user_answer == correct_answer if user_answer else False
        if is_correct:
            correct_count += 1
        subskill = map_question_to_subskill(question_text, subskills)
        graded_questions.append({
            "question": question_text,
            "user_answer": user_answer or "No answer",
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "options": options,
            "difficulty": difficulty,
            "bloom_level": bloom_level,
            "subskill": subskill
        })

    # Gemini for feedback
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Analyze these quiz responses for '{main_skill}':\n"
        f"{json.dumps(graded_questions, indent=2)}\n\n"
        "For each question where 'is_correct' is False, provide: "
        "1. 'why_wrong': Why the user's answer is wrong (reference 'options' and 'user_answer'). "
        "2. 'why_correct': Why the 'correct_answer' is correct (tie to 'question' and 'subskill'). "
        "Return as a JSON object with a 'feedback' key mapping question text to objects with 'why_wrong' and 'why_correct', "
        "e.g., {'feedback': {'Q1': {'why_wrong': '...', 'why_correct': '...'}}}."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4000,
            "response_mime_type": "application/json"
        }
    }
    feedback = {"feedback": {}}
    for attempt in range(3):
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "candidates" not in data:
                raise ValueError("No 'candidates' in response")
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"Raw feedback response: {raw_text}")  # Debug
            
            # Extract only the JSON portion
            json_pattern = r'```json\s*(.*?)\s*```'
            json_match = re.search(json_pattern, raw_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group(1).strip()
            else:
                # Try to find the JSON object directly
                if raw_text.startswith("{") and "}" in raw_text:
                    cleaned_text = raw_text.split("}", 1)[0] + "}"
                else:
                    cleaned_text = raw_text.strip().strip("```json").strip("```").strip()
            
            # Fix common JSON issues
            cleaned_text = re.sub(r',\s*}', '}', cleaned_text)
            cleaned_text = re.sub(r',\s*]', ']', cleaned_text)
            
            try:
                feedback = json.loads(cleaned_text)
                # Validate feedback structure
                if not isinstance(feedback.get("feedback", {}), dict):
                    raise ValueError("Feedback must be a dict")
                for q, fb in feedback["feedback"].items():
                    if not all(k in fb for k in ["why_wrong", "why_correct"]):
                        raise ValueError(f"Feedback for '{q}' missing 'why_wrong' or 'why_correct'")
                break
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                if attempt == 2:  # Last attempt, create simple feedback
                    feedback = {"feedback": {}}
                    for q in graded_questions:
                        if not q["is_correct"]:
                            feedback["feedback"][q["question"]] = {
                                "why_wrong": f"Your answer '{q['user_answer']}' doesn't match the expected answer.",
                                "why_correct": f"The correct answer is '{q['correct_answer']}' which aligns with {q['subskill']}."
                            }
                    break
                time.sleep(5)
        except Exception as e:
            print(f"Gemini error in Analyzer (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    
    # Fallback: ensure every wrong answer has feedback
    for q in graded_questions:
        if not q["is_correct"] and q["question"] not in feedback["feedback"]:
            feedback["feedback"][q["question"]] = {
                "why_wrong": f"'{q['user_answer']}' doesn’t align with {q['subskill']} concepts.",
                "why_correct": f"'{q['correct_answer']}' is the right fit for {q['subskill']} in this case."
            }

    # Analyze subskills
    proficiency = {subskill: {"correct": 0, "total": 0} for subskill in subskills}
    struggle_points = {subskill: 0 for subskill in subskills}
    
    for q in graded_questions:
        subskill = q["subskill"]
        proficiency[subskill]["total"] += 1
        if q["is_correct"]:
            proficiency[subskill]["correct"] += 1

    for subskill in proficiency:
        correct = proficiency[subskill]["correct"]
        total = proficiency[subskill]["total"]
        score = (correct / total * 100) if total > 0 else 0
        proficiency[subskill] = score
        struggle_points[subskill] = score
    
    gaps = [subskill for subskill, score in proficiency.items() if score < 60]

    return {
        "total_score": correct_count / total_questions * 100,
        "graded_questions": graded_questions,
        "feedback": feedback["feedback"],
        "proficiency": proficiency,
        "struggle_points": {s: score for s, score in struggle_points.items() if score < 60},
        "gaps": gaps
    }