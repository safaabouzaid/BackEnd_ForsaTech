import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash")

def get_inferred_skills(skill_name):
    #Instructional Prompt
    prompt = f"""
    The user has listed the skill: "{skill_name}". Based on this specific skill **only**, suggest a few closely related technical programming skills that are **commonly acquired together** and are reasonably inferred, **without exaggeration**. 
    Limit the output to a **realistic** JSON list of 2 to 5 skill names only.
    Respond with JSON list only.
    """
    
    response = model.generate_content([prompt])
    content = response.text.strip()

    print(f"Raw response from Gemini:\n{content}")

    # clear Markdown 
    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()
    elif content.startswith("```"):
        content = content.replace("```", "").strip()

    print(f" Cleaned response:\n{content}")

    try:
        return json.loads(content)
    except Exception as e:
        print(f" Gemini error during JSON parsing: {e}")
        return []
