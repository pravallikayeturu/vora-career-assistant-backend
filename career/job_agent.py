import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("VORA_GEMINI_API_KEY")
)


def generate_job_recommendations(resume_text, target_role):
    prompt = f"""
You are VORA AI Job Recommendation Agent.

Analyze the candidate's resume and target role.

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

Recommend suitable entry-level job roles for this candidate.

Provide the result in exactly this structure:

1. Recommended Job Roles

For each role provide:
- Job Role
- Why It Matches
- Important Skills
- Preparation Needed

Recommend 5 suitable roles.

2. Role-Specific Skill Focus
List the most important skills the candidate should focus on
for the recommended roles.

3. Job Search Keywords
Give useful keywords the candidate can use when searching
for jobs on LinkedIn, Naukri, Indeed, and company career pages.

4. Application Advice
Give practical advice for applying to these roles as a student
or recent graduate.

Do not claim that any specific job opening currently exists.
Focus on suitable job roles based on the resume.
"""

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash"
    ]

    last_error = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text

        except Exception as e:
            last_error = e
            print(f"Model {model} failed: {e}")

    raise last_error