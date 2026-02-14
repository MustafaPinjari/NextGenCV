"""
Unit tests for VersionService
"""
from django.test import TestCase
from django.contrib.auth.models import User
from apps.resumes.models import Resume, ResumeVersion, PersonalInfo, Experience, Education, Skill, Project
from apps.resumes.services.version_service import VersionService
from datetime import date


class VersionServiceTest(TestCase):
    """Test cases for VersionService"""
    
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
        
        # Create experience
        self.experience = Experience.objects.create(
            resume=self.resume,
            company='Tech Corp',
            role='Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed web applications',
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
            description='A test project',
            technologies='Python, Django',
            order=0
        )
    
    def test_create_version_basic(self):
        """Test basic version creation"""
        version = VersionService.create_version(self.resume)
        
        self.assertIsNotNone(version)
        self.assertEqual(version.resume, self.resume)
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.modification_type, 'manual')
        self.assertIsNotNone(version.snapshot_data)
        
        # Check resume's current version number updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.current_version_number, 1)
    
    def test_create_version_with_parameters(self):
        """Test version creation with custom parameters"""
        version = VersionService.create_version(
            self.resume,
            modification_type='optimized',
            user_notes='Test notes',
            ats_score=85.5
        )
        
        self.assertEqual(version.modification_type, 'optimized')
        self.assertEqual(version.user_notes, 'Test notes')
        self.assertEqual(version.ats_score, 85.5)
    
    def test_create_multiple_versions(self):
        """Test creating multiple versions increments version number"""
        version1 = VersionService.create_version(self.resume)
        version2 = VersionService.create_version(self.resume)
        version3 = VersionService.create_version(self.resume)
        
        self.assertEqual(version1.version_number, 1)
        self.assertEqual(version2.version_number, 2)
        self.assertEqual(version3.version_number, 3)
        
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.current_version_number, 3)
    
    def test_snapshot_contains_all_data(self):
        """Test that snapshot contains all resume data"""
        version = VersionService.create_version(self.resume)
        snapshot = version.snapshot_data
        
        # Check basic fields
        self.assertEqual(snapshot['title'], 'Test Resume')
        self.assertEqual(snapshot['template'], 'professional')
        
        # Check personal info
        self.assertIn('personal_info', snapshot)
        self.assertEqual(snapshot['personal_info']['full_name'], 'John Doe')
        self.assertEqual(snapshot['personal_info']['email'], 'john@example.com')
        
        # Check experiences
        self.assertIn('experiences', snapshot)
        self.assertEqual(len(snapshot['experiences']), 1)
        self.assertEqual(snapshot['experiences'][0]['company'], 'Tech Corp')
        
        # Check education
        self.assertIn('education', snapshot)
        self.assertEqual(len(snapshot['education']), 1)
        self.assertEqual(snapshot['education'][0]['institution'], 'University')
        
        # Check skills
        self.assertIn('skills', snapshot)
        self.assertEqual(len(snapshot['skills']), 1)
        self.assertEqual(snapshot['skills'][0]['name'], 'Python')
        
        # Check projects
        self.assertIn('projects', snapshot)
        self.assertEqual(len(snapshot['projects']), 1)
        self.assertEqual(snapshot['projects'][0]['name'], 'Test Project')
    
    def test_get_version_history(self):
        """Test retrieving version history"""
        # Create multiple versions
        v1 = VersionService.create_version(self.resume)
        v2 = VersionService.create_version(self.resume)
        v3 = VersionService.create_version(self.resume)
        
        history = VersionService.get_version_history(self.resume)
        
        self.assertEqual(len(history), 3)
        # Should be in reverse order (newest first)
        self.assertEqual(history[0].version_number, 3)
        self.assertEqual(history[1].version_number, 2)
        self.assertEqual(history[2].version_number, 1)
    
    def test_get_version_history_empty(self):
        """Test version history for resume with no versions"""
        history = VersionService.get_version_history(self.resume)
        self.assertEqual(len(history), 0)
    
    def test_compare_versions_no_changes(self):
        """Test comparing identical versions"""
        v1 = VersionService.create_version(self.resume)
        v2 = VersionService.create_version(self.resume)
        
        diff = VersionService.compare_versions(v1, v2)
        
        self.assertEqual(diff['version1_number'], 1)
        self.assertEqual(diff['version2_number'], 2)
        self.assertEqual(len(diff['changes']), 0)
    
    def test_compare_versions_with_changes(self):
        """Test comparing versions with changes"""
        # Create first version
        v1 = VersionService.create_version(self.resume)
        
        # Modify resume
        self.resume.title = 'Updated Resume'
        self.resume.save()
        
        self.personal_info.phone = '555-9999'
        self.personal_info.save()
        
        # Create second version
        v2 = VersionService.create_version(self.resume)
        
        diff = VersionService.compare_versions(v1, v2)
        
        self.assertGreater(len(diff['changes']), 0)
        
        # Check for title change
        title_changes = [c for c in diff['changes'] if c['field'] == 'title']
        self.assertEqual(len(title_changes), 1)
        self.assertEqual(title_changes[0]['old_value'], 'Test Resume')
        self.assertEqual(title_changes[0]['new_value'], 'Updated Resume')
        
        # Check for phone change
        phone_changes = [c for c in diff['changes'] if c['field'] == 'phone']
        self.assertEqual(len(phone_changes), 1)
        self.assertEqual(phone_changes[0]['old_value'], '555-1234')
        self.assertEqual(phone_changes[0]['new_value'], '555-9999')
    
    def test_compare_versions_added_experience(self):
        """Test detecting added experience"""
        v1 = VersionService.create_version(self.resume)
        
        # Add new experience
        Experience.objects.create(
            resume=self.resume,
            company='New Corp',
            role='Senior Engineer',
            start_date=date(2024, 1, 1),
            description='New role',
            order=1
        )
        
        v2 = VersionService.create_version(self.resume)
        
        diff = VersionService.compare_versions(v1, v2)
        
        # Check for added experience
        exp_changes = [c for c in diff['changes'] if c['section'] == 'experiences']
        added_changes = [c for c in exp_changes if c['type'] == 'added']
        self.assertGreater(len(added_changes), 0)
    
    def test_restore_version(self):
        """Test restoring a previous version"""
        # Create initial version
        v1 = VersionService.create_version(self.resume)
        original_title = self.resume.title
        
        # Modify resume
        self.resume.title = 'Modified Resume'
        self.resume.save()
        v2 = VersionService.create_version(self.resume)
        
        # Restore to v1
        restored_resume = VersionService.restore_version(v1)
        
        self.assertEqual(restored_resume.title, original_title)
        
        # Should create a new version
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.current_version_number, 3)
        
        # Check that a restored version was created
        latest_version = ResumeVersion.objects.filter(resume=self.resume).order_by('-version_number').first()
        self.assertEqual(latest_version.modification_type, 'restored')
    
    def test_version_uniqueness(self):
        """Test that version numbers are unique per resume"""
        v1 = VersionService.create_version(self.resume)
        
        # Create another resume for same user
        resume2 = Resume.objects.create(
            user=self.user,
            title='Second Resume',
            template='modern'
        )
        
        v2 = VersionService.create_version(resume2)
        
        # Both should have version number 1
        self.assertEqual(v1.version_number, 1)
        self.assertEqual(v2.version_number, 1)
        
        # But they should be different versions
        self.assertNotEqual(v1.id, v2.id)
