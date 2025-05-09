import requests
import json
from src.config.settings import GEMINI_API_KEY
import time

def librarian_agent(skills):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Compile a comprehensive list of learning resources for these skills: {', '.join(skills)}. "
        "For each skill, provide the following types of resources:\n"
        "1. Beginner resources (3-4 items)\n"
        "2. Intermediate resources (3-4 items)\n"
        "3. Advanced resources (2-3 items)\n"
        "4. Documentation and references (2-3 items)\n"
        "5. Practice platforms or projects (2-3 items)\n\n"
        "For each resource, include:\n"
        "- Title (descriptive name)\n"
        "- URL (working link)\n"
        "- Description (1-2 sentences about what it covers)\n"
        "- Format (course, book, tutorial, video, documentation, etc.)\n"
        "- Free/Paid status\n"
        "- Estimated time to complete\n\n"
        "Return in clean JSON as a dictionary with skill names as keys and lists of dictionaries as values. "
        "Each dictionary should have these keys: 'title', 'url', 'description', 'format', 'cost', 'time_commitment', 'level'"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}], 
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1,
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
                
            # Extract the JSON text and clean it if needed
            json_text = data["candidates"][0]["content"]["parts"][0]["text"]
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1]
            if json_text.endswith("```"):
                json_text = json_text.split("```")[0]
            
            # Check if JSON is truncated
            if "MAX_TOKENS" in str(response.text):
                try:
                    # Try to fix truncated JSON
                    json_text = json_text + "}"
                except:
                    pass
                
            resources = json.loads(json_text.strip())
            
            # Validate and clean up resources
            if isinstance(resources, dict):
                for skill, resource_list in resources.items():
                    if isinstance(resource_list, list):
                        for i, resource in enumerate(resource_list):
                            # Ensure all required fields exist
                            if not isinstance(resource, dict):
                                resource_list[i] = {
                                    "title": f"{skill} Resource {i+1}",
                                    "url": "https://www.google.com/search?q=" + "+".join(skill.split()),
                                    "description": "A resource for learning this skill",
                                    "format": "Unknown",
                                    "cost": "Unknown",
                                    "time_commitment": "Varies",
                                    "level": "Beginner"
                                }
                                continue
                                
                            for field in ["title", "url", "description", "format", "cost", "time_commitment", "level"]:
                                if field not in resource or not resource[field]:
                                    if field == "title":
                                        resource[field] = f"{skill} Resource {i+1}"
                                    elif field == "url":
                                        resource[field] = "https://www.google.com/search?q=" + "+".join(skill.split())
                                    elif field == "description":
                                        resource[field] = "A resource for learning this skill"
                                    elif field == "format":
                                        resource[field] = "Unknown"
                                    elif field == "cost":
                                        resource[field] = "Unknown"
                                    elif field == "time_commitment":
                                        resource[field] = "Varies"
                                    elif field == "level":
                                        resource[field] = "Beginner"
            
            return resources
                
        except Exception as e:
            print(f"Gemini error in Librarian (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    
    # Fallback with more detailed structure
    fallback_resources = {}
    for skill in skills:
        fallback_resources[skill] = [
            {
                "title": f"{skill} Fundamentals",
                "url": f"https://www.google.com/search?q={skill}+fundamentals+course",
                "description": f"A comprehensive introduction to {skill} covering all the basics.",
                "format": "Online Course",
                "cost": "Free",
                "time_commitment": "4-6 hours",
                "level": "Beginner"
            },
            {
                "title": f"{skill} Documentation",
                "url": f"https://www.google.com/search?q={skill}+official+documentation",
                "description": f"Official documentation for {skill} with complete reference guides.",
                "format": "Documentation",
                "cost": "Free",
                "time_commitment": "Self-paced",
                "level": "All levels"
            },
            {
                "title": f"Advanced {skill} Techniques",
                "url": f"https://www.google.com/search?q=advanced+{skill}+techniques",
                "description": f"For experienced users looking to master advanced concepts in {skill}.",
                "format": "Tutorial",
                "cost": "Free",
                "time_commitment": "10-15 hours",
                "level": "Advanced"
            },
            {
                "title": f"Building Projects with {skill}",
                "url": f"https://www.google.com/search?q=building+projects+with+{skill}",
                "description": f"Learn {skill} by building practical projects from scratch.",
                "format": "Project-based Tutorial",
                "cost": "Free",
                "time_commitment": "15-20 hours",
                "level": "Intermediate"
            },
            {
                "title": f"Interactive {skill} Practice",
                "url": f"https://www.google.com/search?q=interactive+{skill}+practice+exercises",
                "description": f"Hands-on exercises to practice your {skill} skills with immediate feedback.",
                "format": "Interactive Exercises",
                "cost": "Free/Freemium",
                "time_commitment": "Self-paced",
                "level": "Beginner to Intermediate"
            }
        ]
    return fallback_resources