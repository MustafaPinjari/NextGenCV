"""
Integration tests for Version and Analytics services working together
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.resumes.models import Resume, ResumeAnalysis, PersonalInfo, Experience, Education, Skill
from apps.resumes.services import VersionService
from apps.analytics.services import AnalyticsService, TrendAnalysisService
from datetime import date, timedelta


class VersionAnalyticsIntegrationTest(TestCase):
    """Test integration between versioning and analytics services"""
    
    def setUp(self):
        """Set up test data"""
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
        
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            phone='555-1234',
            email='john@example.com',
            location='New York, NY'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed applications\nIncreased performance by 50%',
            order=0
        )
        
        Education.objects.create(
            resume=self.resume,
            institution='University',
            degree='BS',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=0
        )
        
        Skill.objects.create(
            resume=self.resume,
            name='Python',
            category='Programming'
        )
    
    def test_version_creation_with_health_score(self):
        """Test creating versions and tracking health scores"""
        # Calculate initial health
        initial_health = AnalyticsService.calculate_resume_health(self.resume)
        
        # Create version with health as ATS score
        version1 = VersionService.create_version(
            self.resume,
            modification_type='manual',
            ats_score=initial_health
        )
        
        self.assertEqual(version1.ats_score, initial_health)
        self.assertEqual(version1.version_number, 1)
        
        # Modify resume (add more content)
        Skill.objects.create(
            resume=self.resume,
            name='Django',
            category='Framework'
        )
        
        # Calculate new health
        new_health = AnalyticsService.calculate_resume_health(self.resume)
        
        # Create new version
        version2 = VersionService.create_version(
            self.resume,
            modification_type='manual',
            ats_score=new_health
        )
        
        # Health should improve with more content
        self.assertGreaterEqual(version2.ats_score, version1.ats_score)
    
    def test_analytics_with_multiple_versions(self):
        """Test analytics across multiple resume versions"""
        # Create multiple versions with different scores
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        for i, score in enumerate(scores):
            # Create analysis
            ResumeAnalysis.objects.create(
                resume=self.resume,
                job_description=f'Job description {i}',
                keyword_match_score=score,
                skill_relevance_score=score,
                section_completeness_score=score,
                experience_impact_score=score,
                quantification_score=score,
                action_verb_score=score,
                final_score=score,
                analysis_timestamp=timezone.now() - timedelta(days=len(scores) - i)
            )
            
            # Create version with score
            VersionService.create_version(
                self.resume,
                modification_type='optimized',
                ats_score=score
            )
        
        # Get trends
        trends = AnalyticsService.get_score_trends(self.user)
        
        self.assertEqual(len(trends['scores']), 5)
        self.assertEqual(trends['trend'], 'improving')
        
        # Get version history
        history = VersionService.get_version_history(self.resume)
        
        self.assertEqual(len(history), 5)
        # Verify scores are stored in versions
        for version in history:
            self.assertIsNotNone(version.ats_score)
    
    def test_trend_analysis_on_version_scores(self):
        """Test trend analysis on version ATS scores"""
        # Create versions with improving scores
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        for score in scores:
            VersionService.create_version(
                self.resume,
                modification_type='manual',
                ats_score=score
            )
        
        # Get version history
        history = VersionService.get_version_history(self.resume)
        version_scores = [v.ats_score for v in reversed(history)]
        
        # Analyze trend
        trend_summary = TrendAnalysisService.get_trend_summary(version_scores)
        
        self.assertEqual(trend_summary['direction'], 'improving')
        self.assertGreater(trend_summary['improvement_rate'], 0)
        self.assertGreater(trend_summary['trend_strength'], 0.9)
    
    def test_improvement_report_includes_versions(self):
        """Test that improvement report considers version data"""
        # Create some versions
        for i in range(3):
            VersionService.create_version(
                self.resume,
                modification_type='manual'
            )
        
        # Generate report
        report = AnalyticsService.generate_improvement_report(self.user)
        
        self.assertEqual(report['total_resumes'], 1)
        self.assertGreater(report['average_health'], 0)
        
        # Verify versions exist
        history = VersionService.get_version_history(self.resume)
        self.assertEqual(len(history), 3)
    
    def test_compare_versions_with_health_changes(self):
        """Test comparing versions shows health improvements"""
        # Create initial version
        initial_health = AnalyticsService.calculate_resume_health(self.resume)
        v1 = VersionService.create_version(
            self.resume,
            ats_score=initial_health
        )
        
        # Add more skills
        Skill.objects.create(resume=self.resume, name='Django', category='Framework')
        Skill.objects.create(resume=self.resume, name='React', category='Frontend')
        
        # Create new version
        new_health = AnalyticsService.calculate_resume_health(self.resume)
        v2 = VersionService.create_version(
            self.resume,
            ats_score=new_health
        )
        
        # Compare versions
        diff = VersionService.compare_versions(v1, v2)
        
        # Should show skill additions
        skill_changes = [c for c in diff['changes'] if c['section'] == 'skills']
        self.assertGreater(len(skill_changes), 0)
        
        # Health should be the same or better (adding skills doesn't hurt)
        self.assertGreaterEqual(v2.ats_score, v1.ats_score)
