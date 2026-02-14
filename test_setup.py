#!/usr/bin/env python
"""
Test script to verify Django project setup
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.urls import get_resolver

print("=" * 60)
print("Django Project Setup Verification")
print("=" * 60)

# Check installed apps
print("\n✓ Installed Apps:")
for app in settings.INSTALLED_APPS:
    if app.startswith('apps.'):
        print(f"  - {app}")

# Check templates directory
print(f"\n✓ Templates Directory: {settings.TEMPLATES[0]['DIRS']}")

# Check static files
print(f"✓ Static URL: {settings.STATIC_URL}")
print(f"✓ Static Root: {settings.STATIC_ROOT}")

# Check database
print(f"\n✓ Database: {settings.DATABASES['default']['ENGINE']}")
print(f"✓ Database Name: {settings.DATABASES['default']['NAME']}")

# Check URL patterns
print("\n✓ URL Patterns:")
resolver = get_resolver()
for pattern in resolver.url_patterns:
    print(f"  - {pattern.pattern}")

print("\n" + "=" * 60)
print("✓ Project setup complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: python manage.py runserver")
print("2. Visit: http://localhost:8000")
print("=" * 60)
