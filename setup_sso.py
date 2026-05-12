"""
Run this once after adding credentials to .env:
    python setup_sso.py

Fixes:
  1. Sets Site domain to localhost:8000
  2. Creates/updates Google and LinkedIn SocialApp records from .env
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# ── 1. Fix Site domain ────────────────────────────────────────────────────────
site, _ = Site.objects.get_or_create(pk=1)
site.domain = 'localhost:8000'
site.name   = 'NextGenCV'
site.save()
print(f'[OK] Site set to: {site.domain}')

# ── 2. Google SocialApp ───────────────────────────────────────────────────────
google_id     = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
google_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()

if google_id and google_secret:
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={'name': 'Google'}
    )
    app.name      = 'Google'
    app.client_id = google_id
    app.secret    = google_secret
    app.save()
    app.sites.add(site)
    status = 'created' if created else 'updated'
    print(f'[OK] Google SocialApp {status} (client_id: {google_id[:12]}...)')
else:
    print('[WARN] GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing in .env — skipping Google')

# ── 3. LinkedIn SocialApp ─────────────────────────────────────────────────────
li_id     = os.environ.get('LINKEDIN_CLIENT_ID', '').strip()
li_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '').strip()

if li_id and li_secret:
    app, created = SocialApp.objects.get_or_create(
        provider='linkedin_oauth2',
        defaults={'name': 'LinkedIn'}
    )
    app.name      = 'LinkedIn'
    app.client_id = li_id
    app.secret    = li_secret
    app.save()
    app.sites.add(site)
    status = 'created' if created else 'updated'
    print(f'[OK] LinkedIn SocialApp {status} (client_id: {li_id[:12]}...)')
else:
    print('[WARN] LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET missing in .env — skipping LinkedIn')

# ── 4. Verify ─────────────────────────────────────────────────────────────────
print('\n── Verification ──────────────────────────────────────────')
print(f'Site:  {Site.objects.get(pk=1).domain}')
for a in SocialApp.objects.all():
    sites = list(a.sites.values_list('domain', flat=True))
    print(f'App:   provider={a.provider}  client_id={a.client_id[:12]}...  sites={sites}')
print('\nDone. Restart the dev server and try the SSO buttons.')
