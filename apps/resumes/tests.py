from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from .models import Resume, Experience
from .forms import ExperienceForm


class ExperienceFormTests(TestCase):
    """Test the ExperienceForm validation."""
    
    def test_experience_form_valid_with_end_date(self):
        """Test that form is valid with both start and end dates."""
        form_data = {
            'company': 'Test Company',
            'role': 'Software Engineer',
            'start_date': date(2020, 1, 1),
            'end_date': date(2022, 12, 31),
            'description': 'Test description'
        }
        form = ExperienceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_experience_form_valid_without_end_date(self):
        """Test that form is valid without end date (current position)."""
        form_data = {
            'company': 'Test Company',
            'role': 'Software Engineer',
            'start_date': date(2020, 1, 1),
            'end_date': None,
            'description': 'Test description'
        }
        form = ExperienceForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_experience_form_invalid_date_order(self):
        """Test that form is invalid when start_date is after end_date."""
        form_data = {
            'company': 'Test Company',
            'role': 'Software Engineer',
            'start_date': date(2022, 12, 31),
            'end_date': date(2020, 1, 1),
            'description': 'Test description'
        }
        form = ExperienceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Start date must be before end date', str(form.errors))


class ExperienceViewTests(TestCase):
    """Test the experience management views."""
    
    def setUp(self):
        """Set up test user and resume."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_experience_add_view_get(self):
        """Test that experience add view loads correctly."""
        url = reverse('experience_add', kwargs={'resume_pk': self.resume.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Experience')
    
    def test_experience_add_view_post(self):
        """Test adding a new experience entry."""
        url = reverse('experience_add', kwargs={'resume_pk': self.resume.id})
        data = {
            'company': 'Test Company',
            'role': 'Software Engineer',
            'start_date': '2020-01-01',
            'end_date': '2022-12-31',
            'description': 'Test description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify experience was created
        self.assertEqual(self.resume.experiences.count(), 1)
        exp = self.resume.experiences.first()
        self.assertEqual(exp.company, 'Test Company')
        self.assertEqual(exp.role, 'Software Engineer')
    
    def test_experience_edit_view(self):
        """Test editing an existing experience entry."""
        # Create an experience
        exp = Experience.objects.create(
            resume=self.resume,
            company='Old Company',
            role='Old Role',
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            description='Old description'
        )
        
        url = reverse('experience_edit', kwargs={
            'resume_pk': self.resume.id,
            'experience_pk': exp.id
        })
        data = {
            'company': 'New Company',
            'role': 'New Role',
            'start_date': '2020-01-01',
            'end_date': '2022-12-31',
            'description': 'New description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify experience was updated
        exp.refresh_from_db()
        self.assertEqual(exp.company, 'New Company')
        self.assertEqual(exp.role, 'New Role')
    
    def test_experience_delete_view(self):
        """Test deleting an experience entry."""
        # Create an experience
        exp = Experience.objects.create(
            resume=self.resume,
            company='Test Company',
            role='Test Role',
            start_date=date(2020, 1, 1),
            description='Test description'
        )
        
        url = reverse('experience_delete', kwargs={
            'resume_pk': self.resume.id,
            'experience_pk': exp.id
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        
        # Verify experience was deleted
        self.assertEqual(self.resume.experiences.count(), 0)
    
    def test_experience_ordering(self):
        """Test that experiences are displayed in reverse chronological order."""
        # Create multiple experiences
        exp1 = Experience.objects.create(
            resume=self.resume,
            company='Company 1',
            role='Role 1',
            start_date=date(2018, 1, 1),
            end_date=date(2020, 12, 31),
            description='Description 1'
        )
        exp2 = Experience.objects.create(
            resume=self.resume,
            company='Company 2',
            role='Role 2',
            start_date=date(2021, 1, 1),
            end_date=date(2023, 12, 31),
            description='Description 2'
        )
        exp3 = Experience.objects.create(
            resume=self.resume,
            company='Company 3',
            role='Role 3',
            start_date=date(2015, 1, 1),
            end_date=date(2017, 12, 31),
            description='Description 3'
        )
        
        # Get experiences in order
        experiences = list(self.resume.experiences.all())
        
        # Should be ordered by start_date descending (most recent first)
        self.assertEqual(experiences[0].id, exp2.id)  # 2021
        self.assertEqual(experiences[1].id, exp1.id)  # 2018
        self.assertEqual(experiences[2].id, exp3.id)  # 2015
    
    def test_unauthorized_access(self):
        """Test that users cannot access other users' resumes."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_resume = Resume.objects.create(
            user=other_user,
            title='Other Resume',
            template='professional'
        )
        
        # Try to add experience to other user's resume
        url = reverse('experience_add', kwargs={'resume_pk': other_resume.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
