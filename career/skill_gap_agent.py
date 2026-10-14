import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("VORA_GEMINI_API_KEY")
)


def analyze_skill_gap(resume_text, target_role):
    prompt = f"""
You are VORA AI Skill Gap Agent.

Analyze the candidate's resume for the target job role.

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

Provide the result in the following format:

1. Existing Skills
List the skills already present in the resume.

2. Required Skills
List the important skills normally required for the target role.

3. Missing Skills
Identify skills that appear to be missing from the resume.

4. Priority Skills
Identify the most important missing skills the candidate should learn first.

5. Learning Recommendations
Give a short recommendation for each priority skill.

Keep the response practical and suitable for a student preparing for a job.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text