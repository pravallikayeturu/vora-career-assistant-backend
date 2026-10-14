import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Resume
from .serializers import ResumeSerializer
from .gemini_service import analyze_resume
from .utils import extract_resume_text
from .skill_gap_agent import analyze_skill_gap
from .roadmap_agent import generate_learning_roadmap
from .job_agent import generate_job_recommendations
from .interview_agent import generate_interview_preparation
from .rag_service import get_resume_context


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("VORA_GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "VORA_GEMINI_API_KEY is missing from the backend .env file."
    )

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.8-flash"


# ==========================================
# CURRENT DATE AND TIME — INDIA
# ==========================================

def get_current_datetime():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    return {
        "date": now.strftime("%d %B %Y"),
        "day": now.strftime("%A"),
        "time": now.strftime("%I:%M:%S %p"),
        "hour": now.hour,
        "timezone": "Asia/Kolkata",
    }


# ==========================================
# HELPER: EXTRACT RESUME TEXT
# ==========================================

def get_resume_text(resume):
    if not resume or not resume.resume_file:
        return ""

    try:
        text = extract_resume_text(resume.resume_file)

        if isinstance(text, str) and text.strip():
            return text.strip()

    except Exception as error:
        print(f"Resume text extraction error: {error}")

    return ""


# ==========================================
# INTERVIEW PREPARATION
# ==========================================

