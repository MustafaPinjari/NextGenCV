from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Use DashboardView here
    path('resume/', include('resume.urls')),  # Include resume app URLs
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
