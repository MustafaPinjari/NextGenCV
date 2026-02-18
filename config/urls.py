"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from config.help_views import documentation
from config.performance_views import collect_metrics, performance_dashboard, performance_summary

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing_new.html'), name='landing'),
    path('help/', documentation, name='help_documentation'),
    path('auth/', include('apps.authentication.urls')),
    path('resumes/', include('apps.resumes.urls')),
    path('analyzer/', include('apps.analyzer.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('templates/', include('apps.templates_mgmt.urls')),
    
    # Design system test page (development only)
    path('design-system-test/', TemplateView.as_view(template_name='design-system-test.html'), name='design_system_test'),
    
    # Performance monitoring endpoints (Requirements: 14.6)
    path('api/performance/metrics/', collect_metrics, name='performance_metrics'),
    path('api/performance/summary/', performance_summary, name='performance_summary'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add performance monitoring dashboard in development (Requirements: 14.6)
    urlpatterns += [path('performance/dashboard/', performance_dashboard, name='performance_dashboard')]

# Custom error handlers
handler404 = 'config.views.custom_404'
handler403 = 'config.views.custom_403'
handler500 = 'config.views.custom_500'

