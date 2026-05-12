# NextGenCV — SSO (Google & LinkedIn) + Email System Setup Guide

This guide walks through every step needed to add Google SSO, LinkedIn SSO, and a working email system to the existing NextGenCV Django project. Every code block is copy-paste ready and maps directly to the existing file structure.

---

## Table of Contents

1. [Overview of What We Are Adding](#1-overview)
2. [Install Required Packages](#2-install-required-packages)
3. [Part A — Email System (SMTP)](#3-part-a--email-system-smtp)
   - 3.1 Gmail Setup
   - 3.2 Settings Configuration
   - 3.3 Update `.env`
   - 3.4 Update Email Tasks
   - 3.5 Test Email Works
4. [Part B — Google SSO](#4-part-b--google-sso)
   - 4.1 Create Google OAuth Credentials
   - 4.2 Install & Configure django-allauth
   - 4.3 Settings Changes
   - 4.4 URL Changes
   - 4.5 Database Migration
   - 4.6 Django Admin Setup
   - 4.7 Login Template Button
5. [Part C — LinkedIn SSO](#5-part-c--linkedin-sso)
   - 5.1 Create LinkedIn OAuth App
   - 5.2 Configure Provider
   - 5.3 Django Admin Setup
   - 5.4 Login Template Button
6. [Part D — Post-Login Signal (Auto-create Profile)](#6-part-d--post-login-signal)
7. [Part E — Updated `.env.example`](#7-part-e--updated-envexample)
8. [Part F — Full Updated `settings.py` Block](#8-part-f--full-updated-settingspy-block)
9. [Part G — Full Updated `urls.py`](#9-part-g--full-updated-urlspy)
10. [Testing Checklist](#10-testing-checklist)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Overview

| Feature | Library | What it does |
|---|---|---|
| Google SSO | `django-allauth` | OAuth2 login via Google account |
| LinkedIn SSO | `django-allauth` | OAuth2 login via LinkedIn account |
| Email (SMTP) | Django built-in | Real email delivery via Gmail/SendGrid/Mailgun |
| Email (Dev) | Django console backend | Prints emails to terminal — no SMTP needed |

`django-allauth` handles the full OAuth2 flow for both Google and LinkedIn. It creates a Django `User` automatically on first login, links social accounts to existing users by email, and integrates cleanly with Django's session auth system that NextGenCV already uses.

---

## 2. Install Required Packages

```bash
pip install django-allauth==0.61.1
```

Add to `requirements.txt`:

```
django-allauth==0.61.1
```

> `django-allauth` covers both Google and LinkedIn — no separate packages needed.

---

## 3. Part A — Email System (SMTP)

The project currently uses `console` email backend (prints to terminal). This section switches it to real SMTP delivery.

### 3.1 Gmail App Password Setup

Gmail requires an **App Password** — not your regular Gmail password.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required for App Passwords)
3. Go to **Security → App passwords**
4. Select app: **Mail** | Select device: **Other (custom name)** → type `NextGenCV`
5. Click **Generate** — copy the 16-character password shown
6. Store it as `EMAIL_HOST_PASSWORD` in your `.env`

> If you prefer not to use Gmail, see the SendGrid and Mailgun alternatives at the end of this section.

### 3.2 Settings Configuration

Open `config/settings.py`. Find the existing email block:

```python
# Email backend (console for dev — swap to SMTP in production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'NextGenCV <noreply@nextgencv.com>'
```

**Replace it entirely** with:

```python
# ─── Email Configuration ─────────────────────────────────────────────────────
_email_backend = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_BACKEND    = _email_backend
EMAIL_HOST       = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT       = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS    = os.environ.get('EMAIL_USE_TLS', 'True').lower() not in ('false', '0', 'no')
EMAIL_HOST_USER  = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'NextGenCV <noreply@nextgencv.com>')
SERVER_EMAIL        = DEFAULT_FROM_EMAIL
```

### 3.3 Update `.env`

Add these lines to your `.env` file:

```env
# ── Email (SMTP via Gmail) ────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=NextGenCV <your-gmail@gmail.com>
```

> For **development**, leave `EMAIL_BACKEND` commented out or set it to `django.core.mail.backends.console.EmailBackend` — emails print to the terminal and no SMTP is needed.

### 3.4 Update the Email Task

Open `apps/resumes/tasks.py` and find `send_verification_email_task`. Make sure it uses Django's `send_mail`:

```python
# apps/resumes/tasks.py  (add or update this task)
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id: int, token: str, base_url: str):
    """
    Send email verification link to a newly registered user.
    Retries up to 3 times on failure (network issues, SMTP errors).
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
        verify_url = f"{base_url}/auth/verify-email/{token}/"

        subject = "Verify your NextGenCV email address"
        plain_message = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Please verify your email address by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"This link expires in 48 hours.\n\n"
            f"If you did not create a NextGenCV account, ignore this email.\n\n"
            f"— The NextGenCV Team"
        )
        html_message = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #2563eb;">Verify your email address</h2>
          <p>Hi {user.first_name or user.username},</p>
          <p>Click the button below to verify your NextGenCV account:</p>
          <p style="text-align: center; margin: 32px 0;">
            <a href="{verify_url}"
               style="background: #2563eb; color: white; padding: 14px 28px;
                      text-decoration: none; border-radius: 6px; font-weight: bold;">
              Verify Email Address
            </a>
          </p>
          <p style="color: #6b7280; font-size: 14px;">
            This link expires in 48 hours. If you did not register, ignore this email.
          </p>
        </body></html>
        """
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")

    except User.DoesNotExist:
        logger.error(f"send_verification_email_task: User {user_id} not found")
    except Exception as exc:
        logger.error(f"Failed to send verification email to user {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(self, user_id: int, reset_url: str):
    """Send password reset email."""
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id)
        send_mail(
            subject="Reset your NextGenCV password",
            message=f"Reset your password: {reset_url}\n\nThis link expires in 1 hour.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=f"""
            <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <h2 style="color: #2563eb;">Reset your password</h2>
              <p>Hi {user.first_name or user.username},</p>
              <p>Click below to reset your NextGenCV password:</p>
              <p style="text-align: center; margin: 32px 0;">
                <a href="{reset_url}"
                   style="background: #2563eb; color: white; padding: 14px 28px;
                          text-decoration: none; border-radius: 6px; font-weight: bold;">
                  Reset Password
                </a>
              </p>
              <p style="color: #6b7280; font-size: 14px;">This link expires in 1 hour.</p>
            </body></html>
            """,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
```

### 3.5 Test Email Works

```bash
# In Django shell — sends a real email if SMTP is configured
python manage.py shell

from django.core.mail import send_mail
send_mail(
    subject='NextGenCV test email',
    message='If you see this, SMTP is working.',
    from_email='your-gmail@gmail.com',
    recipient_list=['your-gmail@gmail.com'],
)
```

If you see no error, email is working. Check your inbox (and spam folder).

#### Alternative: SendGrid

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
```

#### Alternative: Mailgun

```env
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@mg.yourdomain.com
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
```

---

## 4. Part B — Google SSO

### 4.1 Create Google OAuth Credentials

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or select existing) → name it `NextGenCV`
3. Go to **APIs & Services → OAuth consent screen**
   - User type: **External**
   - App name: `NextGenCV`
   - User support email: your Gmail
   - Developer contact: your Gmail
   - Click **Save and Continue** through all steps
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Name: `NextGenCV Web`
   - Authorised JavaScript origins:
     ```
     http://localhost:8000
     https://yourdomain.com
     ```
   - Authorised redirect URIs:
     ```
     http://localhost:8000/auth/google/login/callback/
     https://yourdomain.com/auth/google/login/callback/
     ```
5. Click **Create** — copy the **Client ID** and **Client Secret**

### 4.2 Install & Configure django-allauth

Already installed in Step 2. Now configure it.

### 4.3 Settings Changes

Open `config/settings.py` and make the following changes:

#### A — Add to `INSTALLED_APPS`

Find the `INSTALLED_APPS` list and add these entries **after** `'django.contrib.staticfiles'` and before your custom apps:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',          # ← ADD THIS (required by allauth)

    # Third-party apps
    'django_extensions',
    'django_celery_results',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # django-allauth (SSO)           ← ADD ALL FOUR BELOW
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin_oauth2',

    # Custom apps
    'apps.authentication',
    'apps.resumes',
    'apps.analyzer',
    'apps.analytics',
    'apps.templates_mgmt',
    'apps.tracker',
    'apps.api',
]
```

#### B — Add `SITE_ID` and allauth settings

Add this block anywhere in `settings.py` (after the existing auth settings):

```python
# ─── django-allauth (SSO) ────────────────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Default Django backend (username/password login still works)
    'django.contrib.auth.backends.ModelBackend',
    # allauth backend (handles Google + LinkedIn OAuth)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# allauth general settings
ACCOUNT_EMAIL_REQUIRED        = True
ACCOUNT_USERNAME_REQUIRED     = False   # Use email as primary identifier
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION    = 'optional'  # 'mandatory' in production
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET         = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if os.environ.get('DJANGO_ENV') == 'production' else 'http'

# Where to redirect after login/logout (matches existing NextGenCV settings)
LOGIN_REDIRECT_URL  = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'

# Social account settings
SOCIALACCOUNT_AUTO_SIGNUP    = True   # Auto-create user on first SSO login
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL    = True
SOCIALACCOUNT_LOGIN_ON_GET   = True   # Allow GET-based OAuth callback

# Google OAuth2 provider config
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id':     os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret':        os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key':           '',
        },
    },
    'linkedin_oauth2': {
        'SCOPE': ['r_liteprofile', 'r_emailaddress'],
        'PROFILE_FIELDS': ['id', 'first-name', 'last-name', 'email-address',
                           'picture-url', 'public-profile-url'],
        'APP': {
            'client_id':  os.environ.get('LINKEDIN_CLIENT_ID', ''),
            'secret':     os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
            'key':        '',
        },
    },
}
```

#### C — Add allauth middleware

In the `MIDDLEWARE` list, add `'allauth.account.middleware.AccountMiddleware'` **after** `'django.contrib.messages.middleware.MessageMiddleware'`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # ← ADD THIS LINE
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.GzipStaticMiddleware',
    'config.middleware.StaticFilesCacheMiddleware',
    'config.middleware.SecurityHeadersMiddleware',
    'config.middleware.PerformanceMonitoringMiddleware',
]
```

#### D — Add `request` context processor

In `TEMPLATES`, make sure `'django.template.context_processors.request'` is present (it already is in this project — no change needed).

### 4.4 URL Changes

Open `config/urls.py` and add the allauth URL include:

```python
# config/urls.py
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
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
    path('help/', documentation, name='help_documentation'),
    path('auth/', include('apps.authentication.urls')),

    # ── SSO (Google + LinkedIn via django-allauth) ──────────────────────────
    path('auth/', include('allauth.urls')),   # ← ADD THIS LINE

    path('resumes/', include('apps.resumes.urls')),
    path('analyzer/', include('apps.analyzer.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('templates/', include('apps.templates_mgmt.urls')),
    path('tracker/', include('apps.tracker.urls')),
    path('api/v1/', include('apps.api.urls')),
    path('api/performance/metrics/', collect_metrics, name='performance_metrics'),
    path('api/performance/summary/', performance_summary, name='performance_summary'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('performance/dashboard/', performance_dashboard,
                         name='performance_dashboard')]

handler404 = 'config.views.custom_404'
handler403 = 'config.views.custom_403'
handler500 = 'config.views.custom_500'
```

> The `path('auth/', include('allauth.urls'))` line adds all OAuth callback routes under `/auth/`. Google's callback will be at `/auth/google/login/callback/` which matches what you set in the Google Console.

### 4.5 Database Migration

```bash
python manage.py migrate
```

This creates the `sites`, `socialaccount`, `socialapp`, and `socialtoken` tables that allauth needs.

### 4.6 Django Admin Setup — Set Site Domain

1. Run the server: `python manage.py runserver`
2. Go to `http://localhost:8000/admin/`
3. Go to **Sites → Sites**
4. Click on the default site (ID=1, domain `example.com`)
5. Change:
   - **Domain name:** `localhost:8000` (dev) or `yourdomain.com` (production)
   - **Display name:** `NextGenCV`
6. Click **Save**

> This is required. allauth uses the `Sites` framework to build callback URLs. If the domain is wrong, OAuth will fail.

### 4.7 Login Template — Add Google Button

Open `templates/authentication/login.html` and add the Google login button. Find your existing login form and add this **above** or **below** it:

```html
<!-- templates/authentication/login.html -->

{% load socialaccount %}

<!-- existing login form here ... -->

<div class="sso-divider">
  <span>or continue with</span>
</div>

<div class="sso-buttons">

  <!-- Google Login Button -->
  <a href="{% provider_login_url 'google' %}"
     class="btn-sso btn-google">
    <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
    Continue with Google
  </a>

  <!-- LinkedIn Login Button -->
  <a href="{% provider_login_url 'linkedin_oauth2' %}"
     class="btn-sso btn-linkedin">
    <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="#0077B5"/>
    </svg>
    Continue with LinkedIn
  </a>

</div>
```

Add this CSS to your stylesheet (or inline in the template):

```css
.sso-divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  gap: 12px;
}
.sso-divider::before,
.sso-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border, #e5e7eb);
}
.sso-divider span {
  color: var(--text-muted, #6b7280);
  font-size: 14px;
  white-space: nowrap;
}
.sso-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.btn-sso {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid var(--border, #e5e7eb);
  background: var(--surface, #fff);
  color: var(--text, #111827);
  transition: background 0.15s, border-color 0.15s;
}
.btn-sso:hover {
  background: var(--surface-hover, #f9fafb);
  border-color: #9ca3af;
}
.btn-linkedin { border-color: #0077B5; color: #0077B5; }
.btn-linkedin:hover { background: #eff8ff; }
```

---

## 5. Part C — LinkedIn SSO

### 5.1 Create LinkedIn OAuth App

1. Go to [https://www.linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. Click **Create app**
   - App name: `NextGenCV`
   - LinkedIn Page: your company/personal page (required — create one if needed)
   - App logo: upload any logo
3. Click **Create app**
4. Go to the **Auth** tab:
   - Under **OAuth 2.0 settings → Authorized redirect URLs**, add:
     ```
     http://localhost:8000/auth/linkedin_oauth2/login/callback/
     https://yourdomain.com/auth/linkedin_oauth2/login/callback/
     ```
5. Go to the **Products** tab:
   - Request access to **Sign In with LinkedIn using OpenID Connect**
   - This is usually approved instantly
6. Back on the **Auth** tab, copy:
   - **Client ID**
   - **Client Secret**

### 5.2 Configure Provider

The LinkedIn provider is already configured in the `SOCIALACCOUNT_PROVIDERS` block added in Step 4.3. No additional code is needed.

### 5.3 Django Admin Setup — Add LinkedIn Social App

1. Go to `http://localhost:8000/admin/`
2. Go to **Social Accounts → Social applications → Add social application**
3. Fill in:
   - **Provider:** LinkedIn (OAuth2)
   - **Name:** LinkedIn
   - **Client id:** (paste your LinkedIn Client ID)
   - **Secret key:** (paste your LinkedIn Client Secret)
   - **Sites:** move `localhost:8000` from Available to Chosen
4. Click **Save**

> Repeat this step for Google too (see below).

### 5.4 Django Admin Setup — Add Google Social App

1. Go to **Social Accounts → Social applications → Add social application**
2. Fill in:
   - **Provider:** Google
   - **Name:** Google
   - **Client id:** (paste your Google Client ID)
   - **Secret key:** (paste your Google Client Secret)
   - **Sites:** move `localhost:8000` from Available to Chosen
3. Click **Save**

> **Alternative to Admin UI:** You can also set credentials directly in `settings.py` via the `SOCIALACCOUNT_PROVIDERS` `APP` dict (already done in Step 4.3). If both are set, the database record takes precedence.

---

## 6. Part D — Post-Login Signal (Auto-create Profile)

When a user logs in via Google or LinkedIn for the first time, allauth creates a `User` object but does not create the related `PersonalInfo` or `ActivityLog` records that NextGenCV expects. Add a signal to handle this.

Create a new file `apps/authentication/signals.py`:

```python
# apps/authentication/signals.py
"""
Signals fired after social account login.
Ensures every SSO user gets a proper NextGenCV profile on first login.
"""
import logging
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, pre_social_login
from allauth.account.signals import user_signed_up

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    """
    Fired when a new user registers — via SSO or standard form.
    Logs the signup event to ActivityLog.
    """
    from apps.authentication.models import ActivityLog
    try:
        ActivityLog.log(
            user=user,
            action='resume_created',   # closest available action type
            description=f'Account created for {user.username}',
        )
        logger.info(f'New user signed up: {user.username} ({user.email})')
    except Exception as e:
        logger.warning(f'Could not log signup for {user.username}: {e}')


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    """
    Fired when a social account (Google/LinkedIn) is connected to a user.
    Populates first_name and last_name from the social profile if not already set.
    """
    user = sociallogin.user
    try:
        extra = sociallogin.account.extra_data

        # Populate name from Google profile
        if sociallogin.account.provider == 'google':
            if not user.first_name:
                user.first_name = extra.get('given_name', '')
            if not user.last_name:
                user.last_name = extra.get('family_name', '')
            user.save(update_fields=['first_name', 'last_name'])

        # Populate name from LinkedIn profile
        elif sociallogin.account.provider == 'linkedin_oauth2':
            if not user.first_name:
                user.first_name = extra.get('localizedFirstName', '')
            if not user.last_name:
                user.last_name = extra.get('localizedLastName', '')
            user.save(update_fields=['first_name', 'last_name'])

        logger.info(
            f'Social account ({sociallogin.account.provider}) '
            f'linked to user {user.username}'
        )
    except Exception as e:
        logger.warning(f'Could not populate profile from social account: {e}')
```

Now register the signals in `apps/authentication/apps.py`:

```python
# apps/authentication/apps.py
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        import apps.authentication.signals  # noqa — registers signal handlers
```

---

## 7. Part E — Updated `.env.example`

Replace the contents of `.env.example` with this complete version:

```env
# NextGenCV Environment Variables
# Copy this file to .env and fill in your values:
#   cp .env.example .env

# ── Django ────────────────────────────────────────────────────────────────────
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ── Database ──────────────────────────────────────────────────────────────────
# Leave blank to use SQLite (default for dev)
# DATABASE_URL=postgres://user:password@localhost:5432/nextgencv

# ── Redis + Celery ────────────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── OpenAI ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.7

# ── Email (SMTP) ──────────────────────────────────────────────────────────────
# Dev: leave EMAIL_BACKEND commented out → emails print to console
# Prod: uncomment and fill in SMTP credentials
#
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-gmail@gmail.com
# EMAIL_HOST_PASSWORD=your-16-char-app-password
# DEFAULT_FROM_EMAIL=NextGenCV <your-gmail@gmail.com>

# ── Google SSO ────────────────────────────────────────────────────────────────
# Get from: https://console.cloud.google.com → APIs & Services → Credentials
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ── LinkedIn SSO ──────────────────────────────────────────────────────────────
# Get from: https://www.linkedin.com/developers/apps
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=

# ── Media files ───────────────────────────────────────────────────────────────
# MEDIA_ROOT=/var/www/nextgencv/media

# ── Environment tag ───────────────────────────────────────────────────────────
# DJANGO_ENV=production
```

---

## 8. Part F — Full Updated `settings.py` Block

This is the complete diff of everything added to `config/settings.py`. Apply each change in the location described.

### Change 1 — INSTALLED_APPS (add 6 lines)

```python
# After 'django.contrib.staticfiles', add:
'django.contrib.sites',

# After 'corsheaders', add:
'allauth',
'allauth.account',
'allauth.socialaccount',
'allauth.socialaccount.providers.google',
'allauth.socialaccount.providers.linkedin_oauth2',
```

### Change 2 — MIDDLEWARE (add 1 line)

```python
# After 'django.contrib.messages.middleware.MessageMiddleware', add:
'allauth.account.middleware.AccountMiddleware',
```

### Change 3 — Email block (replace existing)

```python
# ─── Email Configuration ─────────────────────────────────────────────────────
EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND',
                        'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True').lower() not in ('false','0','no')
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'NextGenCV <noreply@nextgencv.com>')
SERVER_EMAIL        = DEFAULT_FROM_EMAIL
```

### Change 4 — SSO block (add after email block)

```python
# ─── django-allauth (SSO) ────────────────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED        = True
ACCOUNT_USERNAME_REQUIRED     = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION    = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET         = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if os.environ.get('DJANGO_ENV') == 'production' else 'http'

SOCIALACCOUNT_AUTO_SIGNUP    = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL    = True
SOCIALACCOUNT_LOGIN_ON_GET   = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret':    os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key':       '',
        },
    },
    'linkedin_oauth2': {
        'SCOPE': ['r_liteprofile', 'r_emailaddress'],
        'PROFILE_FIELDS': ['id', 'first-name', 'last-name',
                           'email-address', 'picture-url', 'public-profile-url'],
        'APP': {
            'client_id': os.environ.get('LINKEDIN_CLIENT_ID', ''),
            'secret':    os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
            'key':       '',
        },
    },
}
```

---

## 9. Part G — Full Updated `urls.py`

```python
# config/urls.py
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
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
    path('help/', documentation, name='help_documentation'),

    # Custom auth routes (register, verify-email, dashboard, profile, etc.)
    path('auth/', include('apps.authentication.urls')),

    # django-allauth SSO routes (Google, LinkedIn OAuth callbacks)
    # Adds: /auth/google/login/, /auth/google/login/callback/
    #       /auth/linkedin_oauth2/login/, /auth/linkedin_oauth2/login/callback/
    path('auth/', include('allauth.urls')),

    path('resumes/', include('apps.resumes.urls')),
    path('analyzer/', include('apps.analyzer.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('templates/', include('apps.templates_mgmt.urls')),
    path('tracker/', include('apps.tracker.urls')),
    path('api/v1/', include('apps.api.urls')),
    path('api/performance/metrics/', collect_metrics, name='performance_metrics'),
    path('api/performance/summary/', performance_summary, name='performance_summary'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('performance/dashboard/', performance_dashboard,
                         name='performance_dashboard')]

handler404 = 'config.views.custom_404'
handler403 = 'config.views.custom_403'
handler500 = 'config.views.custom_500'
```

---

## 10. Testing Checklist

Run through each item after completing all steps above.

### Email

```
[ ] python manage.py shell → send_mail() → email arrives in inbox
[ ] Register a new account → verification email arrives
[ ] Click verification link → account marked as verified
[ ] Password reset → reset email arrives with working link
[ ] Check spam folder if emails are not arriving
```

### Google SSO

```
[ ] python manage.py migrate → no errors
[ ] Admin → Sites → domain set to localhost:8000
[ ] Admin → Social Applications → Google app created with correct client_id + secret
[ ] Visit http://localhost:8000/auth/login/ → Google button visible
[ ] Click Google button → redirected to Google consent screen
[ ] Approve → redirected to /auth/dashboard/
[ ] Admin → Social Accounts → Social accounts → new record visible
[ ] Log out → log in again with Google → works without re-consent
```

### LinkedIn SSO

```
[ ] Admin → Social Applications → LinkedIn app created with correct client_id + secret
[ ] Visit http://localhost:8000/auth/login/ → LinkedIn button visible
[ ] Click LinkedIn button → redirected to LinkedIn consent screen
[ ] Approve → redirected to /auth/dashboard/
[ ] Admin → Social Accounts → Social accounts → LinkedIn record visible
```

### Signal / Profile

```
[ ] New Google login → user.first_name and user.last_name populated from Google profile
[ ] New LinkedIn login → user.first_name and user.last_name populated from LinkedIn profile
[ ] ActivityLog → signup event recorded for new SSO users
```

---

## 11. Troubleshooting

### "Site matching query does not exist"

```
django.contrib.sites.models.Site.DoesNotExist
```

**Fix:** Go to Admin → Sites → make sure a site with ID=1 exists and its domain matches your server.

---

### "redirect_uri_mismatch" (Google)

**Fix:** The redirect URI in your Google Console must exactly match what allauth sends. Check:
- Google Console → Credentials → your OAuth client → Authorised redirect URIs
- Must include: `http://localhost:8000/auth/google/login/callback/`
- No trailing slash differences, no `http` vs `https` mismatch

---

### "invalid_redirect_uri" (LinkedIn)

**Fix:** Same issue. LinkedIn → App → Auth → Authorized redirect URLs must include:
`http://localhost:8000/auth/linkedin_oauth2/login/callback/`

---

### Email not sending (SMTP)

```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Fix:**
1. Make sure you are using an **App Password**, not your regular Gmail password
2. Make sure 2-Step Verification is enabled on your Google account
3. Double-check `EMAIL_HOST_USER` matches the Gmail account you generated the App Password for

---

### "allauth.account.middleware.AccountMiddleware" error

```
django.core.exceptions.ImproperlyConfigured: allauth.account.middleware.AccountMiddleware must be added to settings.MIDDLEWARE
```

**Fix:** Add `'allauth.account.middleware.AccountMiddleware'` to `MIDDLEWARE` in `settings.py` (Step 4.3C).

---

### SSO user has no password (cannot log in with username/password)

This is expected. SSO users authenticate via Google/LinkedIn only. If they want a password, they can use the **Change Password** form in `/auth/profile/` — Django will set a usable password.

---

### LinkedIn "r_liteprofile" scope deprecated

LinkedIn deprecated `r_liteprofile` in 2023. If you get a scope error, update the scope in `settings.py`:

```python
'linkedin_oauth2': {
    'SCOPE': ['openid', 'profile', 'email'],
    ...
}
```

And make sure you have the **Sign In with LinkedIn using OpenID Connect** product enabled on your LinkedIn app.

---

*End of SSO & Email Setup Guide*
