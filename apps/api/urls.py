"""
URL routing for the NextGenCV REST API v1.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()
router.register(r'resumes', views.ResumeViewSet, basename='api-resume')
router.register(r'applications', views.JobApplicationViewSet, basename='api-application')

urlpatterns = [
    # JWT Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='api_token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='api_token_verify'),

    # Current user
    path('me/', views.me, name='api_me'),

    # Task status polling
    path('tasks/<str:task_id>/', views.task_status, name='api_task_status'),

    # Outcome analytics
    path('outcomes/', views.outcome_analytics, name='api_outcomes'),

    # Router-generated routes
    path('', include(router.urls)),
]
