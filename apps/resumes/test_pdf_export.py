"""
Tests for PDF export functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from .models import Resume, PersonalInfo, Experience, Education, Skill, Project
from .pdf_service import PDFExportService


class PDFExportServiceTest(TestCase):
    """Test PDF export service functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test resume with all sections
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
            location='New York, NY'
        )
        
        # Add experience
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed web applications',
            order=0
        )
        
        # Add education
        Education.objects.create(
            resume=self.resume,
            institution='University',
            degree='Bachelor of Science',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=0
        )
        
        # Add skill
        Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Technical'
        )
        
        # Add project
        Project.objects.create(
            resume=self.resume,
            name='Test Project',
            description='A test project',
            technologies='Python, Django',
            url='https://github.com/test',
            order=0
        )
    
    def test_render_resume_html(self):
        """Test HTML rendering for PDF."""
        html = PDFExportService.render_resume_html(self.resume)
        
        # Check that HTML contains key elements
        self.assertIn('John Doe', html)
        self.assertIn('Tech Corp', html)
        self.assertIn('Software Engineer', html)
        self.assertIn('University', html)
        self.assertIn('Python', html)
        self.assertIn('Test Project', html)
    
    def test_generate_pdf(self):
        """Test PDF generation."""
        pdf_bytes, resume = PDFExportService.generate_pdf(self.resume.id)
        
        # Check that PDF bytes are returned
        self.assertIsNotNone(pdf_bytes)
        self.assertIsInstance(pdf_bytes, bytes)
        
        # Check that PDF starts with PDF header
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        
        # Check that resume is returned
        self.assertEqual(resume.id, self.resume.id)
    
    def test_generate_pdf_with_minimal_data(self):
        """Test PDF generation with minimal resume data."""
        # Create minimal resume
        minimal_resume = Resume.objects.create(
            user=self.user,
            title='Minimal Resume',
            template='professional'
        )
        
        # Add only personal info
        PersonalInfo.objects.create(
            resume=minimal_resume,
            full_name='Jane Smith',
            email='jane@example.com',
            phone='',
            linkedin='',
            github='',
            location=''
        )
        
        # Generate PDF
        pdf_bytes, resume = PDFExportService.generate_pdf(minimal_resume.id)
        
        # Check that PDF is generated successfully
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
