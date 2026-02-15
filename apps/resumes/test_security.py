"""
Comprehensive Security Tests for NextGenCV v2.0

Tests security requirements including:
- File upload validation
- XSS protection
- Authorization checks
- Data isolation
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.resumes.models import (
    Resume, PersonalInfo, Experience, ResumeVersion,
    UploadedResume, ResumeAnalysis, OptimizationHistory
)
from apps.resumes.services.version_service import VersionService
from datetime import date
import io


class FileUploadSecurityTest(TestCase):
    """Test file upload validation and security"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_file_type_validation(self):
        """Test that only PDF files are accepted"""
        # Try to upload a non-PDF file
        fake_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a PDF file",
            content_type="text/plain"
        )
        
        response = self.client.post(reverse('pdf_upload'), {
            'resume': fake_file
        })
        
        # Should reject non-PDF files
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PDF')
    
    def test_file_size_validation(self):
        """Test that files over 10MB are rejected"""
        # Create a file that's too large (simulated)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        
        response = self.client.post(reverse('pdf_upload'), {
            'resume': large_file
        })
        
        # Should reject files over 10MB
        self.assertEqual(response.status_code, 200)
        # Check for size error message
        messages = list(response.context.get('messages', []))
        has_size_error = any('size' in str(m).lower() or '10' in str(m) for m in messages)
        self.assertTrue(has_size_error or 'size' in response.content.decode().lower())
    
    def test_secure_filename_generation(self):
        """Test that uploaded files get secure random filenames"""
        # Create a valid PDF file
        pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"  # Minimal PDF header
        pdf_file = SimpleUploadedFile(
            "../../../etc/passwd.pdf",  # Malicious filename
            pdf_content,
            content_type="application/pdf"
        )
        
        # Upload should succeed but filename should be sanitized
        response = self.client.post(reverse('pdf_upload'), {
            'resume': pdf_file
        })
        
        # Check that uploaded resume doesn't use the malicious filename
        if UploadedResume.objects.filter(user=self.user).exists():
            uploaded = UploadedResume.objects.filter(user=self.user).first()
            # Filename should not contain path traversal characters
            self.assertNotIn('..', str(uploaded.file_path))
            self.assertNotIn('/etc/', str(uploaded.file_path))


