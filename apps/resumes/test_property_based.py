"""
Property-Based Tests for NextGenCV v2.0

Uses Hypothesis to test universal properties that should hold for all inputs.
These tests validate correctness properties defined in the design document.
"""
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth.models import User
from apps.resumes.models import Resume, Experience, ResumeVersion, ResumeAnalysis
from apps.resumes.services.version_service import VersionService
from apps.analyzer.services.scoring_engine import ScoringEngineService
from apps.analytics.services.analytics_service import AnalyticsService
from datetime import date


class PropertyBasedTests(TestCase):
    """Property-based tests for core system properties"""
    
    @given(st.floats(min_value=0.0, max_value=100.0))
    @settings(max_examples=100, deadline=None)
    def test_property_score_bounds(self, score):
        """
        Property: Score Composition
        For any ATS score calculation, the final score should be between 0 and 100.
        
        **Feature: nextgencv-v2-advanced, Property 6: Score Composition**
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**
        """
        # Create a user for this test
        user = User.objects.create_user(
            username=f'testuser_{score}',
            password='testpass123'
        )
        
        # Create a resume
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            template='professional'
        )
        
        # Create minimal experience
        Experience.objects.create(
            resume=resume,
            company='Test Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description='Test description',
            order=0
        )
        
        # Calculate score
        job_description = "Python developer with Django experience"
        result = ScoringEngineService.calculate_ats_score(resume, job_description)
        
        # Property: Final score must be between 0 and 100
        self.assertGreaterEqual(result['final_score'], 0.0,
                               f"Score {result['final_score']} is below 0")
        self.assertLessEqual(result['final_score'], 100.0,
                            f"Score {result['final_score']} is above 100")
        
        # All component scores must also be in bounds
        for key, value in result.items():
            if key.endswith('_score'):
                self.assertGreaterEqual(value, 0.0,
                                       f"{key} {value} is below 0")
                self.assertLessEqual(value, 100.0,
                                    f"{key} {value} is above 100")
    
    @given(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
    @settings(max_examples=50, deadline=None)
    def test_property_health_score_bounds(self, resume_title):
        """
        Property: Health Score Bounds
        For any resume, the health score should be between 0 and 100 inclusive.
        
        **Feature: nextgencv-v2-advanced, Property 11: Health Score Bounds**
        **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**
        """
        # Create user for this test
        user = User.objects.create_user(
            username=f'user_{hash(resume_title) % 10000}',
            password='testpass123'
        )
        
        # Create resume with random title
        resume = Resume.objects.create(
            user=user,
            title=resume_title[:100],  # Limit to model max_length
            template='professional'
        )
        
        # Calculate health
        health = AnalyticsService.calculate_resume_health(resume)
        
        # Property: Health score must be between 0 and 100
        self.assertGreaterEqual(health, 0.0,
                               f"Health score {health} is below 0")
        self.assertLessEqual(health, 100.0,
                            f"Health score {health} is above 100")
    
    def test_property_version_comparison_symmetry(self):
        """
        Property: Version Comparison Symmetry
        For any two versions A and B, comparing A to B should show the inverse
        changes of comparing B to A.
        
        **Feature: nextgencv-v2-advanced, Property 9: Version Comparison Symmetry**
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        # Create user
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create resume
        resume = Resume.objects.create(
            user=user,
            title='Original Title',
            template='professional'
        )
        
        # Create version 1
        v1 = VersionService.create_version(resume, ats_score=70.0)
        
        # Modify resume
        resume.title = 'Modified Title'
        resume.save()
        
        # Create version 2
        v2 = VersionService.create_version(resume, ats_score=80.0)
        
        # Compare v1 to v2
        diff_1_to_2 = VersionService.compare_versions(v1, v2)
        
        # Compare v2 to v1
        diff_2_to_1 = VersionService.compare_versions(v2, v1)
        
        # Property: Number of changes should be the same
        self.assertEqual(len(diff_1_to_2['changes']), len(diff_2_to_1['changes']))
        
        # Property: Changes should be inverse
        # If v1->v2 shows "old: X, new: Y", then v2->v1 should show "old: Y, new: X"
        for change_1_to_2 in diff_1_to_2['changes']:
            # Find corresponding change in reverse comparison
            matching_changes = [
                c for c in diff_2_to_1['changes']
                if c['field'] == change_1_to_2['field']
            ]
            
            if matching_changes:
                change_2_to_1 = matching_changes[0]
                # Old and new should be swapped
                self.assertEqual(change_1_to_2['old_value'], change_2_to_1['new_value'])
                self.assertEqual(change_1_to_2['new_value'], change_2_to_1['old_value'])
    
    def test_property_version_number_uniqueness(self):
        """
        Property: Version Number Uniqueness
        For any resume, version numbers should be unique and sequential within
        that resume's version history.
        
        **Feature: nextgencv-v2-advanced, Property 2: Version Number Uniqueness**
        **Validates: Requirements 1.1, 1.6**
        """
        # Create user
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # Create resume
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            template='professional'
        )
        
        # Create multiple versions
        versions = []
        for i in range(10):
            resume.title = f'Version {i}'
            resume.save()
            v = VersionService.create_version(resume)
            versions.append(v)
        
        # Property: All version numbers should be unique
        version_numbers = [v.version_number for v in versions]
        self.assertEqual(len(version_numbers), len(set(version_numbers)),
                        "Version numbers are not unique")
        
        # Property: Version numbers should be sequential (1, 2, 3, ...)
        expected_numbers = list(range(1, len(versions) + 1))
        self.assertEqual(sorted(version_numbers), expected_numbers,
                        "Version numbers are not sequential")
    
    def test_property_data_isolation(self):
        """
        Property: Data Isolation
        For any user, they should only be able to access resumes, versions,
        and analyses that belong to them.
        
        **Feature: nextgencv-v2-advanced, Property 10: Data Isolation**
        **Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5**
        """
        # Create two users
        user1 = User.objects.create_user(username='user1', password='pass1')
        user2 = User.objects.create_user(username='user2', password='pass2')
        
        # Create resumes for each user
        resume1 = Resume.objects.create(user=user1, title='User1 Resume', template='professional')
        resume2 = Resume.objects.create(user=user2, title='User2 Resume', template='professional')
        
        # Create versions
        v1 = VersionService.create_version(resume1)
        v2 = VersionService.create_version(resume2)
        
        # Create analyses
        analysis1 = ResumeAnalysis.objects.create(
            resume=resume1,
            job_description='Test',
            keyword_match_score=70.0,
            skill_relevance_score=70.0,
            section_completeness_score=70.0,
            experience_impact_score=70.0,
            quantification_score=70.0,
            action_verb_score=70.0,
            final_score=70.0
        )
        
        analysis2 = ResumeAnalysis.objects.create(
            resume=resume2,
            job_description='Test',
            keyword_match_score=80.0,
            skill_relevance_score=80.0,
            section_completeness_score=80.0,
            experience_impact_score=80.0,
            quantification_score=80.0,
            action_verb_score=80.0,
            final_score=80.0
        )
        
        # Property: User1 should only see their own resumes
        user1_resumes = Resume.objects.filter(user=user1)
        self.assertEqual(user1_resumes.count(), 1)
        self.assertEqual(user1_resumes.first().id, resume1.id)
        
        # Property: User2 should only see their own resumes
        user2_resumes = Resume.objects.filter(user=user2)
        self.assertEqual(user2_resumes.count(), 1)
        self.assertEqual(user2_resumes.first().id, resume2.id)
        
        # Property: User1 should only see their own versions
        user1_versions = ResumeVersion.objects.filter(resume__user=user1)
        self.assertEqual(user1_versions.count(), 1)
        self.assertEqual(user1_versions.first().id, v1.id)
        
        # Property: User2 should only see their own versions
        user2_versions = ResumeVersion.objects.filter(resume__user=user2)
        self.assertEqual(user2_versions.count(), 1)
        self.assertEqual(user2_versions.first().id, v2.id)
        
        # Property: User1 should only see their own analyses
        user1_analyses = ResumeAnalysis.objects.filter(resume__user=user1)
        self.assertEqual(user1_analyses.count(), 1)
        self.assertEqual(user1_analyses.first().id, analysis1.id)
        
        # Property: User2 should only see their own analyses
        user2_analyses = ResumeAnalysis.objects.filter(resume__user=user2)
        self.assertEqual(user2_analyses.count(), 1)
        self.assertEqual(user2_analyses.first().id, analysis2.id)
        
        # Cleanup
        user1.delete()
        user2.delete()
    
    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=20, deadline=None)
    def test_property_optimization_improvement(self, num_changes):
        """
        Property: Optimization Improvement
        For any accepted optimization, the optimized version's ATS score should
        be greater than or equal to the original score.
        
        **Feature: nextgencv-v2-advanced, Property 13: Optimization Improvement**
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7**
        """
        from apps.resumes.services.resume_optimizer import ResumeOptimizerService
        
        # Create user for this test
        user = User.objects.create_user(
            username=f'user_{num_changes}',
            password='testpass123'
        )
        
        # Create resume
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            template='professional'
        )
        
        # Add experience
        Experience.objects.create(
            resume=resume,
            company='Test Corp',
            role='Developer',
            start_date=date(2020, 1, 1),
            description='Worked on projects\nHelped with testing',
            order=0
        )
        
        # Run optimization
        job_description = "Python Django developer with React experience. " * 5
        result = ResumeOptimizerService.optimize_resume(resume, job_description)
        
        # Property: Optimized score >= Original score
        self.assertGreaterEqual(
            result['optimized_score'],
            result['original_score'],
            f"Optimized score {result['optimized_score']} is less than original {result['original_score']}"
        )
        
        # Property: Improvement delta >= 0
        self.assertGreaterEqual(
            result['improvement_delta'],
            0.0,
            f"Improvement delta {result['improvement_delta']} is negative"
        )
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    @settings(max_examples=30, deadline=None)
    def test_property_version_creation_atomicity(self, modification_type):
        """
        Property: Version Creation Atomicity
        For any resume modification, creating a new version should be atomic—
        either the version is fully created with all metadata, or no version is created.
        
        **Feature: nextgencv-v2-advanced, Property 1: Version Creation Atomicity**
        **Validates: Requirements 1.1**
        """
        # Limit modification_type to valid choices
        valid_types = ['manual', 'optimized', 'restored']
        mod_type = valid_types[hash(modification_type) % len(valid_types)]
        
        # Create user for this test
        user = User.objects.create_user(
            username=f'user_{hash(modification_type) % 10000}',
            password='testpass123'
        )
        
        # Create resume
        resume = Resume.objects.create(
            user=user,
            title='Test Resume',
            template='professional'
        )
        
        # Get initial version count
        initial_count = ResumeVersion.objects.filter(resume=resume).count()
        
        # Create version
        version = VersionService.create_version(
            resume,
            modification_type=mod_type,
            ats_score=75.0
        )
        
        # Property: Version should be fully created
        self.assertIsNotNone(version)
        self.assertIsNotNone(version.id)
        self.assertEqual(version.resume, resume)
        self.assertEqual(version.modification_type, mod_type)
        self.assertEqual(version.ats_score, 75.0)
        self.assertIsNotNone(version.snapshot_data)
        self.assertIsNotNone(version.created_at)
        
        # Property: Version count should increase by exactly 1
        final_count = ResumeVersion.objects.filter(resume=resume).count()
        self.assertEqual(final_count, initial_count + 1)


class TextSanitizationPropertyTests(TestCase):
    """Property-based tests for text sanitization"""
    
    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=100)
    def test_property_text_sanitization(self, text):
        """
        Property: Text Sanitization
        For any extracted text from PDF, the sanitized output should contain
        no XSS vectors or control characters.
        
        **Feature: nextgencv-v2-advanced, Property 4: Text Sanitization**
        **Validates: Requirements 3.5, 15.7**
        """
        from apps.resumes.services.pdf_parser import PDFParserService
        
        # Clean the text
        cleaned = PDFParserService.clean_extracted_text(text)
        
        # Property: No control characters (except newlines, tabs, spaces)
        for char in cleaned:
            if char not in ['\n', '\t', ' '] and not char.isprintable():
                self.fail(f"Control character found in cleaned text: {repr(char)}")
        
        # Property: No common XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        cleaned_lower = cleaned.lower()
        for pattern in xss_patterns:
            self.assertNotIn(pattern, cleaned_lower,
                           f"XSS pattern '{pattern}' found in cleaned text")
        
        # Property: Cleaned text should be a string
        self.assertIsInstance(cleaned, str)
