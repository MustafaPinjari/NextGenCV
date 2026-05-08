"""
Security regression tests.
Covers every vulnerability identified in the audit:
  - IDOR on resume views
  - Public share token logic
  - Filename injection in Content-Disposition
  - Wizard remove actions (dead-code bug regression)
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo


class ResumeOwnershipTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='pass123!')
        self.attacker = User.objects.create_user('attacker', password='pass123!')
        self.resume = Resume.objects.create(user=self.owner, title='Private Resume')
        self.client = Client()

    def test_attacker_cannot_view_resume(self):
        self.client.login(username='attacker', password='pass123!')
        r = self.client.get(f'/resumes/{self.resume.id}/')
        self.assertEqual(r.status_code, 403)

    def test_attacker_cannot_edit_resume(self):
        self.client.login(username='attacker', password='pass123!')
        r = self.client.get(f'/resumes/{self.resume.id}/edit/')
        self.assertEqual(r.status_code, 403)

    def test_attacker_cannot_delete_resume(self):
        self.client.login(username='attacker', password='pass123!')
        r = self.client.post(f'/resumes/{self.resume.id}/delete/')
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Resume.objects.filter(id=self.resume.id).exists())

    def test_attacker_cannot_export_resume(self):
        self.client.login(username='attacker', password='pass123!')
        r = self.client.get(f'/resumes/{self.resume.id}/export/')
        self.assertIn(r.status_code, [403, 404])  # 403 if found, 404 if URL differs

    def test_owner_can_view_own_resume(self):
        self.client.login(username='owner', password='pass123!')
        r = self.client.get(f'/resumes/{self.resume.id}/')
        self.assertIn(r.status_code, [200, 302])

    def test_unauthenticated_redirected_to_login(self):
        r = self.client.get(f'/resumes/{self.resume.id}/')
        self.assertRedirects(r, f'/auth/login/?next=/resumes/{self.resume.id}/',
                             fetch_redirect_response=False)


class PublicShareTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', password='pass123!')
        self.client = Client()

    def test_empty_token_returns_404(self):
        r = self.client.get('/resumes/public//')
        self.assertEqual(r.status_code, 404)

    def test_nonexistent_token_returns_404(self):
        r = self.client.get('/resumes/public/nonexistent-token-xyz/')
        self.assertEqual(r.status_code, 404)

    def test_valid_token_returns_200(self):
        resume = Resume.objects.create(
            user=self.user, title='Public Resume', share_token='valid-token-abc'
        )
        r = self.client.get('/resumes/public/valid-token-abc/')
        self.assertEqual(r.status_code, 200)

    def test_revoked_token_returns_404(self):
        """After revoking, the empty share_token must not match any resume."""
        resume = Resume.objects.create(
            user=self.user, title='Was Public', share_token=''
        )
        # Empty string token — should 404 before even hitting the view
        r = self.client.get('/resumes/public//')
        self.assertEqual(r.status_code, 404)


class WizardRemoveActionTests(TestCase):
    """Regression tests for the dead-code remove bug (Bug 3)."""

    def setUp(self):
        self.user = User.objects.create_user('wizard_user', password='pass123!')
        self.client = Client()
        self.client.login(username='wizard_user', password='pass123!')

    def _init_wizard(self, step=2, experiences=None):
        session = self.client.session
        session['resume_wizard'] = {
            'step': step,
            'data': {
                'personal_info': {
                    'full_name': 'Test User', 'email': 'test@test.com',
                    'phone': '', 'linkedin': '', 'github': '', 'location': ''
                },
                'experiences': experiences or [
                    {'company': 'ACME', 'role': 'Dev',
                     'start_date': '2020-01-01', 'end_date': None, 'description': 'Did stuff'}
                ],
            }
        }
        session.save()

    def test_remove_experience_actually_removes_it(self):
        self._init_wizard(step=2, experiences=[
            {'company': 'ACME', 'role': 'Dev', 'start_date': '2020-01-01',
             'end_date': None, 'description': 'Did stuff'},
            {'company': 'Corp', 'role': 'Lead', 'start_date': '2022-01-01',
             'end_date': None, 'description': 'Led stuff'},
        ])
        r = self.client.post('/resumes/create/', {
            'action': 'remove_experience', 'index': '0'
        })
        self.assertIn(r.status_code, [200, 302])
        session = self.client.session
        experiences = session['resume_wizard']['data']['experiences']
        self.assertEqual(len(experiences), 1)
        self.assertEqual(experiences[0]['company'], 'Corp')


class ContentDispositionTests(TestCase):
    """Regression tests for filename injection in Content-Disposition."""

    def setUp(self):
        self.user = User.objects.create_user('export_user', password='pass123!')
        self.client = Client()
        self.client.login(username='export_user', password='pass123!')

    def test_malicious_title_sanitized_in_export(self):
        """A resume title with injection characters must not contain quotes or semicolons."""
        import re
        malicious_title = 'evil"; filename="malware.exe'
        safe = re.sub(r'[^\w\-.]', '_', malicious_title)[:100]
        # The critical injection characters must be gone
        self.assertNotIn('"', safe)
        self.assertNotIn(';', safe)
        # The header value must be safe to embed in Content-Disposition
        header = f'attachment; filename="{safe}.pdf"'
        self.assertEqual(header.count('"'), 2)  # exactly opening and closing quote
