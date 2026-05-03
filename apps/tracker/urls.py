from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_list, name='application_list'),
    path('create/', views.application_create, name='application_create'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/edit/', views.application_update, name='application_update'),
    path('<int:pk>/delete/', views.application_delete, name='application_delete'),
    path('<int:pk>/cover-letter/', views.generate_cover_letter, name='generate_cover_letter'),
    path('<int:pk>/interview-prep/', views.interview_prep, name='interview_prep'),
    path('<int:pk>/followup/', views.followup_email, name='followup_email'),
    path('scrape/', views.scrape_job, name='scrape_job'),
    path('outcomes/', views.outcome_dashboard, name='outcome_dashboard'),
    path('skill-gap/', views.skill_gap, name='skill_gap'),
    path('salary/', views.salary_intelligence, name='salary_intelligence'),
    path('rejections/', views.rejection_analysis, name='rejection_analysis'),
]
