"""
Tests for PDF Upload Module Views

This test file verifies the PDF upload, parsing, and import functionality.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.resumes.models import UploadedResume, Resume
import os


class PDFUploadViewsTest(TestCase):
    """Test cases for PDF upload module views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_pdf_upload_view_get(self):
        """Test GET request to pdf_upload view displays form."""
        response = self.client.get(reverse('pdf_upload'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resumes/pdf_upload.html')
        self.assertContains(response, 'Upload Resume PDF')
    
    def test_pdf_upload_view_requires_login(self):
        """Test that pdf_upload view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse('pdf_upload'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_pdf_upload_view_post_no_file(self):
        """Test POST request without file shows error."""
        response = self.client.post(reverse('pdf_upload'), {})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please select a PDF file')
    
    def test_pdf_parse_review_view_requires_login(self):
        """Test that pdf_parse_review view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse('pdf_parse_review', kwargs={'upload_id': 1}))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_pdf_parse_review_view_authorization(self):
        """Test that users can only view their own uploads."""
        # Create another user and their upload
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        uploaded_resume = UploadedResume.objects.create(
            user=other_user,
            original_filename='test.pdf',
            file_size=1024,
            status='parsed',
            parsed_data={}
        )
        
        # Try to access other user's upload
        response = self.client.get(
            reverse('pdf_parse_review', kwargs={'upload_id': uploaded_resume.id})
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_pdf_import_confirm_requires_post(self):
        """Test that pdf_import_confirm only accepts POST requests."""
        uploaded_resume = UploadedResume.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_size=1024,
            status='parsed',
            parsed_data={}
        )
        
        response = self.client.get(
            reverse('pdf_import_confirm', kwargs={'upload_id': uploaded_resume.id})
        )
        
        # Should redirect back to review page
        self.assertEqual(response.status_code, 302)
    
    def test_pdf_import_confirm_authorization(self):
        """Test that users can only import their own uploads."""
        # Create another user and their upload
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        uploaded_resume = UploadedResume.objects.create(
            user=other_user,
            original_filename='test.pdf',
            file_size=1024,
            status='parsed',
            parsed_data={}
        )
        
        # Try to import other user's upload
        response = self.client.post(
            reverse('pdf_import_confirm', kwargs={'upload_id': uploaded_resume.id}),
            {'title': 'Test Resume', 'template': 'professional'}
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_url_patterns_exist(self):
        """Test that all PDF upload URL patterns are configured."""
        # Test pdf_upload URL
        url = reverse('pdf_upload')
        self.assertEqual(url, '/resumes/upload/')
        
        # Test pdf_parse_review URL
        url = reverse('pdf_parse_review', kwargs={'upload_id': 1})
        self.assertEqual(url, '/resumes/upload/1/review/')
        
        # Test pdf_import_confirm URL
        url = reverse('pdf_import_confirm', kwargs={'upload_id': 1})
        self.assertEqual(url, '/resumes/upload/1/confirm/')


class PDFUploadIntegrationTest(TestCase):
    """Integration tests for complete PDF upload workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_upload_workflow_with_mock_data(self):
        """Test complete workflow from upload to import with mock data."""
        # Create a mock uploaded resume with parsed data
        uploaded_resume = UploadedResume.objects.create(
            user=self.user,
            original_filename='test_resume.pdf',
            file_size=1024,
            status='parsed',
            parsing_confidence=0.85,
            extracted_text='Sample resume text',
            parsed_data={
                'personal_info': {
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'phone': '123-456-7890',
                    'location': 'New York, NY'
                },
                'experiences': [
                    {
                        'company': 'Tech Corp',
                        'title': 'Software Engineer',
                        'start_date': 'January 2020',
                        'end_date': 'Present',
                        'description': '• Developed web applications'
                    }
                ],
                'education': [
                    {
                        'institution': 'University of Example',
                        'degree': 'Bachelor of Science',
                        'field_of_study': 'Computer Science',
                        'graduation_date': '2019'
                    }
                ],
                'skills': [
                    {'name': 'Python', 'category': 'Programming'},
                    {'name': 'Django', 'category': 'Framework'}
                ]
            }
        )
        
        # Step 1: View the review page
        response = self.client.get(
            reverse('pdf_parse_review', kwargs={'upload_id': uploaded_resume.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Tech Corp')
        
        # Step 2: Import the resume
        response = self.client.post(
            reverse('pdf_import_confirm', kwargs={'upload_id': uploaded_resume.id}),
            {
                'title': 'My Imported Resume',
                'template': 'professional'
            }
        )
        
        # Should redirect to resume detail
        self.assertEqual(response.status_code, 302)
        
        # Verify resume was created
        self.assertEqual(Resume.objects.filter(user=self.user).count(), 1)
        resume = Resume.objects.get(user=self.user)
        self.assertEqual(resume.title, 'My Imported Resume')
        
        # Verify upload status was updated
        uploaded_resume.refresh_from_db()
        self.assertEqual(uploaded_resume.status, 'imported')
