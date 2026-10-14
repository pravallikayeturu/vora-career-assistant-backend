import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("VORA_GEMINI_API_KEY")
)


def generate_interview_preparation(resume_text, target_role):
    prompt = f"""
You are VORA AI Interview Preparation Agent.

Prepare a personalized interview preparation guide for a student
applying for the target job role.

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

Analyze the resume and generate interview preparation content.

Provide the result in exactly this structure:

1. Technical Interview Questions
Give 10 important technical questions relevant to the target role.
Include a short answer or explanation for each question.

2. Python Questions
Give 8 Python interview questions with concise answers.

3. Django and REST API Questions
Give 8 important Django and REST API interview questions with
concise answers.

4. SQL and Database Questions
Give 8 SQL/database interview questions with concise answers.

5. DSA Questions
Give 8 beginner-to-intermediate DSA questions with a short
explanation of the expected approach.

6. Project-Based Questions
Ask 8 questions based on the candidate's projects and provide
guidance on what a strong answer should include.

7. HR Interview Questions
Give 8 common HR questions with suggested answer points.

8. Mock Interview Preparation
Give a practical checklist for preparing for the interview.

9. Final Advice
Give concise advice for improving interview performance.

Keep the questions suitable for an entry-level candidate and
tailor them to the target role and resume.
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