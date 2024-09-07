from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_resume_view, name='create_resume'),
    path('templates/', views.resume_templates, name='resume_templates'),
    # path('editor/<str:template_name>/', views.editor_template, name='editor_template'),
]
