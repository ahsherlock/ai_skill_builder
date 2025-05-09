import requests
import json
from src.config.settings import GEMINI_API_KEY
import streamlit as st
import time
import re

def extract_concepts(knowledge_base):
    """Split Knowledge Base into concepts based on headers or paragraphs."""
    # First try to extract headers
    headers = re.findall(r'##\s+(.*?)(?=\n|$)', knowledge_base)
    if headers and len(headers) >= 3:
        return headers
    
    # If no headers found, split by paragraphs
    concepts = re.split(r'###?\s+|\n\n', knowledge_base.strip())
    return [c.strip() for c in concepts if c.strip() and len(c) > 20]

def generate_questions(skills):
    knowledge_base = st.session_state.get("knowledge_base", "No knowledge base available.")
    concepts = extract_concepts(knowledge_base)
    if not concepts:
        concepts = ["General " + ", ".join(skills)]

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        "Using this Knowledge Base:\n"
        f"{knowledge_base}\n\n"
        "Generate a quiz based on these skills: "
        f"{', '.join(skills)}. Create 10-15 unique questions in total. "
        "Mix Multiple Choice (MCQ, 4 options) and True/False (T/F, 2 options) types. "
        "Each question must: "
        "1. Be specific, unique, and based on a concept from the Knowledge Base. "
        "2. Have a Difficulty (Easy/Medium/Hard). "
        "3. Align with Bloom's Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create). "
        "For MCQs, provide 4 detailed options (full sentences): "
        "- a) Completely wrong, b) Mostly wrong, c) Somewhat wrong/somewhat right, d) Correct. "
        "For T/F, provide 2 options: 'True' and 'False', with the question phrased so the answer is clear. "
        "Return as a JSON array of objects with keys: 'question', 'difficulty', 'bloom_level', 'type', 'options', 'answer'. "
        "Example MCQ: {'question': 'What is X?', 'difficulty': 'Easy', 'bloom_level': 'Remember', 'type': 'Multiple Choice', "
        "'options': ['a) Totally wrong thing', 'b) Mostly wrong idea', 'c) Half-right guess', 'd) The right answer'], 'answer': 'd'}."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3000
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
            print(f"Raw Gemini response: {raw_text}")  # Debug
            # Clean up the JSON text
            cleaned_text = raw_text.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json", 1)[1]
            if "```" in cleaned_text:
                cleaned_text = cleaned_text.split("```", 1)[0]
            cleaned_text = cleaned_text.strip()
            
            # Additional JSON cleaning
            # Sometimes the model adds trailing commas which are invalid in JSON
            cleaned_text = re.sub(r',\s*}', '}', cleaned_text)
            cleaned_text = re.sub(r',\s*]', ']', cleaned_text)
            
            try:
                questions = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # Try to fix common JSON errors
                if str(e).startswith("Expecting ',' delimiter"):
                    # Fix missing commas between objects
                    cleaned_text = re.sub(r'}\s*{', '},{', cleaned_text)
                    questions = json.loads(cleaned_text)
                else:
                    raise
            print(f"Parsed questions: {json.dumps(questions, indent=2)}")  # Debug
            # Validate
            if len(questions) < 5:
                raise ValueError(f"Too few questions: {len(questions)}")
            for q in questions:
                if not all(k in q for k in ["question", "difficulty", "bloom_level", "type", "options", "answer"]):
                    raise ValueError(f"Malformed question: {q}")
                if q["type"] == "Multiple Choice" and len(q["options"]) != 4:
                    raise ValueError(f"MCQ needs 4 options, got {len(q['options'])}: {q}")
                if q["type"] == "True/False" and len(q["options"]) != 2:
                    raise ValueError(f"T/F needs 2 options, got {len(q['options'])}: {q}")
            return questions
        except Exception as e:
            print(f"Gemini error (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    # Fallback: Generate simple questions as fallback
    fallback_questions = []
    for i, concept in enumerate(concepts[:5]):
        fallback_questions.extend([
            {
                "question": f"What is a core feature of {concept}?",
                "difficulty": "Easy",
                "bloom_level": "Remember",
                "type": "Multiple Choice",
                "options": [
                    f"a) A completely unrelated feature",
                    f"b) A mostly incorrect feature of {concept}",
                    f"c) A somewhat correct but incomplete feature",
                    f"d) The primary feature of {concept}"
                ],
                "answer": "d"
            },
            {
                "question": f"Does {concept} always require advanced tools?",
                "difficulty": "Medium",
                "bloom_level": "Understand",
                "type": "True/False",
                "options": ["True", "False"],
                "answer": "False"
            },
            {
                "question": f"How would you use {concept} to solve a problem?",
                "difficulty": "Hard",
                "bloom_level": "Apply",
                "type": "Multiple Choice",
                "options": [
                    f"a) A totally wrong approach",
                    f"b) A mostly wrong method for {concept}",
                    f"c) A partially valid but inefficient way",
                    f"d) The optimal use of {concept}"
                ],
                "answer": "d"
            }
        ])
    return fallback_questions[:15]

def quiz_generator_agent(skills):
    questions = generate_questions(skills)
    quiz_content = ""
    for q in questions:
        question = q.get("question", "Unknown question")
        difficulty = q.get("difficulty", "Unknown")
        bloom_level = q.get("bloom_level", "Unknown")
        options = q.get("options", ["a) N/A", "b) N/A", "c) N/A", "d) N/A"])
        options_str = "\n- " + "\n- ".join(options)
        quiz_content += (
            f"**{question}** ({difficulty}, Bloom's {bloom_level})\n"
            f"{options_str}\n\n"
        )
    return {
        "quiz": quiz_content,
        "questions": [
            (
                q.get("question", "Unknown"),
                q.get("difficulty", "Unknown"),
                q.get("bloom_level", "Unknown"),
                q.get("type", "Unknown"),
                None,
                q.get("options", ["a) N/A", "b) N/A", "c) N/A", "d) N/A"]),
                q.get("answer", "a")
            ) for q in questions
        ]
    }
