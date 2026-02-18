"""
Integration tests for ATS Analyzer functionality.

Tests the complete ATS analysis workflow including:
- Text aggregation from resume sections
- Keyword extraction and cleaning
- Match score calculation
- Suggestion generation
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project
from apps.analyzer.services import ATSAnalyzerService
from apps.analyzer.forms import JobDescriptionForm


class ATSAnalyzerServiceTests(TestCase):
    """Test the ATSAnalyzerService methods."""
    
    def setUp(self):
        """Set up test data."""
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
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            location='San Francisco, CA'
        )
        
        # Add experience
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date='2020-01-01',
            description='Developed Python applications using Django and PostgreSQL'
        )
        
        # Add education
        Education.objects.create(
            resume=self.resume,
            institution='University of California',
            degree='Bachelor of Science',
            field='Computer Science',
            start_year=2016,
            end_year=2020
        )
        
        # Add skills
        Skill.objects.create(resume=self.resume, name='Python', category='Technical')
        Skill.objects.create(resume=self.resume, name='Django', category='Technical')
        Skill.objects.create(resume=self.resume, name='JavaScript', category='Technical')
        
        # Add project
        Project.objects.create(
            resume=self.resume,
            name='E-commerce Platform',
            description='Built a full-stack e-commerce platform using React and Node.js',
            technologies='React, Node.js, MongoDB'
        )
    
    def test_aggregate_resume_text(self):
        """Test that resume text aggregation includes all sections."""
        text = ATSAnalyzerService.aggregate_resume_text(self.resume)
        
        # Verify all sections are included
        self.assertIn('John Doe', text)
        self.assertIn('San Francisco', text)
        self.assertIn('Tech Corp', text)
        self.assertIn('Software Engineer', text)
        self.assertIn('Python', text)
        self.assertIn('Django', text)
        self.assertIn('University of California', text)
        self.assertIn('Computer Science', text)
        self.assertIn('E-commerce Platform', text)
        self.assertIn('React', text)
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        text = "Hello, World! This is a TEST."
        cleaned = ATSAnalyzerService.clean_text(text)
        
        # Should be lowercase and tokenized
        self.assertIn('hello', cleaned)
        self.assertIn('world', cleaned)
        self.assertIn('test', cleaned)
        
        # Should not contain punctuation
        self.assertNotIn(',', ' '.join(cleaned))
        self.assertNotIn('!', ' '.join(cleaned))
    
    def test_extract_keywords(self):
        """Test keyword extraction removes stop words and short words."""
        text = "Python Django web development with PostgreSQL database at IT"
        keywords = ATSAnalyzerService.extract_keywords(text)
        
        # Should include meaningful keywords (>= 3 chars)
        self.assertIn('python', keywords)
        self.assertIn('django', keywords)
        self.assertIn('web', keywords)  # 3 chars, should be included
        self.assertIn('development', keywords)
        self.assertIn('postgresql', keywords)
        self.assertIn('database', keywords)
        
        # Should not include stop words
        self.assertNotIn('with', keywords)
        self.assertNotIn('the', keywords)
        self.assertNotIn('at', keywords)
        
        # Should not include short words (< 3 chars)
        self.assertNotIn('it', keywords)  # 2 chars, should be filtered
    
    def test_calculate_match_score_perfect_match(self):
        """Test match score calculation with perfect match."""
        resume_keywords = {'python', 'django', 'postgresql'}
        jd_keywords = {'python', 'django', 'postgresql'}
        
        result = ATSAnalyzerService.calculate_match_score(resume_keywords, jd_keywords)
        
        self.assertEqual(result['score'], 100.0)
        self.assertEqual(len(result['matched_keywords']), 3)
        self.assertEqual(len(result['missing_keywords']), 0)
    
    def test_calculate_match_score_partial_match(self):
        """Test match score calculation with partial match."""
        resume_keywords = {'python', 'django'}
        jd_keywords = {'python', 'django', 'postgresql', 'redis'}
        
        result = ATSAnalyzerService.calculate_match_score(resume_keywords, jd_keywords)
        
        self.assertEqual(result['score'], 50.0)  # 2 out of 4
        self.assertEqual(len(result['matched_keywords']), 2)
        self.assertEqual(len(result['missing_keywords']), 2)
        self.assertIn('postgresql', result['missing_keywords'])
        self.assertIn('redis', result['missing_keywords'])
    
    def test_calculate_match_score_no_match(self):
        """Test match score calculation with no match."""
        resume_keywords = {'python', 'django'}
        jd_keywords = {'java', 'spring', 'mysql'}
        
        result = ATSAnalyzerService.calculate_match_score(resume_keywords, jd_keywords)
        
        self.assertEqual(result['score'], 0.0)
        self.assertEqual(len(result['matched_keywords']), 0)
        self.assertEqual(len(result['missing_keywords']), 3)
    
    def test_calculate_match_score_empty_jd(self):
        """Test match score calculation with empty job description."""
        resume_keywords = {'python', 'django'}
        jd_keywords = set()
        
        result = ATSAnalyzerService.calculate_match_score(resume_keywords, jd_keywords)
        
        self.assertEqual(result['score'], 0.0)
    
    def test_generate_suggestions_with_missing_keywords(self):
        """Test suggestion generation with missing keywords."""
        missing_keywords = ['postgresql', 'redis', 'docker']
        suggestions = ATSAnalyzerService.generate_suggestions(missing_keywords)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Should mention missing keywords
        suggestions_text = ' '.join(suggestions).lower()
        self.assertIn('missing', suggestions_text)
    
    def test_generate_suggestions_no_missing_keywords(self):
        """Test suggestion generation with no missing keywords."""
        missing_keywords = []
        suggestions = ATSAnalyzerService.generate_suggestions(missing_keywords)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Should have positive message
        suggestions_text = ' '.join(suggestions).lower()
        self.assertIn('great', suggestions_text)
    
    def test_analyze_resume_complete_workflow(self):
        """Test complete analysis workflow."""
        job_description = """
        We are looking for a Software Engineer with experience in Python, Django,
        and PostgreSQL. The ideal candidate should have knowledge of web development,
        RESTful APIs, and database design. Experience with JavaScript and React is a plus.
        """
        
        result = ATSAnalyzerService.analyze_resume(self.resume.id, job_description)
        
        # Verify result structure
        self.assertIn('score', result)
        self.assertIn('matched_keywords', result)
        self.assertIn('missing_keywords', result)
        self.assertIn('suggestions', result)
        
        # Score should be between 0 and 100
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
        
        # Should have some matched keywords (python, django, javascript)
        self.assertGreater(len(result['matched_keywords']), 0)
        self.assertIn('python', result['matched_keywords'])
        self.assertIn('django', result['matched_keywords'])
        
        # Should have suggestions
        self.assertGreater(len(result['suggestions']), 0)


class JobDescriptionFormTests(TestCase):
    """Test the JobDescriptionForm."""
    
    def test_form_valid_with_text(self):
        """Test form is valid with job description text."""
        form = JobDescriptionForm(data={
            'job_description': 'Looking for a Python developer with Django experience.'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_empty(self):
        """Test form is invalid with empty job description."""
        form = JobDescriptionForm(data={
            'job_description': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('job_description', form.errors)
    
    def test_form_invalid_whitespace_only(self):
        """Test form is invalid with whitespace-only job description."""
        form = JobDescriptionForm(data={
            'job_description': '   \n\t   '
        })
        self.assertFalse(form.is_valid())
        self.assertIn('job_description', form.errors)
    
    def test_form_strips_whitespace(self):
        """Test form strips leading/trailing whitespace."""
        form = JobDescriptionForm(data={
            'job_description': '  Python developer needed  '
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['job_description'], 'Python developer needed')


class AnalyzerViewTests(TestCase):
    """Test the analyzer views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        
        # Add minimal data for analysis
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            location='San Francisco, CA'
        )
        
        Skill.objects.create(resume=self.resume, name='Python', category='Technical')
        Skill.objects.create(resume=self.resume, name='Django', category='Technical')
    
    def test_analyze_view_requires_login(self):
        """Test that analyze view requires authentication."""
        response = self.client.get(f'/analyzer/{self.resume.id}/analyze/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/auth/login/', response.url)
    
    def test_analyze_view_get(self):
        """Test GET request to analyze view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/analyzer/{self.resume.id}/analyze/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analyzer/analyze_new.html')
        self.assertIn('form', response.context)
        self.assertIn('resume', response.context)
        self.assertIsNone(response.context['analysis_result'])
    
    def test_analyze_view_post_valid(self):
        """Test POST request with valid job description."""
        self.client.login(username='testuser', password='testpass123')
        
        job_description = 'Looking for a Python developer with Django experience.'
        response = self.client.post(
            f'/analyzer/{self.resume.id}/analyze/',
            data={'job_description': job_description}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis_result', response.context)
        
        result = response.context['analysis_result']
        self.assertIsNotNone(result)
        self.assertIn('score', result)
        self.assertIn('matched_keywords', result)
        self.assertIn('missing_keywords', result)
        self.assertIn('suggestions', result)
    
    def test_analyze_view_post_invalid(self):
        """Test POST request with invalid (empty) job description."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            f'/analyzer/{self.resume.id}/analyze/',
            data={'job_description': ''}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['analysis_result'])
        self.assertFalse(response.context['form'].is_valid())
    
    def test_analyze_view_unauthorized_access(self):
        """Test that users cannot analyze other users' resumes."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Login as other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to access first user's resume
        response = self.client.get(f'/analyzer/{self.resume.id}/analyze/')
        
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_analyze_view_nonexistent_resume(self):
        """Test accessing analyzer with non-existent resume ID."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/analyzer/99999/analyze/')
        self.assertEqual(response.status_code, 404)
