from django.urls import path
from . import views

urlpatterns = [
    path('<int:resume_id>/analyze/', views.analyze_resume, name='analyze_resume'),
    path('<int:resume_id>/beat-the-ats/', views.beat_the_ats, name='beat_the_ats'),
]
