# resume/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_resume_view, name='create_resume'),           
]
