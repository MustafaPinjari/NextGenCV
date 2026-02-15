from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('trends/', views.analytics_trends, name='analytics_trends'),
    path('improvement-report/', views.improvement_report, name='improvement_report'),
]
