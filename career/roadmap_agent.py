import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("VORA_GEMINI_API_KEY")
)


def generate_learning_roadmap(resume_text, target_role):
    prompt = f"""
You are VORA AI Learning Roadmap Agent.

Create a personalized learning roadmap for a student preparing
for the target job role.

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

Provide the result in exactly this structure:

1. Current Skill Level
Briefly describe the candidate's current preparation level.

2. Skills To Learn
List the important skills the candidate should learn or improve.

3. 8-Week Learning Roadmap

Week 1:
- Topics
- What to practice
- Expected outcome

Week 2:
- Topics
- What to practice
- Expected outcome

Week 3:
- Topics
- What to practice
- Expected outcome

Week 4:
- Topics
- What to practice
- Expected outcome

Week 5:
- Topics
- What to practice
- Expected outcome

Week 6:
- Topics
- What to practice
- Expected outcome

Week 7:
- Topics
- What to practice
- Expected outcome

Week 8:
- Topics
- What to practice
- Expected outcome

3. Projects To Build
Suggest 2-3 projects relevant to the target role.

4. Interview Preparation
List the main areas the candidate should prepare for interviews.

5. Final Advice
Give concise practical advice for becoming job-ready.

Keep the roadmap realistic for a student.
"""

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash"
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