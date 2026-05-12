"""
Fixes MultipleObjectsReturned error by removing duplicate SocialApp records.
Keeps the one with the correct client_id from .env and links it to the site.

Run with:
    python fix_sso_duplicates.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

site = Site.objects.get(pk=1)
print(f"Site: {site.domain}\n")

for provider, env_id_key, env_secret_key, label in [
    ('google',          'GOOGLE_CLIENT_ID',    'GOOGLE_CLIENT_SECRET',    'Google'),
    ('linkedin_oauth2', 'LINKEDIN_CLIENT_ID',  'LINKEDIN_CLIENT_SECRET',  'LinkedIn'),
]:
    correct_id     = os.environ.get(env_id_key, '').strip()
    correct_secret = os.environ.get(env_secret_key, '').strip()

    apps = list(SocialApp.objects.filter(provider=provider))
    print(f"[{label}] Found {len(apps)} record(s):")
    for a in apps:
        linked = list(a.sites.values_list('domain', flat=True))
        print(f"  id={a.id}  client_id={a.client_id[:20]}  sites={linked}")

    if len(apps) == 0:
        if correct_id and correct_secret:
            app = SocialApp.objects.create(
                provider=provider,
                name=label,
                client_id=correct_id,
                secret=correct_secret,
            )
            app.sites.add(site)
            print(f"  → Created new record id={app.id}")
        else:
            print(f"  → No credentials in .env — skipping")

    elif len(apps) == 1:
        app = apps[0]
        if correct_id:
            app.client_id = correct_id
            app.secret    = correct_secret
            app.name      = label
            app.save()
        app.sites.set([site])
        print(f"  → OK (single record, updated & linked to site)")

    else:
        # Multiple records — keep the one whose client_id matches .env, delete the rest
        keeper = None
        if correct_id:
            for a in apps:
                if a.client_id == correct_id:
                    keeper = a
                    break
        if keeper is None:
            # Fall back to keeping the one already linked to the site
            for a in apps:
                if site in a.sites.all():
                    keeper = a
                    break
        if keeper is None:
            keeper = apps[0]  # last resort: keep first

        # Delete duplicates
        for a in apps:
            if a.id != keeper.id:
                a.delete()
                print(f"  → Deleted duplicate id={a.id}")

        # Update keeper
        if correct_id:
            keeper.client_id = correct_id
            keeper.secret    = correct_secret
            keeper.name      = label
            keeper.save()
        keeper.sites.set([site])
        print(f"  → Kept id={keeper.id}, linked to {site.domain}")

    print()

# Final verification
print("── Final state ──────────────────────────────────────────")
print(f"Site: {Site.objects.get(pk=1).domain}")
for a in SocialApp.objects.all():
    linked = list(a.sites.values_list('domain', flat=True))
    print(f"  provider={a.provider}  client_id={a.client_id[:20]}  sites={linked}")
print("\nDone. Restart the server and try the SSO buttons again.")
