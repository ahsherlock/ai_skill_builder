import requests
import json
from src.config.settings import GEMINI_API_KEY
import time
import re

def advisor_agent(skills):
    # Ensure skills is a list and not empty
    if not skills:
        print("Warning: No skills provided to advisor_agent")
        skills = ["general learning"]

    # Convert to list if it's not already
    if not isinstance(skills, list):
        skills = [skills]

    print(f"Generating learning path for skills: {', '.join(skills)}")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    prompt = (
        f"You are an expert educator who creates comprehensive learning guides. Create a detailed guide for learning this skill or list of skills: {', '.join(skills)}. "
        "Your guide should include: "
        "1. A detailed introduction to the skill and its importance (3-5 sentences) "
        "2. A breakdown of the skill into 3 - 10 sub-skills or components "
        "3. A detailed learning path from beginner to advanced (7 levels max) "
        "4. 4-5 resources for each stage "
        "5. 4-5 common challenges and how to overcome them "
        "6. 4-5 practice exercises "
        "7. 4-5 metrics to track progress "
        "8. Estimated time commitment (one brief sentence) "
        "Format the guide in a clear, structured way with headings and bullet points where appropriate. "
        "Return in valid JSON with the following structure: "
        "{\"introduction\": string, \"skill_components\": [string], \"learning_path\": [{\"level\": string, \"description\": string, \"resources\": [string]}], "
        "\"challenges\": [{\"challenge\": string, \"solution\": string}], \"practice_exercises\": [string], "
        "\"progress_metrics\": [string], \"time_commitment\": string, \"milestones\": [{\"title\": string, \"description\": string}]}"
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

            json_text = data["candidates"][0]["content"]["parts"][0]["text"]

            # Remove any markdown formatting that might interfere with JSON parsing
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1]
            if json_text.endswith("```"):
                json_text = json_text.split("```")[0]

            # Fix JSON syntax errors and missing brackets
            print("Checking and fixing JSON structure...")
            
            # Look for specific pattern issues - like missing closing bracket for dictionary in array
            json_text = re.sub(r'\{([^{}]*)\},\s*\{([^{}]*)\{', r'{\1}, {\2},\n{', json_text)
            
            # Try to find and fix unclosed objects in arrays
            json_text = re.sub(r'(\{[^{}]*)\},\s*(\{[^{}]*)\},\s*\{([^{},]*)("|\')\s*:\s*("|\')()', r'\1}, \2}, {\3\4: \5}', json_text)
            
            # Fix trailing commas before closing brackets/braces
            json_text = re.sub(r',(\s*[\]}])', r'\1', json_text)
            
            # Check for balanced braces and brackets
            open_braces = json_text.count('{')
            close_braces = json_text.count('}')
            open_brackets = json_text.count('[')
            close_brackets = json_text.count(']')
            
            # Fix unmatched braces or brackets
            if (open_braces != close_braces) or (open_brackets != close_brackets):
                print(f"Imbalanced JSON: {open_braces}/{close_braces} braces, {open_brackets}/{close_brackets} brackets")
                
                # Track structure to determine missing brackets more accurately
                stack = []
                expected_closers = {'{': '}', '[': ']'}
                
                # Scan through string to find where things went wrong
                for i, char in enumerate(json_text):
                    if char in '{[':
                        stack.append(char)
                    elif char in ']}':
                        if not stack or expected_closers[stack.pop()] != char:
                            # Found a mismatch or unexpected closer
                            print(f"JSON syntax error at position {i}: unexpected '{char}'")
                
                # Add missing closing characters in the right order
                while stack:
                    char = stack.pop()
                    if char == '{':
                        json_text += '}'
                    elif char == '[':
                        json_text += ']'

            try:
                # Try to parse the fixed JSON
                learning_path = json.loads(json_text.strip())
            except json.JSONDecodeError as e:
                print(f"Still having JSON issues: {e}")
                # Try more aggressive fixes if specific errors are found
                error_msg = str(e)
                
                if "Expecting property name enclosed in double quotes" in error_msg:
                    # Fix missing quotes around property names
                    match = re.search(r'line\s+\d+\s+column\s+(\d+)', error_msg)
                    if match:
                        pos = int(match.group(1)) - 1
                        # Find the problematic spot and try to fix it
                        if pos < len(json_text):
                            before = json_text[:pos]
                            after = json_text[pos:]
                            if re.search(r'[{,]\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', after):
                                # Add quotes around property name
                                fixed = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', after)
                                json_text = before + fixed
                
                # Try a simple fallback fix for missing closing brackets in arrays
                if "learning_path" in json_text and "level" in json_text:
                    # Look for learning_path array specifically
                    path_start = json_text.find('"learning_path"')
                    if path_start > 0:
                        path_bracket = json_text.find('[', path_start)
                        if path_bracket > 0:
                            # Count braces in learning_path array
                            path_text = json_text[path_bracket:]
                            open_braces = 0
                            for i, char in enumerate(path_text):
                                if char == '{':
                                    open_braces += 1
                                elif char == '}':
                                    open_braces -= 1
                                # Fix missing brace after a level entry
                                if open_braces > 0 and char == ',' and '"level"' in path_text[max(0, i-50):i]:
                                    # Find the location of the comma after "resources"
                                    resources_end = path_text.rfind('"]', 0, i)
                                    if resources_end > 0 and path_text[resources_end:i].count('}') == 0:
                                        # Add missing closing brace
                                        path_text = path_text[:resources_end+2] + '}' + path_text[resources_end+2:]
                            
                            json_text = json_text[:path_bracket] + path_text
                
                # Final attempt to parse after fixes
                learning_path = json.loads(json_text.strip())

            # Ensure required keys exist
            if "milestones" not in learning_path:
                learning_path["milestones"] = [
                    {"title": f"Understand {skill} fundamentals", "description": f"Learn the basic concepts of {skill}"}
                    for skill in skills
                ]

            return learning_path
        except Exception as e:
            print(f"Gemini error in Advisor (attempt {attempt + 1}): {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            
            # Extract raw JSON for manual fixing if possible
            if 'response' in locals() and hasattr(response, 'text'):
                try:
                    # Get the raw text and try custom parsing fixes
                    data = response.json()
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"Attempting manual JSON recovery with {len(raw_json)} characters of text")
                    
                    # Common pattern fixes for dog walking example
                    if "dog walking" in raw_json.lower() or "leash" in raw_json.lower():
                        # Fix specific issue in learning_path array with missing closing braces
                        learning_path_pattern = r'"learning_path":\s*\[\s*\{.*?"Intermediate".*?resources.*?\]'
                        if re.search(learning_path_pattern, raw_json, re.DOTALL):
                            raw_json = re.sub(r'(\{.*?"Intermediate".*?"resources":\s*\[[^\]]*\])(,\s*\{)', r'\1}\2', raw_json, flags=re.DOTALL)
                    
                    # Try fixing brackets with a simpler approach
                    if "Expecting property name" in str(e) or "Expecting ',' delimiter" in str(e):
                        # Look for missing closing braces after resources arrays
                        raw_json = re.sub(r'"resources":\s*\[[^\]]*\](?!\s*})(?=\s*,\s*\{)', r'"resources": []\1}', raw_json)
                    
                    # Add missing closing braces/brackets and try again
                    open_braces = raw_json.count('{')
                    close_braces = raw_json.count('}')
                    open_brackets = raw_json.count('[')
                    close_brackets = raw_json.count(']')
                    
                    # Make sure we have balanced JSON before returning
                    if open_braces > close_braces:
                        raw_json += '}' * (open_braces - close_braces)
                    if open_brackets > close_brackets:
                        raw_json += ']' * (open_brackets - close_brackets)
                    
                    # Try to parse the fixed JSON
                    learning_path = json.loads(raw_json)
                    print("Successfully recovered JSON from error state")
                    return learning_path
                except Exception as recovery_error:
                    print(f"JSON recovery failed: {recovery_error}")
            
            time.sleep(5 * (attempt + 1))

    # Fallback with more detailed structure
    fallback = {
        "introduction": f"Learn {', '.join(skills)} to boost your career and problem-solving abilities!",
        "skill_components": [f"Core {skill} concepts" for skill in skills],
        "learning_path": [
            {"level": "Beginner", "description": f"Learn the fundamentals of {', '.join(skills)}", "resources": ["Online tutorials"]},
            {"level": "Intermediate", "description": f"Build projects with {', '.join(skills)}", "resources": ["Practice websites"]},
            {"level": "Advanced", "description": f"Master advanced {', '.join(skills)} concepts", "resources": ["Advanced courses"]}
        ],
        "challenges": [{"challenge": "Learning curve", "solution": "Consistent practice"}],
        "practice_exercises": [f"Build a simple {skill} project" for skill in skills],
        "progress_metrics": ["Completion of projects", "Ability to solve problems independently"],
        "time_commitment": "3-6 months depending on prior experience",
        "milestones": [
            {"title": f"Understand {skill} fundamentals", "description": f"Learn the basic concepts of {skill}"}
            for skill in skills
        ] + [
            {"title": f"Apply {skills[0]} in projects", "description": f"Build simple applications using {skills[0]}"},
            {"title": f"Master advanced {skills[0]} techniques", "description": f"Learn complex patterns and best practices"}
        ]
    }
    print("Using fallback learning path due to API errors")
    return fallback
