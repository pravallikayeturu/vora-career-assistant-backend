from django.urls import path

from .views import (
    SignupView,
    LoginView,
    MeView,
    RefreshTokenView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
]