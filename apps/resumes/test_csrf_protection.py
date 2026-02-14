"""
Tests for CSRF protection on forms.

Validates: Requirements 13.1
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.resumes.models import Resume


class CSRFProtectionTestCase(TestCase):
    """Test CSRF protection across all form submissions."""
    
    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.login(username='testuser', password='testpass123')
        
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
    
    def test_resume_create_requires_csrf_token(self):
        """Test that resume creation requires CSRF token."""
        # Attempt to create resume without CSRF token
        response = self.client.post('/resumes/create/', {
            'title': 'New Resume',
            'template': 'professional'
        })
        
        # Should be rejected with 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_resume_update_requires_csrf_token(self):
        """Test that resume update requires CSRF token."""
        # Attempt to update resume without CSRF token
        response = self.client.post(f'/resumes/{self.resume.id}/edit/', {
            'title': 'Updated Resume',
            'template': 'modern'
        })
        
        # Should be rejected with 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_resume_delete_requires_csrf_token(self):
        """Test that resume deletion requires CSRF token."""
        # Attempt to delete resume without CSRF token
        response = self.client.post(f'/resumes/{self.resume.id}/delete/')
        
        # Should be rejected with 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_csrf_middleware_enabled(self):
        """Test that CSRF middleware is enabled in settings."""
        from django.conf import settings
        
        # Check that CSRF middleware is in MIDDLEWARE setting
        self.assertIn(
            'django.middleware.csrf.CsrfViewMiddleware',
            settings.MIDDLEWARE
        )
    
    def test_csrf_token_validation(self):
        """Test that forms validate CSRF tokens."""
        # This test verifies that Django's CSRF protection is working
        # by attempting a POST without CSRF token
        response = self.client.post('/resumes/create/', {
            'title': 'Test',
            'template': 'professional'
        })
        
        # Should be rejected
        self.assertEqual(response.status_code, 403)
