import requests
import json
from src.config.settings import GEMINI_API_KEY
from src.agents.advisor import advisor_agent
import time

def generate_exercises(skill, milestones):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"Generate 3 practical exercises for the skill '{skill}' based on these learning path milestones:\n"
        f"{json.dumps(milestones, indent=2)}\n"
        "For each exercise, provide a description and task in markdown format. "
        "Return as a markdown string."
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
            print(f"Exercises generated for {skill}")
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Gemini error in Assistant (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            time.sleep(5 * (attempt + 1))
    # Fallback with milestone context
    return (
        f"### {skill} Exercises\n"
        f"1. **Explore {skill} Basics**: Learn the core of {milestones[0]['title'] if milestones else skill}.\n"
        f"2. **Apply {skill}**: Tackle a simple task from {milestones[1]['title'] if len(milestones) > 1 else skill}.\n"
        f"3. **Build with {skill}**: Create a small project using {milestones[2]['title'] if len(milestones) > 2 else skill}."
    )

def assistant_agent(skills):
    # Ensure skills is a list
    if not isinstance(skills, list):
        skills = [skills]
    
    # Make sure skills is not empty
    if not skills:
        print("Warning: No skills provided to assistant_agent")
        return {}
        
    print(f"Generating exercises for skills: {', '.join(skills)}")
    
    # Get learning path from advisor
    try:
        learning_path = advisor_agent(skills)
        
        # Verify learning_path is a dictionary
        if not isinstance(learning_path, dict):
            print(f"Warning: advisor_agent returned {type(learning_path)} instead of dict")
            learning_path = {}
            
        exercises = {}
        for skill in skills:
            # Check if milestones exist in the learning path
            milestones = learning_path.get("milestones", [])
            # Filter milestones for this skill (assuming skill appears in titles/descriptions)
            skill_milestones = []
            if milestones and isinstance(milestones, list):
                skill_milestones = [
                    m for m in milestones
                    if isinstance(m, dict) and (
                        skill.lower() in m.get("title", "").lower() or 
                        skill.lower() in m.get("description", "").lower()
                    )
                ]
            exercises[skill] = generate_exercises(skill, skill_milestones or milestones or [])
        return exercises
    except Exception as e:
        print(f"Error in assistant_agent: {e}")
        # Fallback exercise generation
        return {skill: f"### {skill} Exercises\n1. Research {skill} basics\n2. Practice {skill} applications\n3. Create a project using {skill}" for skill in skills}