from django.urls import path

from .views import (
    chatbot,
    DashboardView,
    ResumeUploadView,
    ResumeAnalysisView,
    SkillGapAgentView,
    LearningRoadmapView,
    JobRecommendationView,
    InterviewPreparationView,
)


urlpatterns = [

    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard"
    ),

    path(
        "resume/upload/",
        ResumeUploadView.as_view(),
        name="resume-upload"
    ),

    path(
        "resume/<int:resume_id>/analysis/",
        ResumeAnalysisView.as_view(),
        name="resume-analysis"
    ),

    path(
        "skill-gap/",
        SkillGapAgentView.as_view(),
        name="skill-gap"
    ),

    path(
        "roadmap/",
        LearningRoadmapView.as_view(),
        name="roadmap"
    ),

    path(
        "jobs/",
        JobRecommendationView.as_view(),
        name="job-recommendations"
    ),

    path(
        "interview/",
        InterviewPreparationView.as_view(),
        name="interview-preparation"
    ),

    # VORA AI single chatbot
    path(
        "chatbot/",
        chatbot,
        name="chatbot"
    ),
]