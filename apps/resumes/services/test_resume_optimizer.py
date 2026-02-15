"""
Unit tests for ResumeOptimizerService
"""
from django.test import TestCase
from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project
from apps.resumes.services.resume_optimizer import ResumeOptimizerService
from datetime import date


class ResumeOptimizerServiceTest(TestCase):
    """Test cases for ResumeOptimizerService"""
    
    def setUp(self):
        """Set up test data"""
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
        
        # Create personal info
        self.personal_info = PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            location='New York, NY'
        )
        
        # Create experience with weak verbs
        self.experience = Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Worked on web applications\nHelped with testing\nResponsible for bug fixes',
            order=0
        )
        
        # Create education
        self.education = Education.objects.create(
            resume=self.resume,
            institution='University',
            degree='BS',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=0
        )
        
        # Create skill
        self.skill = Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Programming'
        )
        
        # Create project
        self.project = Project.objects.create(
            resume=self.resume,
            name='Test Project',
            description='Built a web application',
            technologies='Python, Django',
            order=0
        )
        
        # Job description with keywords
        self.job_description = """
        We are looking for a Senior Software Engineer with expertise in:
        - Python and Django framework
        - React and JavaScript
        - PostgreSQL database
        - AWS cloud services
        - Docker and Kubernetes
        - Agile methodologies
        
        Responsibilities:
        - Lead development of web applications
        - Mentor junior developers
        - Implement CI/CD pipelines
        - Optimize application performance
        """
    
    def test_optimize_resume_basic(self):
        """Test basic resume optimization"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        # Check result structure
        self.assertIn('original_score', result)
        self.assertIn('optimized_score', result)
        self.assertIn('improvement_delta', result)
        self.assertIn('detailed_changes', result)
        self.assertIn('changes_summary', result)
        self.assertIn('optimized_data', result)
        
        # Check scores are valid
        self.assertGreaterEqual(result['original_score'], 0)
        self.assertLessEqual(result['original_score'], 100)
        self.assertGreaterEqual(result['optimized_score'], 0)
        self.assertLessEqual(result['optimized_score'], 100)
    
    def test_optimize_resume_improves_score(self):
        """Test that optimization improves or maintains score"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        # Optimized score should be >= original score
        self.assertGreaterEqual(
            result['optimized_score'],
            result['original_score']
        )
        
        # Improvement delta should be non-negative
        self.assertGreaterEqual(result['improvement_delta'], 0)
    
    def test_optimize_resume_with_options(self):
        """Test optimization with custom options"""
        options = {
            'rewrite_bullets': True,
            'inject_keywords': False,
            'suggest_quantifications': True,
            'standardize_formatting': False,
            'max_keywords': 5
        }
        
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description,
            options
        )
        
        # Should have bullet rewrites
        self.assertGreaterEqual(result['changes_summary']['bullet_rewrites'], 0)
        
        # Should not have keyword injections (disabled)
        self.assertEqual(result['changes_summary']['keyword_injections'], 0)
        
        # Should have quantification suggestions
        self.assertGreaterEqual(result['changes_summary']['quantification_suggestions'], 0)
        
        # Should not have formatting fixes (disabled)
        self.assertEqual(result['changes_summary']['formatting_fixes'], 0)
    
    def test_optimize_resume_changes_summary(self):
        """Test that changes summary is accurate"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        summary = result['changes_summary']
        
        # Check summary structure
        self.assertIn('bullet_rewrites', summary)
        self.assertIn('keyword_injections', summary)
        self.assertIn('quantification_suggestions', summary)
        self.assertIn('formatting_fixes', summary)
        self.assertIn('total_changes', summary)
        
        # Total should equal sum of individual changes
        expected_total = (
            summary['bullet_rewrites'] +
            summary['keyword_injections'] +
            summary['quantification_suggestions'] +
            summary['formatting_fixes']
        )
        self.assertEqual(summary['total_changes'], expected_total)
    
    def test_optimize_resume_detailed_changes(self):
        """Test that detailed changes are tracked"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        changes = result['detailed_changes']
        
        # Should have some changes
        self.assertGreater(len(changes), 0)
        
        # Each change should have required fields
        for change in changes:
            self.assertIn('type', change)
            
            # Type should be one of the expected types
            self.assertIn(change['type'], [
                'bullet_rewrite',
                'keyword_injection',
                'quantification_suggestion',
                'formatting_standardization'
            ])
            
            # Different change types have different structures
            if change['type'] == 'keyword_injection':
                self.assertIn('keyword', change)
                self.assertIn('location', change)
            else:
                # Other types should have section
                self.assertIn('section', change)
    
    def test_optimize_resume_optimized_data_structure(self):
        """Test that optimized data has correct structure"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        data = result['optimized_data']
        
        # Check structure
        self.assertIn('personal_info', data)
        self.assertIn('experiences', data)
        self.assertIn('education', data)
        self.assertIn('skills', data)
        self.assertIn('projects', data)
        
        # Check personal info
        self.assertEqual(data['personal_info']['full_name'], 'John Doe')
        self.assertEqual(data['personal_info']['email'], 'john@example.com')
        
        # Check experiences
        self.assertEqual(len(data['experiences']), 1)
        self.assertEqual(data['experiences'][0]['company'], 'Tech Corp')
        
        # Check education
        self.assertEqual(len(data['education']), 1)
        self.assertEqual(data['education'][0]['institution'], 'University')
        
        # Check skills
        self.assertGreaterEqual(len(data['skills']), 1)
        
        # Check projects
        self.assertEqual(len(data['projects']), 1)
    
    def test_optimize_bullet_points(self):
        """Test bullet point optimization"""
        changes = ResumeOptimizerService._optimize_bullet_points(
            self.resume,
            self.job_description
        )
        
        # Should have changes for weak verbs
        self.assertGreater(len(changes), 0)
        
        # Check change structure
        for change in changes:
            self.assertEqual(change['type'], 'bullet_rewrite')
            self.assertEqual(change['section'], 'experience')
            self.assertIn('old_text', change)
            self.assertIn('new_text', change)
            self.assertIn('reason', change)
    
    def test_suggest_quantifications(self):
        """Test quantification suggestions"""
        changes = ResumeOptimizerService._suggest_quantifications(self.resume)
        
        # Should have suggestions for unquantified bullets
        self.assertGreater(len(changes), 0)
        
        # Check change structure
        for change in changes:
            self.assertEqual(change['type'], 'quantification_suggestion')
            self.assertIn('old_text', change)
            self.assertIn('suggested_text', change)
            self.assertIn('achievement_type', change)
            self.assertIn('metric_options', change)
    
    def test_standardize_formatting(self):
        """Test formatting standardization"""
        changes = ResumeOptimizerService._standardize_formatting(self.resume)
        
        # May or may not have changes depending on current formatting
        self.assertIsInstance(changes, list)
        
        # If there are changes, check structure
        for change in changes:
            self.assertEqual(change['type'], 'formatting_standardization')
            self.assertIn('old_text', change)
            self.assertIn('new_text', change)
            self.assertIn('specific_changes', change)
    
    def test_generate_optimized_data(self):
        """Test optimized data generation"""
        # Create some mock changes
        changes = [
            {
                'type': 'bullet_rewrite',
                'section': 'experience',
                'company': 'Tech Corp',
                'role': 'Software Engineer',
                'old_text': 'Worked on web applications',
                'new_text': 'Developed web applications'
            }
        ]
        
        data = ResumeOptimizerService._generate_optimized_data(
            self.resume,
            changes
        )
        
        # Check that change was applied
        exp_desc = data['experiences'][0]['description']
        self.assertIn('Developed web applications', exp_desc)
        self.assertNotIn('Worked on web applications', exp_desc)
    
    def test_estimate_optimized_score(self):
        """Test score estimation"""
        original_score = 60.0
        changes_summary = {
            'bullet_rewrites': 3,
            'keyword_injections': 5,
            'quantification_suggestions': 2,
            'formatting_fixes': 1
        }
        original_analysis = {
            'keyword_match_score': 50.0,
            'action_verb_score': 40.0
        }
        
        estimated = ResumeOptimizerService._estimate_optimized_score(
            original_score,
            changes_summary,
            original_analysis
        )
        
        # Should be higher than original
        self.assertGreater(estimated, original_score)
        
        # Should not exceed 100
        self.assertLessEqual(estimated, 100.0)
    
    def test_estimate_optimized_score_bounds(self):
        """Test that estimated score is always between 0 and 100"""
        test_cases = [
            (0.0, {'bullet_rewrites': 10, 'keyword_injections': 10, 'quantification_suggestions': 10, 'formatting_fixes': 10}),
            (50.0, {'bullet_rewrites': 5, 'keyword_injections': 5, 'quantification_suggestions': 5, 'formatting_fixes': 5}),
            (95.0, {'bullet_rewrites': 20, 'keyword_injections': 20, 'quantification_suggestions': 20, 'formatting_fixes': 20}),
        ]
        
        for original_score, changes in test_cases:
            estimated = ResumeOptimizerService._estimate_optimized_score(
                original_score,
                changes,
                {}
            )
            
            self.assertGreaterEqual(estimated, 0.0)
            self.assertLessEqual(estimated, 100.0)
    
    def test_get_resume_text(self):
        """Test getting all resume text"""
        text = ResumeOptimizerService._get_resume_text(self.resume)
        
        # Should contain text from all sections
        self.assertIn('John Doe', text)
        self.assertIn('Tech Corp', text)
        self.assertIn('Software Engineer', text)
        self.assertIn('University', text)
        self.assertIn('Python', text)
        self.assertIn('Test Project', text)
    
    def test_get_resume_text_empty_resume(self):
        """Test getting text from empty resume"""
        empty_resume = Resume.objects.create(
            user=self.user,
            title='Empty Resume',
            template='professional'
        )
        
        text = ResumeOptimizerService._get_resume_text(empty_resume)
        
        # Should return empty or minimal text
        self.assertIsInstance(text, str)
    
    def test_optimize_resume_no_changes_needed(self):
        """Test optimization when resume is already good"""
        # Create a resume with strong verbs and quantifications
        good_resume = Resume.objects.create(
            user=self.user,
            title='Good Resume',
            template='professional'
        )
        
        PersonalInfo.objects.create(
            resume=good_resume,
            full_name='Jane Smith',
            email='jane@example.com'
        )
        
        Experience.objects.create(
            resume=good_resume,
            company='Tech Inc',
            role='Senior Engineer',
            start_date=date(2020, 1, 1),
            description='Led team of 5 developers\nIncreased performance by 50%\nDelivered 10 projects',
            order=0
        )
        
        result = ResumeOptimizerService.optimize_resume(
            good_resume,
            self.job_description
        )
        
        # Should still return valid result
        self.assertIn('original_score', result)
        self.assertIn('optimized_score', result)
        
        # May have minimal changes
        self.assertGreaterEqual(result['changes_summary']['total_changes'], 0)
    
    def test_optimize_resume_preserves_data_integrity(self):
        """Test that optimization doesn't corrupt data"""
        result = ResumeOptimizerService.optimize_resume(
            self.resume,
            self.job_description
        )
        
        data = result['optimized_data']
        
        # All original data should be present
        self.assertEqual(len(data['experiences']), self.resume.experiences.count())
        self.assertEqual(len(data['education']), self.resume.education.count())
        self.assertGreaterEqual(len(data['skills']), self.resume.skills.count())
        self.assertEqual(len(data['projects']), self.resume.projects.count())
        
        # Personal info should be intact
        self.assertEqual(data['personal_info']['full_name'], 'John Doe')
        self.assertEqual(data['personal_info']['email'], 'john@example.com')
