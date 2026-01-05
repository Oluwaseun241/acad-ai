from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ExamViewSet, SubmissionViewSet
from .auth_views import login

router = DefaultRouter()
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", login, name="api_token_auth"),
]
