"""
Integration tests for complete workflows in NextGenCV v2.0.

Tests end-to-end flows for:
- Resume optimization workflow
- Version management workflow
- Analytics dashboard workflow
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from apps.resumes.models import (
    Resume, PersonalInfo, Experience, Education, Skill, Project,
    ResumeVersion, ResumeAnalysis, OptimizationHistory
)
from datetime import date, timedelta


class OptimizationFlowIntegrationTest(TestCase):
    """Test complete optimization workflow end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create resume with weak content
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            email='john@example.com',
            phone='555-1234',
            location='New York, NY'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Worked on projects\nHelped with development\nDid some coding',
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
        
        self.job_description = """
        We are looking for a Senior Software Engineer with:
        - Python and Django expertise
        - React and JavaScript skills
        - PostgreSQL database experience
        - AWS cloud services knowledge
        - Docker and Kubernetes experience
        
        Responsibilities:
        - Lead development of web applications
        - Mentor junior developers
        - Implement CI/CD pipelines
        """ * 2  # Make it long enough
        
        # Login
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_optimization_flow(self):
        """Test complete optimization workflow from start to finish"""
        # Step 1: Access fix resume page
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Submit job description
        response = self.client.post(url, {
            'job_description': self.job_description
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('fix/preview', response.url)
        
        # Step 3: View optimization preview
        preview_url = reverse('fix_preview', kwargs={'pk': self.resume.id})
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)
        
        # Check that optimization results are in context
        self.assertIn('optimization_results', response.context)
        results = response.context['optimization_results']
        self.assertIn('original_score', results)
        self.assertIn('optimized_score', results)
        self.assertIn('improvement_delta', results)
        self.assertIn('detailed_changes', results)
        
        # Step 4: Accept optimization
        accept_url = reverse('fix_accept', kwargs={'pk': self.resume.id})
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Verify optimization was saved
        # Check that a new version was created
        versions = ResumeVersion.objects.filter(resume=self.resume)
        self.assertGreater(versions.count(), 0)
        
        # Check that optimization history was created
        history = OptimizationHistory.objects.filter(resume=self.resume)
        self.assertEqual(history.count(), 1)
        
        opt_record = history.first()
        self.assertIsNotNone(opt_record.original_score)
        self.assertIsNotNone(opt_record.optimized_score)
        self.assertGreaterEqual(opt_record.improvement_delta, 0)
    
    def test_optimization_flow_reject(self):
        """Test rejecting optimization changes"""
        # Submit job description
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        self.client.post(url, {'job_description': self.job_description})
        
        # View preview
        preview_url = reverse('fix_preview', kwargs={'pk': self.resume.id})
        self.client.get(preview_url)
        
        # Reject changes
        reject_url = reverse('fix_reject', kwargs={'pk': self.resume.id})
        response = self.client.post(reject_url)
        self.assertEqual(response.status_code, 302)
        
        # Verify no optimization history was created
        history = OptimizationHistory.objects.filter(resume=self.resume)
        self.assertEqual(history.count(), 0)
        
        # Verify no new version was created
        versions = ResumeVersion.objects.filter(resume=self.resume)
        self.assertEqual(versions.count(), 0)


class VersionManagementFlowIntegrationTest(TestCase):
    """Test complete version management workflow end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            email='john@example.com'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description='Original description',
            order=0
        )
        
        # Create multiple versions
        from apps.resumes.services.version_service import VersionService
        self.version1 = VersionService.create_version(self.resume, ats_score=70.0)
        
        # Modify resume
        self.resume.title = 'Updated Resume'
        self.resume.save()
        self.version2 = VersionService.create_version(self.resume, ats_score=75.0)
        
        # Modify again
        self.resume.title = 'Final Resume'
        self.resume.save()
        self.version3 = VersionService.create_version(self.resume, ats_score=80.0)
        
        # Login
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_version_management_flow(self):
        """Test complete version management workflow"""
        # Step 1: View version list
        url = reverse('version_list', kwargs={'pk': self.resume.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check all versions are displayed
        self.assertIn('versions', response.context)
        versions = response.context['versions']
        self.assertEqual(len(versions), 3)
        
        # Step 2: View specific version detail
        url = reverse('version_detail', kwargs={
            'pk': self.resume.id,
            'version_id': self.version1.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('version', response.context)
        
        # Step 3: Compare two versions
        url = reverse('version_compare', kwargs={'pk': self.resume.id})
        response = self.client.get(url, {
            'v1': self.version1.id,
            'v2': self.version3.id
        })
        self.assertEqual(response.status_code, 200)
        
        # Check comparison data
        self.assertIn('version1', response.context)
        self.assertIn('version2', response.context)
        self.assertIn('diff', response.context)
        
        diff = response.context['diff']
        self.assertIn('changes', diff)
        self.assertGreater(len(diff['changes']), 0)
        
        # Step 4: Restore old version
        url = reverse('version_restore', kwargs={
            'pk': self.resume.id,
            'version_id': self.version1.id
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        # Verify new version was created
        versions = ResumeVersion.objects.filter(resume=self.resume)
        self.assertEqual(versions.count(), 4)
        
        # Verify latest version is marked as restored
        latest = versions.order_by('-version_number').first()
        self.assertEqual(latest.modification_type, 'restored')


class AnalyticsDashboardFlowIntegrationTest(TestCase):
    """Test complete analytics dashboard workflow end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        PersonalInfo.objects.create(
            resume=self.resume,
            full_name='John Doe',
            email='john@example.com',
            phone='555-1234',
            location='New York, NY'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description='Led team of 5 developers\nIncreased performance by 50%\nDelivered 10 projects',
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
        
        # Create multiple analyses with improving scores
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
                missing_keywords=['docker', 'kubernetes', 'aws'],
                analysis_timestamp=timezone.now() + timedelta(days=i)
            )
        
        # Create optimization history
        OptimizationHistory.objects.create(
            resume=self.resume,
            job_description='Test job',
            original_score=70.0,
            optimized_score=85.0,
            improvement_delta=15.0
        )
        
        # Login
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_analytics_dashboard_flow(self):
        """Test complete analytics dashboard workflow"""
        # Step 1: Access analytics dashboard
        url = reverse('analytics_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check dashboard data
        self.assertIn('resume_health', response.context)
        self.assertIn('score_trends', response.context)
        self.assertIn('top_missing_keywords', response.context)
        
        # Verify resume health is calculated
        health = response.context['resume_health']
        self.assertGreater(health, 0)
        self.assertLessEqual(health, 100)
        
        # Verify score trends are present
        trends = response.context['score_trends']
        self.assertIn('scores', trends)
        self.assertIn('trend', trends)
        self.assertEqual(len(trends['scores']), 5)
        
        # Verify missing keywords are present
        keywords = response.context['top_missing_keywords']
        self.assertGreater(len(keywords), 0)
        
        # Step 2: Access trends page
        url = reverse('analytics_trends')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check trends data
        self.assertIn('trends', response.context)
        
        # Step 3: Access improvement report
        url = reverse('improvement_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check report data
        self.assertIn('report', response.context)
        report = response.context['report']
        
        self.assertIn('total_resumes', report)
        self.assertIn('average_health', report)
        self.assertIn('total_optimizations', report)
        self.assertIn('recommendations', report)
        
        # Verify optimization data is included
        self.assertEqual(report['total_optimizations'], 1)
        self.assertEqual(report['average_improvement'], 15.0)
    
    def test_analytics_dashboard_with_no_data(self):
        """Test analytics dashboard with user who has no data"""
        # Create new user with no resumes
        new_user = User.objects.create_user(
            username='newuser',
            password='testpass123'
        )
        
        # Login as new user
        self.client.logout()
        self.client.login(username='newuser', password='testpass123')
        
        # Access dashboard
        url = reverse('analytics_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Should handle empty data gracefully
        self.assertIn('score_trends', response.context)
        trends = response.context['score_trends']
        self.assertEqual(trends['trend'], 'no_data')
        self.assertEqual(len(trends['scores']), 0)


class CrossModuleIntegrationTest(TestCase):
    """Test integration between multiple modules"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
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
            email='john@example.com'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description='Worked on projects',
            order=0
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_optimization_creates_version_and_analysis(self):
        """Test that optimization creates both version and analysis records"""
        from apps.resumes.services.version_service import VersionService
        
        # Create initial version
        initial_version = VersionService.create_version(self.resume)
        
        # Run optimization
        job_description = "Python Django developer with React experience. " * 10
        
        url = reverse('fix_resume', kwargs={'pk': self.resume.id})
        self.client.post(url, {'job_description': job_description})
        
        preview_url = reverse('fix_preview', kwargs={'pk': self.resume.id})
        self.client.get(preview_url)
        
        accept_url = reverse('fix_accept', kwargs={'pk': self.resume.id})
        self.client.post(accept_url)
        
        # Verify version was created
        versions = ResumeVersion.objects.filter(resume=self.resume)
        self.assertGreater(versions.count(), 1)
        
        # Verify optimization history exists
        history = OptimizationHistory.objects.filter(resume=self.resume)
        self.assertEqual(history.count(), 1)
        
        # Verify scores are recorded
        opt_record = history.first()
        self.assertIsNotNone(opt_record.original_score)
        self.assertIsNotNone(opt_record.optimized_score)
    
    def test_version_restore_updates_analytics(self):
        """Test that restoring a version is reflected in analytics"""
        from apps.resumes.services.version_service import VersionService
        
        # Create versions
        v1 = VersionService.create_version(self.resume, ats_score=70.0)
        
        self.resume.title = 'Updated'
        self.resume.save()
        v2 = VersionService.create_version(self.resume, ats_score=80.0)
        
        # Restore v1
        url = reverse('version_restore', kwargs={
            'pk': self.resume.id,
            'version_id': v1.id
        })
        self.client.post(url)
        
        # Verify new version was created
        versions = ResumeVersion.objects.filter(resume=self.resume)
        self.assertEqual(versions.count(), 3)
        
        # Verify latest version is marked as restored
        latest = versions.order_by('-version_number').first()
        self.assertEqual(latest.modification_type, 'restored')
