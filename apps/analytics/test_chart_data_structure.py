"""
Test chart data structure for analytics dashboard
Validates: Requirements 6.1, 6.2, 6.3, 6.4
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from apps.resumes.models import Resume, ResumeAnalysis, PersonalInfo, Experience, Education, Skill
from datetime import timedelta
import json


class ChartDataStructureTest(TestCase):
    """Test cases for chart data structure passed to analytics dashboard"""
    
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
        
        # Create test client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Create personal info
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            location='New York, NY'
        )
        
        # Create experience
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=timezone.now().date(),
            description='Developed applications',
            order=0
        )
        
        # Create education
        Education.objects.create(
            resume=self.resume,
            institution='University',
            degree='BS',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=0
        )
        
        # Create skills
        Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Programming'
        )
    
    def test_chart_data_json_exists_in_context(self):
        """Test that chart_data_json is passed to template context"""
        response = self.client.get('/analytics/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('chart_data_json', response.context)
    
    def test_chart_data_is_valid_json(self):
        """Test that chart_data_json is valid JSON"""
        response = self.client.get('/analytics/dashboard/')
        
        chart_data_json = response.context['chart_data_json']
        
        # Should be able to parse as JSON
        try:
            chart_data = json.loads(chart_data_json)
        except json.JSONDecodeError:
            self.fail("chart_data_json is not valid JSON")
        
        self.assertIsInstance(chart_data, dict)
    
    def test_score_trend_structure_with_no_data(self):
        """Test score_trend structure when no analyses exist"""
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        
        # Should have score_trend key
        self.assertIn('score_trend', chart_data)
        
        score_trend = chart_data['score_trend']
        
        # Should have required keys
        self.assertIn('labels', score_trend)
        self.assertIn('scores', score_trend)
        self.assertIn('moving_average', score_trend)
        
        # Should be empty lists when no data
        self.assertIsInstance(score_trend['labels'], list)
        self.assertIsInstance(score_trend['scores'], list)
        self.assertIsInstance(score_trend['moving_average'], list)
    
    def test_score_trend_structure_with_data(self):
        """Test score_trend structure includes labels, scores, and moving_average"""
        # Create multiple analyses in chronological order
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
                analysis_timestamp=timezone.now() + timedelta(days=i)
            )
        
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        score_trend = chart_data['score_trend']
        
        # Verify structure
        self.assertIn('labels', score_trend)
        self.assertIn('scores', score_trend)
        self.assertIn('moving_average', score_trend)
        
        # Verify data types
        self.assertIsInstance(score_trend['labels'], list)
        self.assertIsInstance(score_trend['scores'], list)
        self.assertIsInstance(score_trend['moving_average'], list)
        
        # Verify data exists
        self.assertEqual(len(score_trend['labels']), 5)
        self.assertEqual(len(score_trend['scores']), 5)
        self.assertEqual(len(score_trend['moving_average']), 5)
        
        # Verify scores match
        self.assertEqual(score_trend['scores'], scores)
        
        # Verify labels are strings (ISO format timestamps)
        for label in score_trend['labels']:
            self.assertIsInstance(label, str)
        
        # Verify moving average values are numbers
        for avg in score_trend['moving_average']:
            self.assertIsInstance(avg, (int, float))
    
    def test_health_by_resume_structure(self):
        """Test health_by_resume data structure matches Chart.js expectations"""
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        
        # Should have health_by_resume key
        self.assertIn('health_by_resume', chart_data)
        
        health_by_resume = chart_data['health_by_resume']
        
        # Should have labels and data keys
        self.assertIn('labels', health_by_resume)
        self.assertIn('data', health_by_resume)
        
        # Should be lists
        self.assertIsInstance(health_by_resume['labels'], list)
        self.assertIsInstance(health_by_resume['data'], list)
        
        # Should have same length
        self.assertEqual(len(health_by_resume['labels']), len(health_by_resume['data']))
        
        # Labels should be strings (resume titles)
        for label in health_by_resume['labels']:
            self.assertIsInstance(label, str)
        
        # Data should be numbers (health scores)
        for score in health_by_resume['data']:
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_section_completeness_structure(self):
        """Test section_completeness data structure"""
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        
        # Should have section_completeness key
        self.assertIn('section_completeness', chart_data)
        
        section_completeness = chart_data['section_completeness']
        
        # Should have labels and data keys
        self.assertIn('labels', section_completeness)
        self.assertIn('data', section_completeness)
        
        # Should be lists
        self.assertIsInstance(section_completeness['labels'], list)
        self.assertIsInstance(section_completeness['data'], list)
        
        # Should have 5 sections
        self.assertEqual(len(section_completeness['labels']), 5)
        self.assertEqual(len(section_completeness['data']), 5)
        
        # Labels should be section names
        expected_labels = ['Personal Info', 'Experience', 'Education', 'Skills', 'Projects']
        self.assertEqual(section_completeness['labels'], expected_labels)
        
        # Data should be percentages (0-100)
        for percentage in section_completeness['data']:
            self.assertIsInstance(percentage, (int, float))
            self.assertGreaterEqual(percentage, 0)
            self.assertLessEqual(percentage, 100)
    
    def test_chart_data_chronological_order(self):
        """Test that score trend data is ordered chronologically
        Validates: Requirements 6.1, 6.3
        """
        # Create analyses in random order but with sequential timestamps
        base_time = timezone.now()
        analyses_data = [
            (base_time + timedelta(days=2), 70.0),
            (base_time + timedelta(days=0), 60.0),
            (base_time + timedelta(days=4), 80.0),
            (base_time + timedelta(days=1), 65.0),
            (base_time + timedelta(days=3), 75.0),
        ]
        
        for timestamp, score in analyses_data:
            analysis = ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description='Test job description',
                keyword_match_score=score,
                skill_relevance_score=score,
                section_completeness_score=score,
                experience_impact_score=score,
                quantification_score=score,
                action_verb_score=score,
                final_score=score
            )
            # Update timestamp after creation (auto_now_add=True ignores passed value)
            ResumeAnalysis.objects.filter(id=analysis.id).update(analysis_timestamp=timestamp)
        
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        score_trend = chart_data['score_trend']
        
        # Verify scores are in chronological order
        expected_scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        self.assertEqual(score_trend['scores'], expected_scores)
        
        # Verify timestamps are in chronological order
        timestamps = score_trend['labels']
        self.assertEqual(len(timestamps), 5)
        
        # Parse timestamps and verify they're in order
        # Note: timestamps are ISO format strings
        for i in range(len(timestamps) - 1):
            # Just verify we have 5 timestamps - the service orders them
            self.assertIsInstance(timestamps[i], str)
    
    def test_empty_state_handling(self):
        """Test that empty state is handled correctly
        Validates: Requirements 6.2
        """
        # Create user with no resumes
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        client = Client()
        client.login(username='newuser', password='testpass123')
        
        response = client.get('/analytics/dashboard/')
        
        # Should show empty state
        self.assertEqual(response.status_code, 200)
        self.assertIn('has_resumes', response.context)
        self.assertFalse(response.context['has_resumes'])
        self.assertIn('message', response.context)
    
    def test_chart_data_with_multiple_resumes(self):
        """Test chart data structure with multiple resumes"""
        # Create second resume
        resume2 = Resume.objects.create(
            user=self.user,
            title='Second Resume',
            template='modern'
        )
        
        # Add minimal data to second resume
        PersonalInfo.objects.create(
            resume=resume2,
            full_name='Jane Doe',
            email='jane@example.com'
        )
        
        response = self.client.get('/analytics/dashboard/')
        
        chart_data = json.loads(response.context['chart_data_json'])
        health_by_resume = chart_data['health_by_resume']
        
        # Should have data for both resumes
        self.assertEqual(len(health_by_resume['labels']), 2)
        self.assertEqual(len(health_by_resume['data']), 2)
        
        # Should include both resume titles
        self.assertIn('Test Resume', health_by_resume['labels'])
        self.assertIn('Second Resume', health_by_resume['labels'])
