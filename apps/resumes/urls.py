from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('create/', views.resume_create, name='resume_create'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('<int:pk>/edit/', views.resume_update, name='resume_update'),
    path('<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('<int:pk>/duplicate/', views.resume_duplicate, name='resume_duplicate'),
    path('<int:pk>/export/', views.resume_export, name='resume_export'),
    
    # PDF Upload Module
    path('upload/', views.pdf_upload, name='pdf_upload'),
    path('upload/<int:upload_id>/review/', views.pdf_parse_review, name='pdf_parse_review'),
    path('upload/<int:upload_id>/confirm/', views.pdf_import_confirm, name='pdf_import_confirm'),
    
    # Experience management
    path('<int:resume_pk>/experience/add/', views.experience_add, name='experience_add'),
    path('<int:resume_pk>/experience/<int:experience_pk>/edit/', views.experience_edit, name='experience_edit'),
    path('<int:resume_pk>/experience/<int:experience_pk>/delete/', views.experience_delete, name='experience_delete'),
    
    # Education management
    path('<int:resume_pk>/education/add/', views.education_add, name='education_add'),
    path('<int:resume_pk>/education/<int:education_pk>/edit/', views.education_edit, name='education_edit'),
    path('<int:resume_pk>/education/<int:education_pk>/delete/', views.education_delete, name='education_delete'),
    
    # Skill management
    path('<int:resume_pk>/skill/add/', views.skill_add, name='skill_add'),
    path('<int:resume_pk>/skill/<int:skill_pk>/edit/', views.skill_edit, name='skill_edit'),
    path('<int:resume_pk>/skill/<int:skill_pk>/delete/', views.skill_delete, name='skill_delete'),
    
    # Project management
    path('<int:resume_pk>/project/add/', views.project_add, name='project_add'),
    path('<int:resume_pk>/project/<int:project_pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:resume_pk>/project/<int:project_pk>/delete/', views.project_delete, name='project_delete'),
]
