from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


def _rate_limited_login():
    """Wrap Django's LoginView with IP-based rate limiting."""
    try:
        from ratelimit.decorators import ratelimit
        base = auth_views.LoginView.as_view(template_name='authentication/login.html')
        return ratelimit(key='ip', rate='10/m', method='POST', block=True)(base)
    except ImportError:
        return auth_views.LoginView.as_view(template_name='authentication/login.html')


urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('login/', _rate_limited_login(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset.html',
        email_template_name='authentication/password_reset_email.html',
        subject_template_name='authentication/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html',
    ), name='password_reset_complete'),
]
