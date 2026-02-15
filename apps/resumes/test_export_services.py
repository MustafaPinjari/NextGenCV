"""
Tests for enhanced export services (DOCX, Text, and version-specific exports).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project
from apps.resumes.services.docx_export_service import DOCXExportService
from apps.resumes.services.text_export_service import TextExportService
from apps.resumes.services.version_service import VersionService
from apps.resumes.pdf_service import PDFExportService
from datetime import date
import io


class DOCXExportServiceTest(TestCase):
    """Test DOCX export service functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            linkedin='https://linkedin.com/in/johndoe',
            github='https://github.com/johndoe',
            location='San Francisco, CA'
        )
        
        # Add experience
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed web applications\nImproved system performance',
            order=1
        )
        
        # Add education
        Education.objects.create(
            resume=self.resume,
            institution='University of California',
            degree='Bachelor of Science',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=1
        )
        
        # Add skills
        Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Programming Languages'
        )
        Skill.objects.create(
            resume=self.resume,
            name='Django',
            category='Frameworks'
        )
        
        # Add project
        Project.objects.create(
            resume=self.resume,
            name='Portfolio Website',
            description='Built a personal portfolio website',
            technologies='Django, PostgreSQL, React',
            url='https://example.com',
            order=1
        )
    
    def test_generate_docx_basic(self):
        """Test basic DOCX generation."""
        docx_bytes, resume = DOCXExportService.generate_docx(self.resume.id)
        
        # Verify bytes were generated
        self.assertIsNotNone(docx_bytes)
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 0)
        
        # Verify resume returned
        self.assertEqual(resume.id, self.resume.id)
    
    def test_generate_docx_with_version(self):
        """Test DOCX generation with specific version."""
        # Create a version
        version = VersionService.create_version(self.resume, modification_type='manual')
        
        # Generate DOCX for specific version
        docx_bytes, resume = DOCXExportService.generate_docx(self.resume.id, version_id=version.id)
        
        # Verify bytes were generated
        self.assertIsNotNone(docx_bytes)
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 0)


class TextExportServiceTest(TestCase):
    """Test plain text export service functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='Jane Smith',
            phone='555-5678',
            email='jane@example.com',
            location='New York, NY'
        )
        
        # Add experience
        Experience.objects.create(
            resume=self.resume,
            company='Startup Inc',
            role='Senior Developer',
            start_date=date(2021, 6, 1),
            end_date=None,
            description='Leading development team\nArchitecting scalable solutions',
            order=1
        )
    
    def test_generate_text_basic(self):
        """Test basic plain text generation."""
        text_content, resume = TextExportService.generate_text(self.resume.id)
        
        # Verify text was generated
        self.assertIsNotNone(text_content)
        self.assertIsInstance(text_content, str)
        self.assertGreater(len(text_content), 0)
        
        # Verify content includes key information
        self.assertIn('JANE SMITH', text_content)
        self.assertIn('555-5678', text_content)
        self.assertIn('WORK EXPERIENCE', text_content)
        self.assertIn('Senior Developer', text_content)
        self.assertIn('Startup Inc', text_content)
    
    def test_generate_text_with_version(self):
        """Test plain text generation with specific version."""
        # Create a version
        version = VersionService.create_version(self.resume, modification_type='manual')
        
        # Generate text for specific version
        text_content, resume = TextExportService.generate_text(self.resume.id, version_id=version.id)
        
        # Verify text was generated
        self.assertIsNotNone(text_content)
        self.assertIsInstance(text_content, str)
        self.assertGreater(len(text_content), 0)
    
    def test_text_format_ats_friendly(self):
        """Test that text format is ATS-friendly."""
        text_content, _ = TextExportService.generate_text(self.resume.id)
        
        # Verify clean formatting (no special characters that confuse ATS)
        # Should have clear section headers
        self.assertIn('WORK EXPERIENCE', text_content)
        self.assertIn('=', text_content)  # Section underlines
        
        # Should have bullet points
        self.assertIn('-', text_content)


class VersionSpecificExportTest(TestCase):
    """Test version-specific export functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='Test User',
            phone='555-0000',
            email='test@example.com',
            location='Test City'
        )
    
    def test_pdf_export_with_version(self):
        """Test PDF export with specific version."""
        # Create a version
        version = VersionService.create_version(self.resume, modification_type='manual')
        
        # Generate PDF for specific version
        pdf_bytes, resume = PDFExportService.generate_pdf(self.resume.id, version_id=version.id)
        
        # Verify PDF was generated
        self.assertIsNotNone(pdf_bytes)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
        
        # Verify it's a PDF (starts with PDF magic bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
    
    def test_export_without_version(self):
        """Test that exports work without version parameter (current version)."""
        # Generate exports without version
        pdf_bytes, _ = PDFExportService.generate_pdf(self.resume.id)
        docx_bytes, _ = DOCXExportService.generate_docx(self.resume.id)
        text_content, _ = TextExportService.generate_text(self.resume.id)
        
        # Verify all exports generated successfully
        self.assertIsNotNone(pdf_bytes)
        self.assertIsNotNone(docx_bytes)
        self.assertIsNotNone(text_content)
        
        self.assertGreater(len(pdf_bytes), 0)
        self.assertGreater(len(docx_bytes), 0)
        self.assertGreater(len(text_content), 0)
