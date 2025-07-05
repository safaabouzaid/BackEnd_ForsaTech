import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import json

from google.api_core import exceptions
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(7),         
    retry=retry_if_exception_type(exceptions.ResourceExhausted)
)
def get_inferred_skills(skill_name):
    # Instructional Prompt 
    prompt = f"""
    The user has listed the skill: "{skill_name}". Based on this specific skill **only**, suggest a few closely related technical programming skills that are **commonly acquired together** and are reasonably inferred, **without exaggeration**.
    Limit the output to a **realistic** JSON list of 2 to 5 skill names only.
    Respond with JSON list only.
    """

    try:
        response = model.generate_content([prompt])
        content = response.text.strip()

        print(f"Raw response from Gemini:\n{content}")


        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        print(f" Cleaned response:\n{content}")


        return json.loads(content)
    except json.JSONDecodeError as e:


        print(f" Gemini error during JSON parsing for skill '{skill_name}': {e}. Raw response: '{content}'")
        return []
    except Exception as e:

        print(f" An unexpected error occurred for skill '{skill_name}': {e}")
        return []