class InterviewPreparationView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        resume_id = request.data.get("resume_id")

        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resume = Resume.objects.get(
                id=resume_id,
                user=request.user
            )

            resume_text = get_resume_text(resume)

            if not resume_text:
                return Response(
                    {"error": "Unable to extract text from this resume."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = generate_interview_preparation(
                resume_text,
                resume.target_role
            )

            return Response({
                "resume_id": resume.id,
                "target_role": resume.target_role,
                "interview_preparation": result
            })

        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            print(f"Interview preparation error: {error}")

            return Response(
                {"error": "Unable to generate interview preparation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# JOB RECOMMENDATIONS
# ==========================================

class JobRecommendationView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        resume_id = request.data.get("resume_id")

        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resume = Resume.objects.get(
                id=resume_id,
                user=request.user
            )

            resume_text = get_resume_text(resume)

            if not resume_text:
                return Response(
                    {"error": "Unable to extract text from this resume."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = generate_job_recommendations(
                resume_text,
                resume.target_role
            )

            return Response({
                "resume_id": resume.id,
                "target_role": resume.target_role,
                "job_recommendations": result
            })

        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            print(f"Job recommendation error: {error}")

            return Response(
                {"error": "Unable to generate job recommendations."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# LEARNING ROADMAP
# ==========================================

class LearningRoadmapView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        resume_id = request.data.get("resume_id")

        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resume = Resume.objects.get(
                id=resume_id,
                user=request.user
            )

            resume_text = get_resume_text(resume)

            if not resume_text:
                return Response(
                    {"error": "Unable to extract text from this resume."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = generate_learning_roadmap(
                resume_text,
                resume.target_role
            )

            return Response({
                "resume_id": resume.id,
                "target_role": resume.target_role,
                "learning_roadmap": result
            })

        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            print(f"Learning roadmap error: {error}")

            return Response(
                {"error": "Unable to generate the learning roadmap."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# SKILL GAP ANALYSIS
# ==========================================

class SkillGapAgentView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        resume_id = request.data.get("resume_id")

        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            resume = Resume.objects.get(
                id=resume_id,
                user=request.user
            )

            resume_text = get_resume_text(resume)

            if not resume_text:
                return Response(
                    {"error": "Unable to extract text from this resume."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = analyze_skill_gap(
                resume_text,
                resume.target_role
            )

            return Response({
                "resume_id": resume.id,
                "target_role": resume.target_role,
                "skill_gap_analysis": result
            })

        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            print(f"Skill gap analysis error: {error}")

            return Response(
                {"error": "Unable to analyze the skill gap."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# RESUME UPLOAD
# ==========================================

class ResumeUploadView(generics.CreateAPIView):

    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ==========================================
# DASHBOARD
# ==========================================

class DashboardView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            "id": user.id,
            "email": user.email,
            "message": "Welcome to VORA AI Career Assistant!"
        })


# ==========================================
# RESUME ANALYSIS
# ==========================================

class ResumeAnalysisView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id):

        try:
            resume = Resume.objects.get(
                id=resume_id,
                user=request.user
            )

            text = get_resume_text(resume)

            if not text:
                return Response(
                    {"error": "Unable to extract text from this resume."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            analysis = analyze_resume(
                text,
                resume.target_role
            )

            return Response({
                "resume_id": resume.id,
                "target_role": resume.target_role,
                "analysis": analysis
            })

        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as error:
            print(f"Resume analysis error: {error}")

            return Response(
                {"error": "Unable to analyze the resume."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==========================================
# VORA AI CHATBOT
# ==========================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chatbot(request):

    question = request.data.get("question", "")

    if not isinstance(question, str):
        return Response(
            {"error": "Question must be text."},
            status=status.HTTP_400_BAD_REQUEST
        )

    question = question.strip()

    if not question:
        return Response(
            {"error": "Question is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    normalized_question = " ".join(question.lower().split())

    # ======================================
    # 1. GREETINGS
    # ======================================

    greeting_words = {
        "hi", "hlo", "hello", "hey", "hii", "hiii",
        "helo", "heelo", "hai", "hiiiii",
        "hello there", "hi there", "hey there",
        "good morning", "good afternoon", "good evening",
    }

    if normalized_question in greeting_words:

        current = get_current_datetime()
        hour = current["hour"]

        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
        elif 17 <= hour < 21:
            greeting = "Good evening"
        else:
            greeting = "Hello"

        return Response(
            {
                "answer": (
                    f"{greeting}! 😊 I'm VORA AI, "
                    "your AI Career Assistant. "
                    "How can I help you today?"
                )
            },
            status=status.HTTP_200_OK
        )

    # ======================================
    # 2. CURRENT DATE, DAY AND TIME
    # ======================================

    date_phrases = [
        "today's date",
        "todays date",
        "current date",
        "what is the date",
        "what's the date",
        "what date is it",
        "date today",
        "today date",
        "today's day",
        "todays day",
        "what day is it",
        "which day is today",
        "what day is today",
        "day today",
        "eroju date enti",
        "eeroju date enti",
        "eroju date anti",
        "eeroju date anti",
        "eroju em date",
        "eeroju em date",
        "eroju em varam",
        "eeroju em varam",
        "ivala em varam",
        "ee roju em varam",
        "today date enti",
        "today em varam",
    ]

    time_phrases = [
        "current time",
        "what time is it",
        "what is the time",
        "what's the time",
        "time right now",
        "time now",
        "present time",
        "ippudu time entha",
        "ippudu time enti",
        "current time enti",
        "time entha",
    ]

    asks_time = any(
        phrase in normalized_question
        for phrase in time_phrases
    )

    asks_date_or_day = any(
        phrase in normalized_question
        for phrase in date_phrases
    )

    if asks_time or asks_date_or_day:

        current = get_current_datetime()

        if asks_time:
            answer = (
                f"The current time is {current['time']} "
                "(India Standard Time)."
            )

        elif any(
            word in normalized_question
            for word in ["varam", "day", "weekday"]
        ):
            answer = (
                f"Today is {current['day']}, "
                f"{current['date']}."
            )

        else:
            answer = (
                f"Today's date is {current['date']} "
                f"({current['day']})."
            )

        return Response(
            {"answer": answer},
            status=status.HTTP_200_OK
        )

    # ======================================
    # 3. GET THE USER'S LATEST RESUME
    # ======================================

    resume_text = ""
    resume_target_role = ""
    resume_id = None

    try:
        resume = (
            Resume.objects
            .filter(user=request.user)
            .order_by("-uploaded_at", "-id")
            .first()
        )

        if resume:
            resume_text = get_resume_text(resume)
            resume_target_role = resume.target_role or ""
            resume_id = resume.id

    except Exception as error:
        print(f"Unable to retrieve user's resume: {error}")

    # ======================================
    # 4. BUILD RAG RESUME CONTEXT
    # ======================================

    resume_context = """
UPLOADED RESUME INFORMATION

No readable resume text is currently available.
Do not invent resume details.
"""

    if resume_text and resume_id:

        try:
            retrieved_context = get_resume_context(
                question=question,
                resume_text=resume_text,
                user_id=request.user.id,
                resume_id=resume_id,
            )

        except Exception as error:
            print(f"RAG retrieval error: {error}")
            retrieved_context = ""

        if retrieved_context:

            resume_context = f"""
UPLOADED RESUME INFORMATION — RETRIEVED USING RAG

Target role: {resume_target_role or "Not specified"}

Relevant resume sections:
{retrieved_context}

RULES:
- Use retrieved resume sections as evidence.
- Do not invent skills, projects, qualifications, or experience.
- If information is missing, clearly state that it was not found.
"""

        else:

            resume_context = f"""
UPLOADED RESUME INFORMATION

Target role: {resume_target_role or "Not specified"}

Extracted resume text:
{resume_text[:18000]}

RULES:
- Base resume-related answers on the provided resume text.
- Do not invent qualifications, experience, or projects.
- Clearly distinguish existing skills from skills to learn.
- If a detail is missing, say it is not specified.
"""

    # ======================================
    # 5. CURRENT DATE AND TIME CONTEXT
    # ======================================

    current = get_current_datetime()

    current_datetime_context = f"""
CURRENT DATE AND TIME

Date: {current["date"]}
Day: {current["day"]}
Time: {current["time"]}
Timezone: {current["timezone"]}

Use this information when answering questions about the current
date, weekday, or time. Do not invent another current date or time.
"""

    # ======================================
    # 6. UNIFIED CAREER ASSISTANT PROMPT
    # ======================================

    prompt = f"""
You are VORA AI, a friendly, intelligent, unified AI Career Assistant.

Your purpose is to help users with career development, programming,
technical learning, resume improvement, and job preparation.

You can assist with:
- Resume analysis
- Skill gap analysis
- Career guidance
- Personalized learning roadmaps
- Job recommendations
- Interview preparation
- Programming languages and technical concepts
- Projects and technologies
- Software development

RESPONSE RULES:

1. Answer the user's exact question directly.
2. Keep simple answers concise, usually 2-4 sentences.
3. Use simple, beginner-friendly English unless another language is requested.
4. Use Markdown headings and bullets when useful.
5. Use code blocks for programming code when necessary.
6. Provide practical and realistic career recommendations.
7. Do not invent resume details.
8. Do not claim to have verified current job openings.
9. Do not ask the user to choose a separate agent.
10. Use resume context when relevant.
11. If the user writes in Telugu or Telugu-English, respond naturally
    in Telugu or Telugu-English.
12. Use the supplied current date and time when relevant.
13. Mention only projects and skills supported by the resume when
    answering questions about the user's resume.
14. Answer general technical questions normally.

{current_datetime_context}

{resume_context}

CURRENT USER QUESTION:
{question}
"""

    # ======================================
    # 7. CALL GEMINI ONCE
    # ======================================

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = getattr(response, "text", None)

        if not answer or not answer.strip():
            return Response(
                {
                    "answer": (
                        "I'm unable to generate a response right now. "
                        "Please try again later. 😊"
                    )
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"answer": answer.strip()},
            status=status.HTTP_200_OK
        )

    except errors.APIError as error:

        error_code = getattr(error, "code", None)
        print(f"Gemini API error: {error}")

        if error_code == 429:
            message = (
                "Your AI request limit has been reached. "
                "Please try again later. 😊"
            )

        elif error_code in (500, 502, 503, 504):
            message = (
                "I'm temporarily unavailable. "
                "Please try again in a few minutes. 😊"
            )

        else:
            message = (
                "I couldn't process your request right now. "
                "Please try again later. 😊"
            )

        return Response(
            {"answer": message},
            status=status.HTTP_200_OK
        )

    except Exception as error:

        print(f"VORA chatbot error: {error}")

        return Response(
            {
                "answer": (
                    "Something went wrong while processing "
                    "your question. Please try again later. 😊"
                )
            },
            status=status.HTTP_200_OK
        )