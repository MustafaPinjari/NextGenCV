from django.urls import path
from . import views
from .views_file_access import serve_uploaded_resume, download_uploaded_resume

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('create/', views.resume_create, name='resume_create'),
    path('batch-export/', views.batch_export, name='batch_export'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('<int:pk>/edit/', views.resume_update, name='resume_update'),
    path('<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('<int:pk>/duplicate/', views.resume_duplicate, name='resume_duplicate'),
    path('<int:pk>/export/', views.resume_export, name='resume_export'),
    path('<int:pk>/export/docx/', views.resume_export_docx, name='resume_export_docx'),
    path('<int:pk>/export/text/', views.resume_export_text, name='resume_export_text'),
    
    # PDF Upload Module
    path('upload/', views.pdf_upload, name='pdf_upload'),
    path('upload/<int:upload_id>/review/', views.pdf_parse_review, name='pdf_parse_review'),
    path('upload/<int:upload_id>/confirm/', views.pdf_import_confirm, name='pdf_import_confirm'),
    
    # Secure File Access (with authorization)
    path('upload/<int:upload_id>/file/', serve_uploaded_resume, name='serve_uploaded_resume'),
    path('upload/<int:upload_id>/download/', download_uploaded_resume, name='download_uploaded_resume'),
    
    # Resume Optimization Module
    path('<int:pk>/fix/', views.fix_resume, name='fix_resume'),
    path('<int:pk>/fix/preview/', views.fix_preview, name='fix_preview'),
    path('<int:pk>/fix/accept/', views.fix_accept, name='fix_accept'),
    path('<int:pk>/fix/reject/', views.fix_reject, name='fix_reject'),
    
    # Version Management Module
    path('<int:pk>/versions/', views.version_list, name='version_list'),
    path('<int:pk>/versions/<int:version_id>/', views.version_detail, name='version_detail'),
    path('<int:pk>/versions/compare/', views.version_compare, name='version_compare'),
    path('<int:pk>/versions/<int:version_id>/restore/', views.version_restore, name='version_restore'),
    
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
