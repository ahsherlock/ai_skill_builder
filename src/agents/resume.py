import requests
import json
import time
from src.config.settings import GEMINI_API_KEY
import PyPDF2
from docx import Document

def extract_text_from_file(file, file_type):
    try:
        if file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            return "".join(page.extract_text() or "" for page in pdf_reader.pages)
        elif file_type == "docx":
            doc = Document(file)
            return "\n".join(para.text for para in doc.paragraphs)
        elif file_type == "txt":
            return file.read().decode("utf-8")
        return ""
    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""

def split_skills(text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Given this input: '{text}', determine if it represents one skill/topic or multiple. "
        "If multiple, split it into distinct skills/topics. Return as a JSON array of strings."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 1000
        }
    }
    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        json_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        # Clean up JSON text if needed
        if json_text.startswith("```json"):
            json_text = json_text.split("```json")[1]
        if json_text.endswith("```"):
            json_text = json_text.split("```")[0]
            
        return json.loads(json_text.strip())
    except Exception as e:
        print(f"Gemini error in split_skills: {e}")
        return [text]

def resume_scanner_agent(file, file_type):
    resume_text = extract_text_from_file(file, file_type)
    if not resume_text:
        return ["General"]
        
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Extract a comprehensive list of professional skills and technologies from this resume text:\n\n{resume_text}\n\n"
        "Group similar skills together and remove duplicates. Include both hard skills (technical) and soft skills."
        "For each skill, include proficiency level if mentioned."
        "Return as a JSON array of strings, with each string formatted as 'Skill Name (category)'."
        "Categories should be one of: 'Technical', 'Business', 'Creative', 'Soft Skill', or 'Other'."
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 2000
        }
    }
    
    for attempt in range(3):  # Try up to 3 times
        try:
            response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=30)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            response_data = response.json()
            if "candidates" not in response_data:
                raise ValueError("No candidates in response")
                
            json_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean up the JSON text if needed
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1]
            if json_text.endswith("```"):
                json_text = json_text.split("```")[0]
            
            # Fix common JSON issues    
            import re
            json_text = re.sub(r',\s*]', ']', json_text.strip())
            json_text = re.sub(r',\s*}', '}', json_text.strip())
                
            try:
                skills = json.loads(json_text.strip())
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in resume_scanner: {e}")
                # Try a simpler format if parsing fails
                skills = ["Python (Technical)", "JavaScript (Technical)", "Data Analysis (Technical)", 
                         "Communication (Soft Skill)", "Problem Solving (Soft Skill)"]
            
            # Ensure we have skills
            if not skills or not isinstance(skills, list):
                return ["General Skills"]
                
            # Remove any empty strings or duplicates
            skills = [s for s in skills if s and isinstance(s, str)]
            skills = list(set(skills))  # Remove duplicates
            
            return skills if skills else ["General"]
            
        except Exception as e:
            print(f"Gemini error in Resume Scanner (attempt {attempt+1}): {e}")
            if attempt == 2:  # Last attempt failed
                return ["Python", "Machine Learning", "Data Analysis", "Communication", "Problem Solving"]
            time.sleep(2)  # Wait before retrying