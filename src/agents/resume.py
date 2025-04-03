import requests
import json
from src.config.settings import GEMINI_API_KEY
import PyPDF2
from docx import Document

def extract_text_from_file(file, file_type):
    if file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif file_type == "docx":
        doc = Document(file)
        return "\n".join(para.text for para in doc.paragraphs)
    elif file_type == "txt":
        return file.read().decode("utf-8")
    return ""

def split_skills(text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = (
        f"Given this input: '{text}', determine if it represents one skill/topic or multiple. "
        "If multiple, split it into distinct skills/topics. Return as a JSON array of strings."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=10)
        return json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e:
        print(f"Gemini error in split_skills: {e}")
        return [text]

def resume_scanner_agent(file, file_type):
    resume_text = extract_text_from_file(file, file_type)
    if not resume_text:
        return ["General"]
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = (
        f"Extract a list of skills and topics from this resume text:\n\n{resume_text}\n\n"
        "Return as a JSON array of strings."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=10)
        skills = json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
        return skills if skills else ["General"]
    except Exception as e:
        print(f"Gemini error in Resume Scanner: {e}")
        return ["Python", "Machine Learning", "Data Analysis"]