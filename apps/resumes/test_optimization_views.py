"""
Tests for Resume Optimization Module views.
Tests the complete optimization workflow: fix_resume, fix_preview, fix_accept, fix_reject.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.resumes.models import Resume, Experience, OptimizationHistory, ResumeVersion
from datetime import date


class OptimizationViewsTestCase(TestCase):
    """Test cases for resume optimization views."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Add experience with weak bullet points
        self.experience = Experience.objects.create(
            resume=self.resume,
            company='Test Company',
            role='Software Developer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Worked on projects\nHelped with development\nDid some coding',
            order=1
        )
        
        # Login
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_fix_resume_view_get(self):
        """Test GET request to fix_resume view displays form."""
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/fix_resume.html')
        self.assertIn('resume', response.context)
    
    def test_fix_resume_view_requires_login(self):
        """Test that fix_resume view requires authentication."""
        self.client.logout()
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_fix_resume_view_post_no_job_description(self):
        """Test POST request without job description shows error."""
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('job description' in str(m).lower() for m in messages))
    
    def test_fix_resume_view_post_short_job_description(self):
        """Test POST request with too short job description shows error."""
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        response = self.client.post(url, {
            'job_description': 'Too short'
        })
        
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('too short' in str(m).lower() for m in messages))
    
    def test_fix_resume_view_post_valid(self):
        """Test POST request with valid job description redirects to preview."""
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        job_description = 'Looking for a Python developer with Django experience. ' * 5
        
        response = self.client.post(url, {
            'job_description': job_description
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('fix/preview', response.url)
        
        # Check session data
        session_key = f'fix_resume_{self.resume.id}_job_description'
        self.assertIn(session_key, self.client.session)
        self.assertEqual(self.client.session[session_key], job_description)
    
    def test_fix_resume_view_authorization(self):
        """Test that users can only optimize their own resumes."""
        # Create another user and their resume
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_resume = Resume.objects.create(
            user=other_user,
            title='Other Resume',
            template='professional'
        )
        
        # Try to access other user's resume
        url = reverse('fix_resume', kwargs={'pk': other_resume.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)
    
    def test_fix_reject_view(self):
        """Test fix_reject view clears session and redirects."""
        # Set up session data
        session = self.client.session
        session[f'fix_resume_{self.resume.id}_job_description'] = 'Test job description'
        session[f'fix_resume_{self.resume.id}_results'] = {'test': 'data'}
        session.save()
        
        # Call reject view
        url = reverse('fix_reject', kwargs={'pk': self.resume.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/resumes/{self.resume.id}/', response.url)
        
        # Check session data is cleared
        self.assertNotIn(f'fix_resume_{self.resume.id}_job_description', self.client.session)
        self.assertNotIn(f'fix_resume_{self.resume.id}_results', self.client.session)
    
    def test_fix_reject_requires_post(self):
        """Test that fix_reject only accepts POST requests."""
        url = reverse('fix_reject', kwargs={'pk': self.resume.id})
        response = self.client.get(url)
        
        # Should redirect to preview
        self.assertEqual(response.status_code, 302)
        self.assertIn('fix/preview', response.url)
    
    def test_url_patterns_exist(self):
        """Test that all optimization URL patterns are configured."""
        # Test fix_resume URL
        url = reverse('fix_resume', kwargs={'pk': 1})
        self.assertEqual(url, '/resumes/1/fix/')
        
        # Test fix_preview URL
        url = reverse('fix_preview', kwargs={'pk': 1})
        self.assertEqual(url, '/resumes/1/fix/preview/')
        
        # Test fix_accept URL
        url = reverse('fix_accept', kwargs={'pk': 1})
        self.assertEqual(url, '/resumes/1/fix/accept/')
        
        # Test fix_reject URL
        url = reverse('fix_reject', kwargs={'pk': 1})
        self.assertEqual(url, '/resumes/1/fix/reject/')
