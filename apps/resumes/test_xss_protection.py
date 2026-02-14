"""
Tests for XSS protection in forms.

Validates: Requirements 14.4
"""
from django.test import TestCase
from django.contrib.auth.models import User
from apps.resumes.forms import (
    ResumeForm, PersonalInfoForm, ExperienceForm,
    EducationForm, SkillForm, ProjectForm
)
from apps.resumes.models import Resume
from apps.analyzer.forms import JobDescriptionForm
from datetime import date


class XSSProtectionTestCase(TestCase):
    """Test XSS protection across all forms."""
    
    def setUp(self):
        """Set up test user and resume."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
    
    def test_resume_form_xss_protection(self):
        """Test that ResumeForm sanitizes XSS payloads in title."""
        xss_payload = '<script>alert("XSS")</script>Test Title'
        form = ResumeForm(data={
            'title': xss_payload,
            'template': 'professional'
        })
        
        self.assertTrue(form.is_valid())
        cleaned_title = form.cleaned_data['title']
        # Script tags should be removed
        self.assertNotIn('<script>', cleaned_title)
        self.assertNotIn('</script>', cleaned_title)
        self.assertIn('Test Title', cleaned_title)
    
    def test_personal_info_form_xss_protection(self):
        """Test that PersonalInfoForm sanitizes XSS payloads."""
        xss_payload = '<img src=x onerror=alert("XSS")>John Doe'
        form = PersonalInfoForm(data={
            'full_name': xss_payload,
            'email': 'john@example.com',
            'phone': '555-1234',
            'location': 'Test City'
        })
        
        self.assertTrue(form.is_valid())
        cleaned_name = form.cleaned_data['full_name']
        # Malicious tags should be escaped or removed
        # bleach escapes tags, so check that they cannot execute
        self.assertNotIn('<img', cleaned_name)  # Tag should be escaped
        self.assertIn('John Doe', cleaned_name)
    
    def test_experience_form_xss_protection(self):
        """Test that ExperienceForm sanitizes XSS payloads."""
        xss_payload = '<script>alert("XSS")</script>Acme Corp'
        form = ExperienceForm(data={
            'company': xss_payload,
            'role': 'Developer',
            'start_date': date(2020, 1, 1),
            'description': 'Test description'
        })
        
        self.assertTrue(form.is_valid())
        cleaned_company = form.cleaned_data['company']
        # Script tags should be removed
        self.assertNotIn('<script>', cleaned_company)
        self.assertIn('Acme Corp', cleaned_company)
    
    def test_education_form_xss_protection(self):
        """Test that EducationForm sanitizes XSS payloads."""
        xss_payload = '<iframe src="evil.com"></iframe>MIT'
        form = EducationForm(data={
            'institution': xss_payload,
            'degree': 'BS',
            'field': 'Computer Science',
            'start_year': 2018,
            'end_year': 2022
        })
        
        self.assertTrue(form.is_valid())
        cleaned_institution = form.cleaned_data['institution']
        # Iframe tags should be removed
        self.assertNotIn('<iframe', cleaned_institution)
        self.assertIn('MIT', cleaned_institution)
    
    def test_skill_form_xss_protection(self):
        """Test that SkillForm sanitizes XSS payloads."""
        xss_payload = '<svg onload=alert("XSS")>Python'
        form = SkillForm(data={
            'name': xss_payload,
            'category': 'Technical'
        }, resume=self.resume)
        
        self.assertTrue(form.is_valid())
        cleaned_name = form.cleaned_data['name']
        # SVG tags should be escaped or removed
        self.assertNotIn('<svg', cleaned_name)  # Tag should be escaped
        self.assertIn('Python', cleaned_name)
    
    def test_project_form_xss_protection(self):
        """Test that ProjectForm sanitizes XSS payloads."""
        xss_payload = '<script>document.cookie</script>My Project'
        form = ProjectForm(data={
            'name': xss_payload,
            'description': 'Test description',
            'technologies': 'Python, Django',
            'url': ''
        })
        
        self.assertTrue(form.is_valid())
        cleaned_name = form.cleaned_data['name']
        # Script tags should be removed
        self.assertNotIn('<script>', cleaned_name)
        self.assertIn('My Project', cleaned_name)
    
    def test_job_description_form_xss_protection(self):
        """Test that JobDescriptionForm sanitizes XSS payloads."""
        xss_payload = '<script>alert("XSS")</script>Looking for a developer with Python skills.'
        form = JobDescriptionForm(data={
            'job_description': xss_payload
        })
        
        self.assertTrue(form.is_valid())
        cleaned_jd = form.cleaned_data['job_description']
        # Script tags should be removed
        self.assertNotIn('<script>', cleaned_jd)
        self.assertIn('Looking for a developer', cleaned_jd)
    
    def test_multiple_xss_vectors(self):
        """Test protection against multiple XSS attack vectors."""
        xss_vectors = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '<iframe src="javascript:alert(1)">',
            '<body onload=alert(1)>',
            '<input onfocus=alert(1) autofocus>',
            '<select onfocus=alert(1) autofocus>',
            '<textarea onfocus=alert(1) autofocus>',
            '<marquee onstart=alert(1)>',
            '<div style="background:url(javascript:alert(1))">',
        ]
        
        for vector in xss_vectors:
            form = ResumeForm(data={
                'title': f'{vector}Test',
                'template': 'professional'
            })
            
            if form.is_valid():
                cleaned_title = form.cleaned_data['title']
                # Ensure no executable script tags remain (they should be escaped)
                self.assertNotIn('<script>', cleaned_title)
                self.assertNotIn('<img', cleaned_title)
                self.assertNotIn('<svg', cleaned_title)
                self.assertNotIn('<iframe', cleaned_title)
                self.assertNotIn('<body', cleaned_title)
                self.assertNotIn('<input', cleaned_title)
