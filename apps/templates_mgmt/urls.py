"""
URL Configuration for Template Management
"""
from django.urls import path
from apps.templates_mgmt import views

urlpatterns = [
    # Template Gallery
    path('gallery/', views.template_gallery, name='template_gallery'),
    
    # Template Preview
    path('preview/<int:template_id>/', views.template_preview, name='template_preview'),
    
    # Template Selection
    path('select/<int:template_id>/<int:resume_id>/', views.template_select, name='template_select'),
    
    # Template Customization
    path('customize/<int:resume_id>/', views.template_customize, name='template_customize'),
    path('customize/<int:resume_id>/preview/', views.template_customize_preview, name='template_customize_preview'),
]
