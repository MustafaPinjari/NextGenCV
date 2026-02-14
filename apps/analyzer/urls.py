from django.urls import path
from . import views

urlpatterns = [
    path('<int:resume_id>/analyze/', views.analyze_resume, name='analyze_resume'),
]
