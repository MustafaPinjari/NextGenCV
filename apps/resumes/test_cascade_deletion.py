"""
Tests for cascade deletion functionality.

Verifies that when a user is deleted, all associated data is properly deleted.
This ensures data isolation and prevents orphaned records.

Requirements: 16.6
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.resumes.models import (
    Resume, PersonalInfo, Experience, Education, Skill, Project,
    ResumeVersion, UploadedResume, ResumeAnalysis, OptimizationHistory
)
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class CascadeDeletionTest(TestCase):
    """Test cascade deletion of user data."""
    
    def setUp(self):
        """Create test user and associated data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create resume
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Create personal info
        self.personal_info = PersonalInfo.objects.create(
            resume=self.resume,
            full_name='Test User',
            phone='123-456-7890',
            email='test@example.com',
            location='Test City'
        )
        
        # Create experience
        self.experience = Experience.objects.create(
            resume=self.resume,
            company='Test Company',
            role='Test Role',
            start_date='2020-01-01',
            end_date='2021-01-01',
            description='Test description'
        )
        
        # Create education
        self.education = Education.objects.create(
            resume=self.resume,
            institution='Test University',
            degree='Bachelor',
            field='Computer Science',
            start_year=2016,
            end_year=2020
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
            description='Test project description',
            technologies='Python, Django'
        )
        
        # Create resume version
        self.version = ResumeVersion.objects.create(
            resume=self.resume,
            version_number=1,
            modification_type='manual',
            snapshot_data={'test': 'data'}
        )
        
        # Create uploaded resume
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"test content",
            content_type="application/pdf"
        )
        self.uploaded_resume = UploadedResume.objects.create(
            user=self.user,
            original_filename='test.pdf',
            file_path=test_file,
            file_size=100,
            status='uploaded'
        )
        
        # Create resume analysis
        self.analysis = ResumeAnalysis.objects.create(
            resume=self.resume,
            job_description='Test job description',
            keyword_match_score=75.0,
            skill_relevance_score=80.0,
            section_completeness_score=85.0,
            experience_impact_score=70.0,
            quantification_score=65.0,
            action_verb_score=75.0,
            final_score=75.0
        )
        
        # Create optimization history
        self.optimization = OptimizationHistory.objects.create(
            resume=self.resume,
            original_version=self.version,
            job_description='Test job description',
            original_score=70.0,
            optimized_score=80.0,
            improvement_delta=10.0
        )
    
    def test_user_deletion_cascades_to_resumes(self):
        """Test that deleting user deletes all resumes."""
        resume_id = self.resume.id
        
        # Delete user
        self.user.delete()
        
        # Verify resume is deleted
        self.assertFalse(Resume.objects.filter(id=resume_id).exists())
    
    def test_user_deletion_cascades_to_personal_info(self):
        """Test that deleting user deletes personal info."""
        personal_info_id = self.personal_info.id
        
        # Delete user
        self.user.delete()
        
        # Verify personal info is deleted
        self.assertFalse(PersonalInfo.objects.filter(id=personal_info_id).exists())
    
    def test_user_deletion_cascades_to_experiences(self):
        """Test that deleting user deletes experiences."""
        experience_id = self.experience.id
        
        # Delete user
        self.user.delete()
        
        # Verify experience is deleted
        self.assertFalse(Experience.objects.filter(id=experience_id).exists())
    
    def test_user_deletion_cascades_to_education(self):
        """Test that deleting user deletes education."""
        education_id = self.education.id
        
        # Delete user
        self.user.delete()
        
        # Verify education is deleted
        self.assertFalse(Education.objects.filter(id=education_id).exists())
    
    def test_user_deletion_cascades_to_skills(self):
        """Test that deleting user deletes skills."""
        skill_id = self.skill.id
        
        # Delete user
        self.user.delete()
        
        # Verify skill is deleted
        self.assertFalse(Skill.objects.filter(id=skill_id).exists())
    
    def test_user_deletion_cascades_to_projects(self):
        """Test that deleting user deletes projects."""
        project_id = self.project.id
        
        # Delete user
        self.user.delete()
        
        # Verify project is deleted
        self.assertFalse(Project.objects.filter(id=project_id).exists())
    
    def test_user_deletion_cascades_to_versions(self):
        """Test that deleting user deletes resume versions."""
        version_id = self.version.id
        
        # Delete user
        self.user.delete()
        
        # Verify version is deleted
        self.assertFalse(ResumeVersion.objects.filter(id=version_id).exists())
    
    def test_user_deletion_cascades_to_uploaded_resumes(self):
        """Test that deleting user deletes uploaded resumes."""
        uploaded_resume_id = self.uploaded_resume.id
        
        # Delete user
        self.user.delete()
        
        # Verify uploaded resume is deleted
        self.assertFalse(UploadedResume.objects.filter(id=uploaded_resume_id).exists())
    
    def test_user_deletion_cascades_to_analyses(self):
        """Test that deleting user deletes resume analyses."""
        analysis_id = self.analysis.id
        
        # Delete user
        self.user.delete()
        
        # Verify analysis is deleted
        self.assertFalse(ResumeAnalysis.objects.filter(id=analysis_id).exists())
    
    def test_user_deletion_cascades_to_optimizations(self):
        """Test that deleting user deletes optimization histories."""
        optimization_id = self.optimization.id
        
        # Delete user
        self.user.delete()
        
        # Verify optimization is deleted
        self.assertFalse(OptimizationHistory.objects.filter(id=optimization_id).exists())
    
    def test_resume_deletion_cascades_to_all_sections(self):
        """Test that deleting resume deletes all associated sections."""
        personal_info_id = self.personal_info.id
        experience_id = self.experience.id
        education_id = self.education.id
        skill_id = self.skill.id
        project_id = self.project.id
        version_id = self.version.id
        analysis_id = self.analysis.id
        optimization_id = self.optimization.id
        
        # Delete resume
        self.resume.delete()
        
        # Verify all sections are deleted
        self.assertFalse(PersonalInfo.objects.filter(id=personal_info_id).exists())
        self.assertFalse(Experience.objects.filter(id=experience_id).exists())
        self.assertFalse(Education.objects.filter(id=education_id).exists())
        self.assertFalse(Skill.objects.filter(id=skill_id).exists())
        self.assertFalse(Project.objects.filter(id=project_id).exists())
        self.assertFalse(ResumeVersion.objects.filter(id=version_id).exists())
        self.assertFalse(ResumeAnalysis.objects.filter(id=analysis_id).exists())
        self.assertFalse(OptimizationHistory.objects.filter(id=optimization_id).exists())
    
    def test_complete_user_data_deletion(self):
        """Test that deleting user removes ALL associated data."""
        user_id = self.user.id
        
        # Count all data before deletion
        resume_count = Resume.objects.filter(user=self.user).count()
        uploaded_count = UploadedResume.objects.filter(user=self.user).count()
        
        # Verify we have data
        self.assertGreater(resume_count, 0)
        self.assertGreater(uploaded_count, 0)
        
        # Delete user
        self.user.delete()
        
        # Verify ALL data is deleted
        self.assertEqual(Resume.objects.filter(user_id=user_id).count(), 0)
        self.assertEqual(UploadedResume.objects.filter(user_id=user_id).count(), 0)
        
        # Verify no orphaned data exists
        self.assertEqual(PersonalInfo.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(Experience.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(Education.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(Skill.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(Project.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(ResumeVersion.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(ResumeAnalysis.objects.filter(resume__user_id=user_id).count(), 0)
        self.assertEqual(OptimizationHistory.objects.filter(resume__user_id=user_id).count(), 0)


class CascadeDeletionMultiUserTest(TestCase):
    """Test that cascade deletion only affects the deleted user's data."""
    
    def setUp(self):
        """Create two users with data."""
        # User 1
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.resume1 = Resume.objects.create(
            user=self.user1,
            title='User 1 Resume'
        )
        
        # User 2
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.resume2 = Resume.objects.create(
            user=self.user2,
            title='User 2 Resume'
        )
    
    def test_deleting_one_user_preserves_other_user_data(self):
        """Test that deleting one user doesn't affect another user's data."""
        resume2_id = self.resume2.id
        
        # Delete user 1
        self.user1.delete()
        
        # Verify user 1's resume is deleted
        self.assertFalse(Resume.objects.filter(user=self.user1).exists())
        
        # Verify user 2's resume still exists
        self.assertTrue(Resume.objects.filter(id=resume2_id).exists())
        self.assertTrue(Resume.objects.filter(user=self.user2).exists())