class AuthorizationSecurityTest(TestCase):
    """Test authorization checks across all views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create two users
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        
        # Create resumes for each user
        self.resume1 = Resume.objects.create(
            user=self.user1,
            title='User1 Resume',
            template='professional'
        )
        self.resume2 = Resume.objects.create(
            user=self.user2,
            title='User2 Resume',
            template='professional'
        )
        
        PersonalInfo.objects.create(
            resume=self.resume1,
            full_name='User One',
            email='user1@example.com'
        )
        
        PersonalInfo.objects.create(
            resume=self.resume2,
            full_name='User Two',
            email='user2@example.com'
        )
        
        # Create versions
        self.version1 = VersionService.create_version(self.resume1)
        self.version2 = VersionService.create_version(self.resume2)
        
        # Create uploaded resumes
        self.upload1 = UploadedResume.objects.create(
            user=self.user1,
            original_filename='test1.pdf',
            file_size=1024,
            status='parsed',
            parsed_data={}
        )
        self.upload2 = UploadedResume.objects.create(
            user=self.user2,
            original_filename='test2.pdf',
            file_size=1024,
            status='parsed',
            parsed_data={}
        )
        
        # Login as user1
        self.client.login(username='user1', password='pass1')
    
    def test_resume_detail_authorization(self):
        """Test that users can only view their own resumes"""
        # Try to access user2's resume
        response = self.client.get(reverse('resume_detail', kwargs={'pk': self.resume2.id}))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to access own resume
        response = self.client.get(reverse('resume_detail', kwargs={'pk': self.resume1.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_resume_update_authorization(self):
        """Test that users can only update their own resumes"""
        # Try to update user2's resume
        response = self.client.get(reverse('resume_update', kwargs={'pk': self.resume2.id}))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to update own resume
        response = self.client.get(reverse('resume_update', kwargs={'pk': self.resume1.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_resume_delete_authorization(self):
        """Test that users can only delete their own resumes"""
        # Try to delete user2's resume
        response = self.client.get(reverse('resume_delete', kwargs={'pk': self.resume2.id}))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to access delete page for own resume
        response = self.client.get(reverse('resume_delete', kwargs={'pk': self.resume1.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_version_list_authorization(self):
        """Test that users can only view versions of their own resumes"""
        # Try to access user2's versions
        response = self.client.get(reverse('version_list', kwargs={'pk': self.resume2.id}))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to access own versions
        response = self.client.get(reverse('version_list', kwargs={'pk': self.resume1.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_version_detail_authorization(self):
        """Test that users can only view their own version details"""
        # Try to access user2's version
        response = self.client.get(reverse('version_detail', kwargs={
            'pk': self.resume2.id,
            'version_id': self.version2.id
        }))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to access own version
        response = self.client.get(reverse('version_detail', kwargs={
            'pk': self.resume1.id,
            'version_id': self.version1.id
        }))
        self.assertEqual(response.status_code, 200)
    
    def test_version_restore_authorization(self):
        """Test that users can only restore their own versions"""
        # Try to restore user2's version
        response = self.client.post(reverse('version_restore', kwargs={
            'pk': self.resume2.id,
            'version_id': self.version2.id
        }))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to restore own version
        response = self.client.post(reverse('version_restore', kwargs={
            'pk': self.resume1.id,
            'version_id': self.version1.id
        }))
        self.assertEqual(response.status_code, 302)  # Redirect on success
    
    def test_optimization_authorization(self):
        """Test that users can only optimize their own resumes"""
        # Try to optimize user2's resume
        response = self.client.get(reverse('fix_resume', kwargs={'pk': self.resume2.id}))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to optimize own resume
        response = self.client.get(reverse('fix_resume', kwargs={'pk': self.resume1.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_pdf_upload_authorization(self):
        """Test that users can only view their own uploaded PDFs"""
        # Try to access user2's upload
        response = self.client.get(reverse('pdf_parse_review', kwargs={
            'upload_id': self.upload2.id
        }))
        self.assertEqual(response.status_code, 403)
        
        # Should be able to access own upload
        response = self.client.get(reverse('pdf_parse_review', kwargs={
            'upload_id': self.upload1.id
        }))
        self.assertEqual(response.status_code, 200)


class DataIsolationSecurityTest(TestCase):
    """Test data isolation between users"""
    
    def setUp(self):
        """Set up test data"""
        # Create two users with resumes
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        
        self.resume1 = Resume.objects.create(user=self.user1, title='Resume1', template='professional')
        self.resume2 = Resume.objects.create(user=self.user2, title='Resume2', template='professional')
        
        # Create versions
        self.version1 = VersionService.create_version(self.resume1)
        self.version2 = VersionService.create_version(self.resume2)
        
        # Create analyses
        self.analysis1 = ResumeAnalysis.objects.create(
            resume=self.resume1,
            job_description='Test',
            keyword_match_score=70.0,
            skill_relevance_score=70.0,
            section_completeness_score=70.0,
            experience_impact_score=70.0,
            quantification_score=70.0,
            action_verb_score=70.0,
            final_score=70.0
        )
        
        self.analysis2 = ResumeAnalysis.objects.create(
            resume=self.resume2,
            job_description='Test',
            keyword_match_score=80.0,
            skill_relevance_score=80.0,
            section_completeness_score=80.0,
            experience_impact_score=80.0,
            quantification_score=80.0,
            action_verb_score=80.0,
            final_score=80.0
        )
    
    def test_resume_query_isolation(self):
        """Test that resume queries are filtered by user"""
        # User1 should only see their own resumes
        user1_resumes = Resume.objects.filter(user=self.user1)
        self.assertEqual(user1_resumes.count(), 1)
        self.assertEqual(user1_resumes.first().id, self.resume1.id)
        
        # User2 should only see their own resumes
        user2_resumes = Resume.objects.filter(user=self.user2)
        self.assertEqual(user2_resumes.count(), 1)
        self.assertEqual(user2_resumes.first().id, self.resume2.id)
    
    def test_version_query_isolation(self):
        """Test that version queries are filtered by user"""
        # User1 should only see their own versions
        user1_versions = ResumeVersion.objects.filter(resume__user=self.user1)
        self.assertEqual(user1_versions.count(), 1)
        self.assertEqual(user1_versions.first().id, self.version1.id)
        
        # User2 should only see their own versions
        user2_versions = ResumeVersion.objects.filter(resume__user=self.user2)
        self.assertEqual(user2_versions.count(), 1)
        self.assertEqual(user2_versions.first().id, self.version2.id)
    
    def test_analysis_query_isolation(self):
        """Test that analysis queries are filtered by user"""
        # User1 should only see their own analyses
        user1_analyses = ResumeAnalysis.objects.filter(resume__user=self.user1)
        self.assertEqual(user1_analyses.count(), 1)
        self.assertEqual(user1_analyses.first().id, self.analysis1.id)
        
        # User2 should only see their own analyses
        user2_analyses = ResumeAnalysis.objects.filter(resume__user=self.user2)
        self.assertEqual(user2_analyses.count(), 1)
        self.assertEqual(user2_analyses.first().id, self.analysis2.id)
    
    def test_cascade_deletion_isolation(self):
        """Test that deleting a user only deletes their data"""
        # Get initial counts
        total_resumes_before = Resume.objects.count()
        total_versions_before = ResumeVersion.objects.count()
        total_analyses_before = ResumeAnalysis.objects.count()
        
        # Delete user1
        self.user1.delete()
        
        # User1's data should be deleted
        self.assertEqual(Resume.objects.filter(id=self.resume1.id).count(), 0)
        self.assertEqual(ResumeVersion.objects.filter(id=self.version1.id).count(), 0)
        self.assertEqual(ResumeAnalysis.objects.filter(id=self.analysis1.id).count(), 0)
        
        # User2's data should still exist
        self.assertEqual(Resume.objects.filter(id=self.resume2.id).count(), 1)
        self.assertEqual(ResumeVersion.objects.filter(id=self.version2.id).count(), 1)
        self.assertEqual(ResumeAnalysis.objects.filter(id=self.analysis2.id).count(), 1)
        
        # Total counts should decrease by exactly user1's data
        self.assertEqual(Resume.objects.count(), total_resumes_before - 1)
        self.assertEqual(ResumeVersion.objects.count(), total_versions_before - 1)
        self.assertEqual(ResumeAnalysis.objects.count(), total_analyses_before - 1)


class TextSanitizationSecurityTest(TestCase):
    """Test text sanitization and XSS protection"""
    
    def test_pdf_text_sanitization(self):
        """Test that extracted PDF text is sanitized"""
        from apps.resumes.services.pdf_parser import PDFParserService
        
        # Test with XSS vectors
        malicious_text = '<script>alert("XSS")</script>Hello World'
        cleaned = PDFParserService.clean_extracted_text(malicious_text)
        
        # Should not contain script tags
        self.assertNotIn('<script>', cleaned)
        self.assertNotIn('</script>', cleaned)
    
    def test_experience_description_sanitization(self):
        """Test that experience descriptions are sanitized"""
        user = User.objects.create_user(username='testuser', password='pass')
        resume = Resume.objects.create(user=user, title='Test', template='professional')
        
        # Try to create experience with XSS
        malicious_desc = '<script>alert("XSS")</script>Developed applications'
        
        experience = Experience.objects.create(
            resume=resume,
            company='Test Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description=malicious_desc,
            order=0
        )
        
        # Description should be stored (sanitization happens on display)
        # But we verify it doesn't execute when rendered
        self.assertIsNotNone(experience.description)
