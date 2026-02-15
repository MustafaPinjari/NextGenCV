"""
Unit tests for AnalyticsService
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.resumes.models import Resume, ResumeAnalysis, OptimizationHistory, PersonalInfo, Experience, Education, Skill
from apps.analytics.services.analytics_service import AnalyticsService
from datetime import date, timedelta


class AnalyticsServiceTest(TestCase):
    """Test cases for AnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        # Clear cache before each test
        from django.core.cache import cache
        cache.clear()
        
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
        
        # Create experience with quantified achievements
        self.experience = Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed web applications\nIncreased performance by 50%\nManaged team of 5 developers',
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
        
        # Create skills
        self.skill = Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Programming'
        )
    
    def test_calculate_resume_health_complete_resume(self):
        """Test health calculation for complete resume"""
        health = AnalyticsService.calculate_resume_health(self.resume)
        
        self.assertIsInstance(health, float)
        self.assertGreaterEqual(health, 0)
        self.assertLessEqual(health, 100)
        
        # Should have good health with all sections
        self.assertGreater(health, 50)
    
    def test_calculate_resume_health_incomplete_resume(self):
        """Test health calculation for incomplete resume"""
        # Create resume without sections
        incomplete_resume = Resume.objects.create(
            user=self.user,
            title='Incomplete Resume',
            template='professional'
        )
        
        health = AnalyticsService.calculate_resume_health(incomplete_resume)
        
        self.assertIsInstance(health, float)
        self.assertGreaterEqual(health, 0)
        self.assertLessEqual(health, 100)
        
        # Should have low health without sections
        self.assertLess(health, 50)
    
    def test_calculate_resume_health_bounds(self):
        """Test that health score is always between 0 and 100"""
        # Test with various resume states
        resumes = [self.resume]
        
        # Create minimal resume
        minimal = Resume.objects.create(
            user=self.user,
            title='Minimal',
            template='professional'
        )
        resumes.append(minimal)
        
        for resume in resumes:
            health = AnalyticsService.calculate_resume_health(resume)
            self.assertGreaterEqual(health, 0, f"Health score {health} is below 0")
            self.assertLessEqual(health, 100, f"Health score {health} is above 100")
    
    def test_get_score_trends_no_data(self):
        """Test score trends with no analyses"""
        trends = AnalyticsService.get_score_trends(self.user)
        
        self.assertEqual(trends['trend'], 'no_data')
        self.assertEqual(len(trends['scores']), 0)
        self.assertEqual(trends['improvement_rate'], 0.0)
    
    def test_get_score_trends_with_data(self):
        """Test score trends with multiple analyses"""
        # Create analyses with improving scores (in chronological order)
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        for i, score in enumerate(scores):
            ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description='Test job description',
                keyword_match_score=score,
                skill_relevance_score=score,
                section_completeness_score=score,
                experience_impact_score=score,
                quantification_score=score,
                action_verb_score=score,
                final_score=score,
                analysis_timestamp=timezone.now() + timedelta(days=i)  # Changed to + for chronological order
            )
        
        trends = AnalyticsService.get_score_trends(self.user)
        
        self.assertEqual(len(trends['scores']), 5)
        self.assertEqual(trends['scores'], scores)
        self.assertEqual(trends['trend'], 'improving')
        self.assertGreater(trends['improvement_rate'], 0)
        self.assertEqual(len(trends['moving_average']), 5)
    
    def test_get_score_trends_declining(self):
        """Test score trends with declining scores"""
        # Create analyses with declining scores (in chronological order)
        scores = [80.0, 75.0, 70.0, 65.0, 60.0]
        for i, score in enumerate(scores):
            ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description='Test job description',
                keyword_match_score=score,
                skill_relevance_score=score,
                section_completeness_score=score,
                experience_impact_score=score,
                quantification_score=score,
                action_verb_score=score,
                final_score=score,
                analysis_timestamp=timezone.now() + timedelta(days=i)  # Changed to + for chronological order
            )
        
        trends = AnalyticsService.get_score_trends(self.user)
        
        self.assertEqual(trends['trend'], 'declining')
        self.assertLess(trends['improvement_rate'], 0)
    
    def test_get_score_trends_stable(self):
        """Test score trends with stable scores"""
        # Create analyses with stable scores (in chronological order)
        scores = [70.0, 70.5, 70.2, 70.3, 70.1]
        for i, score in enumerate(scores):
            ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description='Test job description',
                keyword_match_score=score,
                skill_relevance_score=score,
                section_completeness_score=score,
                experience_impact_score=score,
                quantification_score=score,
                action_verb_score=score,
                final_score=score,
                analysis_timestamp=timezone.now() + timedelta(days=i)  # Changed to + for chronological order
            )
        
        trends = AnalyticsService.get_score_trends(self.user)
        
        self.assertEqual(trends['trend'], 'stable')
    
    def test_get_top_missing_keywords_no_data(self):
        """Test getting top missing keywords with no analyses"""
        keywords = AnalyticsService.get_top_missing_keywords(self.user)
        
        self.assertEqual(len(keywords), 0)
    
    def test_get_top_missing_keywords_with_data(self):
        """Test getting top missing keywords with analyses"""
        # Create analyses with missing keywords
        for i in range(3):
            ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description='Test job description',
                keyword_match_score=70.0,
                skill_relevance_score=70.0,
                section_completeness_score=70.0,
                experience_impact_score=70.0,
                quantification_score=70.0,
                action_verb_score=70.0,
                final_score=70.0,
                missing_keywords=['python', 'django', 'react']
            )
        
        keywords = AnalyticsService.get_top_missing_keywords(self.user, limit=5)
        
        self.assertGreater(len(keywords), 0)
        # Each keyword should appear 3 times
        for keyword, count in keywords:
            self.assertEqual(count, 3)
    
    def test_get_top_missing_keywords_frequency_order(self):
        """Test that keywords are ordered by frequency"""
        # Create analyses with different keyword frequencies
        ResumeAnalysis.objects.create(
            resume=self.resume,
            job_description='Test 1',
            keyword_match_score=70.0,
            skill_relevance_score=70.0,
            section_completeness_score=70.0,
            experience_impact_score=70.0,
            quantification_score=70.0,
            action_verb_score=70.0,
            final_score=70.0,
            missing_keywords=['python', 'django', 'react']
        )
        
        ResumeAnalysis.objects.create(
            resume=self.resume,
            job_description='Test 2',
            keyword_match_score=70.0,
            skill_relevance_score=70.0,
            section_completeness_score=70.0,
            experience_impact_score=70.0,
            quantification_score=70.0,
            action_verb_score=70.0,
            final_score=70.0,
            missing_keywords=['python', 'django']
        )
        
        ResumeAnalysis.objects.create(
            resume=self.resume,
            job_description='Test 3',
            keyword_match_score=70.0,
            skill_relevance_score=70.0,
            section_completeness_score=70.0,
            experience_impact_score=70.0,
            quantification_score=70.0,
            action_verb_score=70.0,
            final_score=70.0,
            missing_keywords=['python']
        )
        
        keywords = AnalyticsService.get_top_missing_keywords(self.user)
        
        # Python should be first (appears 3 times)
        self.assertEqual(keywords[0][0], 'python')
        self.assertEqual(keywords[0][1], 3)
        
        # Django should be second (appears 2 times)
        self.assertEqual(keywords[1][0], 'django')
        self.assertEqual(keywords[1][1], 2)
        
        # React should be third (appears 1 time)
        self.assertEqual(keywords[2][0], 'react')
        self.assertEqual(keywords[2][1], 1)
    
    def test_generate_improvement_report_no_data(self):
        """Test improvement report with no resumes"""
        # Create user with no resumes
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        report = AnalyticsService.generate_improvement_report(new_user)
        
        self.assertEqual(report['total_resumes'], 0)
        self.assertEqual(report['average_health'], 0.0)
        self.assertEqual(report['total_optimizations'], 0)
        self.assertIn('recommendations', report)
    
    def test_generate_improvement_report_with_data(self):
        """Test improvement report with resume data"""
        report = AnalyticsService.generate_improvement_report(self.user)
        
        self.assertEqual(report['total_resumes'], 1)
        self.assertGreater(report['average_health'], 0)
        self.assertIn('recommendations', report)
        self.assertGreater(len(report['recommendations']), 0)
    
    def test_generate_improvement_report_with_optimizations(self):
        """Test improvement report includes optimization data"""
        # Create optimization history
        OptimizationHistory.objects.create(
            resume=self.resume,
            job_description='Test job',
            original_score=70.0,
            optimized_score=85.0,
            improvement_delta=15.0
        )
        
        report = AnalyticsService.generate_improvement_report(self.user)
        
        self.assertEqual(report['total_optimizations'], 1)
        self.assertEqual(report['average_improvement'], 15.0)
    
    def test_moving_average_calculation(self):
        """Test moving average calculation"""
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        moving_avg = AnalyticsService._calculate_moving_average(scores, window_size=3)
        
        self.assertEqual(len(moving_avg), len(scores))
        
        # First value should be just the first score
        self.assertEqual(moving_avg[0], 60.0)
        
        # Second value should be average of first two
        self.assertEqual(moving_avg[1], 62.5)
        
        # Third value should be average of first three
        self.assertEqual(moving_avg[2], 65.0)
    
    def test_moving_average_empty_list(self):
        """Test moving average with empty list"""
        moving_avg = AnalyticsService._calculate_moving_average([], window_size=5)
        self.assertEqual(len(moving_avg), 0)
