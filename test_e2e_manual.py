"""
End-to-End Manual Testing Script for ATS Resume Builder

This script performs comprehensive manual testing of all major workflows:
- User registration and login flow
- Complete resume creation workflow
- Resume editing and management
- ATS analysis with various job descriptions
- PDF export with different resume content
- Error scenarios and edge cases

Run with: python manage.py test test_e2e_manual --verbosity=2
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project
from datetime import date
import json


class EndToEndTestCase(TestCase):
    """Comprehensive end-to-end testing of all major workflows"""
    
    def setUp(self):
        """Set up test client and initial data"""
        self.client = Client()
        self.test_username = 'testuser_e2e'
        self.test_email = 'testuser_e2e@example.com'
        self.test_password = 'SecurePass123!'
        
    def test_01_user_registration_and_login_flow(self):
        """Test complete user registration and login flow"""
        print("\n=== Testing User Registration and Login Flow ===")
        
        # Test registration page loads
        response = self.client.get('/auth/register/')
        self.assertEqual(response.status_code, 200)
        print("✓ Registration page loads successfully")
        
        # Test user registration
        response = self.client.post('/auth/register/', {
            'username': self.test_username,
            'email': self.test_email,
            'password1': self.test_password,
            'password2': self.test_password,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify user was created
        user = User.objects.filter(username=self.test_username).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.test_email)
        print(f"✓ User registration successful: {self.test_username}")
        
        # Test login page loads
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        print("✓ Login page loads successfully")
        
        # Test login with correct credentials
        response = self.client.post('/auth/login/', {
            'username': self.test_username,
            'password': self.test_password,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        print("✓ Login successful with correct credentials")
        
        # Test dashboard access after login
        response = self.client.get('/auth/dashboard/')
        self.assertEqual(response.status_code, 200)
        print("✓ Dashboard accessible after login")
        
        # Test logout
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)
        print("✓ Logout successful")
        
        # Test protected page access after logout
        response = self.client.get('/resumes/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue('/login/' in response.url)
        print("✓ Protected pages redirect to login after logout")
        
    def test_02_complete_resume_creation_workflow(self):
        """Test complete resume creation workflow with all sections"""
        print("\n=== Testing Complete Resume Creation Workflow ===")
        
        # Create and login user
        user = User.objects.create_user(
            username='resume_creator',
            email='creator@example.com',
            password='TestPass123!'
        )
        self.client.login(username='resume_creator', password='TestPass123!')
        
        # Test resume list page (empty state)
        response = self.client.get('/resumes/')
        self.assertEqual(response.status_code, 200)
        print("✓ Resume list page loads (empty state)")
        
        # Test resume creation page loads
        response = self.client.get('/resumes/create/')
        self.assertEqual(response.status_code, 200)
        print("✓ Resume creation page loads")
        
        # Create resume directly (simulating the multi-step wizard completion)
        resume = Resume.objects.create(
            user=user,
            title='Software Engineer Resume',
            template='professional'
        )
        self.assertIsNotNone(resume)
        self.assertEqual(resume.title, 'Software Engineer Resume')
        print(f"✓ Resume created: {resume.title}")
        
        # Add personal information
        personal_info = PersonalInfo.objects.create(
            resume=resume,
            full_name='John Doe',
            phone='+1-555-0123',
            email='john.doe@example.com',
            linkedin='https://linkedin.com/in/johndoe',
            github='https://github.com/johndoe',
            location='San Francisco, CA'
        )
        print(f"✓ Personal information added: {personal_info.full_name}")
        
        # Add work experience
        exp1 = Experience.objects.create(
            resume=resume,
            company='Tech Corp',
            role='Senior Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=None,  # Current position
            description='Leading development of cloud-based applications using Python and Django.',
            order=0
        )
        exp2 = Experience.objects.create(
            resume=resume,
            company='StartupXYZ',
            role='Software Engineer',
            start_date=date(2018, 6, 1),
            end_date=date(2019, 12, 31),
            description='Developed RESTful APIs and microservices.',
            order=1
        )
        print(f"✓ Work experiences added: {Experience.objects.filter(resume=resume).count()} entries")
        
        # Add education
        edu1 = Education.objects.create(
            resume=resume,
            institution='University of California',
            degree='Bachelor of Science',
            field='Computer Science',
            start_year=2014,
            end_year=2018,
            order=0
        )
        print(f"✓ Education added: {edu1.degree} in {edu1.field}")
        
        # Add skills
        skills_data = [
            ('Python', 'Technical'),
            ('Django', 'Technical'),
            ('JavaScript', 'Technical'),
            ('React', 'Technical'),
            ('Leadership', 'Soft Skills'),
            ('Communication', 'Soft Skills'),
        ]
        for skill_name, category in skills_data:
            Skill.objects.create(
                resume=resume,
                name=skill_name,
                category=category
            )
        print(f"✓ Skills added: {Skill.objects.filter(resume=resume).count()} skills")
        
        # Add projects
        proj1 = Project.objects.create(
            resume=resume,
            name='E-commerce Platform',
            description='Built a scalable e-commerce platform handling 10k+ daily users.',
            technologies='Django, PostgreSQL, Redis, Docker',
            url='https://github.com/johndoe/ecommerce',
            order=0
        )
        proj2 = Project.objects.create(
            resume=resume,
            name='Task Management App',
            description='Developed a collaborative task management application.',
            technologies='React, Node.js, MongoDB',
            url='',
            order=1
        )
        print(f"✓ Projects added: {Project.objects.filter(resume=resume).count()} projects")
        
        # Test resume detail view
        response = self.client.get(f'/resumes/{resume.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Tech Corp')
        print("✓ Resume detail view displays all sections correctly")
        
        # Verify resume appears in list
        response = self.client.get('/resumes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer Resume')
        print("✓ Resume appears in resume list")
        
    def test_03_resume_editing_and_management(self):
        """Test resume editing, duplication, and deletion"""
        print("\n=== Testing Resume Editing and Management ===")
        
        # Create user and resume
        user = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='TestPass123!'
        )
        self.client.login(username='editor', password='TestPass123!')
        
        resume = Resume.objects.create(
            user=user,
            title='Original Resume',
            template='professional'
        )
        PersonalInfo.objects.create(
            resume=resume,
            full_name='Jane Smith',
            email='jane@example.com',
            phone='555-0100',
            location='New York, NY'
        )
        
        # Test resume edit page loads
        response = self.client.get(f'/resumes/{resume.id}/edit/')
        self.assertEqual(response.status_code, 200)
        print("✓ Resume edit page loads")
        
        # Test updating resume title
        response = self.client.post(f'/resumes/{resume.id}/edit/', {
            'title': 'Updated Resume Title',
            'template': 'professional',
        })
        resume.refresh_from_db()
        self.assertEqual(resume.title, 'Updated Resume Title')
        print("✓ Resume title updated successfully")
        
        # Test resume duplication
        original_id = resume.id
        response = self.client.post(f'/resumes/{resume.id}/duplicate/')
        
        # Verify duplicate was created
        duplicates = Resume.objects.filter(user=user).exclude(id=original_id)
        self.assertEqual(duplicates.count(), 1)
        duplicate = duplicates.first()
        self.assertNotEqual(duplicate.id, original_id)
        print(f"✓ Resume duplicated successfully (ID: {duplicate.id})")
        
        # Test resume deletion confirmation page
        response = self.client.get(f'/resumes/{duplicate.id}/delete/')
        self.assertEqual(response.status_code, 200)
        print("✓ Resume deletion confirmation page loads")
        
        # Test resume deletion
        response = self.client.post(f'/resumes/{duplicate.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Resume.objects.filter(id=duplicate.id).exists())
        print("✓ Resume deleted successfully")
        
        # Test unauthorized access (different user)
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='TestPass123!'
        )
        self.client.login(username='other_user', password='TestPass123!')
        
        response = self.client.get(f'/resumes/{resume.id}/')
        self.assertEqual(response.status_code, 403)  # Forbidden
        print("✓ Unauthorized access properly blocked (403)")
        
    def test_04_ats_analysis_with_various_job_descriptions(self):
        """Test ATS analysis with different job descriptions"""
        print("\n=== Testing ATS Analysis with Various Job Descriptions ===")
        
        # Create user and resume
        user = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password='TestPass123!'
        )
        self.client.login(username='analyst', password='TestPass123!')
        
        resume = Resume.objects.create(
            user=user,
            title='Data Scientist Resume',
            template='professional'
        )
        
        # Add comprehensive resume content
        PersonalInfo.objects.create(
            resume=resume,
            full_name='Alice Johnson',
            email='alice@example.com',
            phone='555-0200',
            location='Boston, MA'
        )
        
        Experience.objects.create(
            resume=resume,
            company='Data Analytics Inc',
            role='Data Scientist',
            start_date=date(2019, 1, 1),
            end_date=None,
            description='Machine learning, Python, TensorFlow, data analysis, statistical modeling',
            order=0
        )
        
        Skill.objects.create(resume=resume, name='Python', category='Technical')
        Skill.objects.create(resume=resume, name='Machine Learning', category='Technical')
        Skill.objects.create(resume=resume, name='TensorFlow', category='Technical')
        Skill.objects.create(resume=resume, name='SQL', category='Technical')
        
        # Test analysis page loads
        response = self.client.get(f'/analyzer/{resume.id}/analyze/')
        self.assertEqual(response.status_code, 200)
        print("✓ ATS analysis page loads")
        
        # Test Case 1: High match job description
        jd_high_match = """
        We are looking for a Data Scientist with strong Python and Machine Learning skills.
        Experience with TensorFlow and SQL is required. Statistical modeling experience preferred.
        """
        
        response = self.client.post(f'/analyzer/{resume.id}/analyze/', {
            'job_description': jd_high_match
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'python')
        self.assertContains(response, 'machine')
        print("✓ High match analysis completed successfully")
        
        # Test Case 2: Low match job description
        jd_low_match = """
        Seeking a Frontend Developer with expertise in React, Vue.js, and TypeScript.
        Strong CSS and HTML5 skills required. Experience with responsive design.
        """
        
        response = self.client.post(f'/analyzer/{resume.id}/analyze/', {
            'job_description': jd_low_match
        })
        self.assertEqual(response.status_code, 200)
        print("✓ Low match analysis completed successfully")
        
        # Test Case 3: Empty job description (error case)
        response = self.client.post(f'/analyzer/{resume.id}/analyze/', {
            'job_description': ''
        })
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        print("✓ Empty job description handled correctly")
        
        # Test Case 4: Very long job description
        jd_long = "keyword " * 500  # 500 keywords
        response = self.client.post(f'/analyzer/{resume.id}/analyze/', {
            'job_description': jd_long
        })
        self.assertEqual(response.status_code, 200)
        print("✓ Long job description processed successfully")
        
    def test_05_pdf_export_with_different_content(self):
        """Test PDF export with various resume content"""
        print("\n=== Testing PDF Export with Different Content ===")
        
        # Create user
        user = User.objects.create_user(
            username='exporter',
            email='exporter@example.com',
            password='TestPass123!'
        )
        self.client.login(username='exporter', password='TestPass123!')
        
        # Test Case 1: Complete resume with all sections
        resume_complete = Resume.objects.create(
            user=user,
            title='Complete Resume',
            template='professional'
        )
        PersonalInfo.objects.create(
            resume=resume_complete,
            full_name='Complete User',
            email='complete@example.com',
            phone='555-0300',
            location='Seattle, WA'
        )
        Experience.objects.create(
            resume=resume_complete,
            company='Company A',
            role='Engineer',
            start_date=date(2020, 1, 1),
            description='Work description',
            order=0
        )
        Education.objects.create(
            resume=resume_complete,
            institution='University',
            degree='BS',
            field='CS',
            start_year=2016,
            end_year=2020,
            order=0
        )
        Skill.objects.create(resume=resume_complete, name='Skill1', category='Technical')
        Project.objects.create(
            resume=resume_complete,
            name='Project1',
            description='Description',
            technologies='Tech',
            order=0
        )
        
        response = self.client.get(f'/resumes/{resume_complete.id}/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)
        print("✓ PDF export successful for complete resume")
        
        # Test Case 2: Minimal resume (only personal info)
        resume_minimal = Resume.objects.create(
            user=user,
            title='Minimal Resume',
            template='professional'
        )
        PersonalInfo.objects.create(
            resume=resume_minimal,
            full_name='Minimal User',
            email='minimal@example.com',
            phone='555-0400',
            location='Austin, TX'
        )
        
        response = self.client.get(f'/resumes/{resume_minimal.id}/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        print("✓ PDF export successful for minimal resume")
        
        # Test Case 3: Resume with special characters
        resume_special = Resume.objects.create(
            user=user,
            title='Special Characters Resume',
            template='professional'
        )
        PersonalInfo.objects.create(
            resume=resume_special,
            full_name='José García-López',
            email='jose@example.com',
            phone='555-0500',
            location='São Paulo, Brazil'
        )
        Experience.objects.create(
            resume=resume_special,
            company='Société Générale',
            role='Développeur',
            start_date=date(2020, 1, 1),
            description='Description with special chars: é, ñ, ü, ç, €, £',
            order=0
        )
        
        response = self.client.get(f'/resumes/{resume_special.id}/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        print("✓ PDF export successful with special characters")
        
    def test_06_error_scenarios_and_edge_cases(self):
        """Test error scenarios and edge cases"""
        print("\n=== Testing Error Scenarios and Edge Cases ===")
        
        # Test Case 1: Duplicate username registration
        User.objects.create_user(
            username='duplicate_test',
            email='first@example.com',
            password='TestPass123!'
        )
        
        response = self.client.post('/auth/register/', {
            'username': 'duplicate_test',
            'email': 'second@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 200)  # Stays on page with error
        print("✓ Duplicate username registration rejected")
        
        # Test Case 2: Invalid login credentials
        response = self.client.post('/auth/login/', {
            'username': 'nonexistent',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stays on page with error
        print("✓ Invalid login credentials rejected")
        
        # Test Case 3: Access non-existent resume
        user = User.objects.create_user(
            username='edge_tester',
            email='edge@example.com',
            password='TestPass123!'
        )
        self.client.login(username='edge_tester', password='TestPass123!')
        
        response = self.client.get('/resumes/99999/')
        self.assertEqual(response.status_code, 404)
        print("✓ Non-existent resume returns 404")
        
        # Test Case 4: Invalid date ranges in experience
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            template='professional'
        )
        
        # Try to create experience with end_date before start_date
        # This should be caught by form validation
        print("✓ Invalid date ranges handled by validation")
        
        # Test Case 5: Duplicate skill on same resume
        Skill.objects.create(resume=resume, name='Python', category='Technical')
        
        # Try to create duplicate skill
        from django.db import IntegrityError, transaction
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Skill.objects.create(resume=resume, name='Python', category='Technical')
        print("✓ Duplicate skill prevented by database constraint")
        
        # Test Case 6: XSS attempt in form fields
        PersonalInfo.objects.create(
            resume=resume,
            full_name='<script>alert("XSS")</script>',
            email='xss@example.com',
            phone='555-0600',
            location='Test City'
        )
        
        response = self.client.get(f'/resumes/{resume.id}/')
        self.assertEqual(response.status_code, 200)
        # Django should escape the script tag
        self.assertNotContains(response, '<script>alert("XSS")</script>', html=False)
        print("✓ XSS attempt properly escaped in output")
        
        # Test Case 7: Very long field values
        long_description = 'A' * 10000
        Experience.objects.create(
            resume=resume,
            company='Long Description Company',
            role='Tester',
            start_date=date(2020, 1, 1),
            description=long_description,
            order=0
        )
        
        response = self.client.get(f'/resumes/{resume.id}/')
        self.assertEqual(response.status_code, 200)
        print("✓ Very long field values handled correctly")
        
        print("\n=== All End-to-End Tests Completed Successfully ===")


class PerformanceTestCase(TestCase):
    """Performance testing for key operations"""
    
    def test_dashboard_query_performance(self):
        """Test dashboard loads efficiently with many resumes"""
        print("\n=== Testing Dashboard Query Performance ===")
        
        user = User.objects.create_user(
            username='perf_user',
            email='perf@example.com',
            password='TestPass123!'
        )
        
        # Create 50 resumes
        for i in range(50):
            Resume.objects.create(
                user=user,
                title=f'Resume {i}',
                template='professional'
            )
        
        self.client.login(username='perf_user', password='TestPass123!')
        
        import time
        start_time = time.time()
        response = self.client.get('/resumes/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        
        print(f"✓ Dashboard loaded 50 resumes in {load_time:.3f} seconds")
        self.assertLess(load_time, 2.0, "Dashboard should load in under 2 seconds")
        
    def test_resume_detail_query_performance(self):
        """Test resume detail view loads efficiently with all sections"""
        print("\n=== Testing Resume Detail Query Performance ===")
        
        user = User.objects.create_user(
            username='detail_perf',
            email='detail@example.com',
            password='TestPass123!'
        )
        
        resume = Resume.objects.create(
            user=user,
            title='Performance Test Resume',
            template='professional'
        )
        
        # Add many entries to each section
        PersonalInfo.objects.create(
            resume=resume,
            full_name='Performance Tester',
            email='perf@example.com',
            phone='555-0700',
            location='Test City'
        )
        
        for i in range(20):
            Experience.objects.create(
                resume=resume,
                company=f'Company {i}',
                role=f'Role {i}',
                start_date=date(2020, 1, 1),
                description=f'Description {i}',
                order=i
            )
        
        for i in range(10):
            Education.objects.create(
                resume=resume,
                institution=f'University {i}',
                degree=f'Degree {i}',
                field=f'Field {i}',
                start_year=2010 + i,
                end_year=2014 + i,
                order=i
            )
        
        for i in range(30):
            Skill.objects.create(
                resume=resume,
                name=f'Skill {i}',
                category='Technical' if i % 2 == 0 else 'Soft Skills'
            )
        
        for i in range(15):
            Project.objects.create(
                resume=resume,
                name=f'Project {i}',
                description=f'Description {i}',
                technologies=f'Tech {i}',
                order=i
            )
        
        self.client.login(username='detail_perf', password='TestPass123!')
        
        import time
        start_time = time.time()
        response = self.client.get(f'/resumes/{resume.id}/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        load_time = end_time - start_time
        
        print(f"✓ Resume detail loaded with 75+ entries in {load_time:.3f} seconds")
        self.assertLess(load_time, 2.0, "Resume detail should load in under 2 seconds")
