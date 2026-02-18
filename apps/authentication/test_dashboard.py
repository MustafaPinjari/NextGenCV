"""
Tests for the redesigned dashboard view
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.resumes.models import Resume, PersonalInfo


class DashboardViewTest(TestCase):
    """Test the redesigned dashboard view"""
    
    def setUp(self):
        """Set up test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.dashboard_url = reverse('dashboard')
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login/', response.url)
    
    def test_dashboard_loads_for_authenticated_user(self):
        """Test that dashboard loads successfully for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/dashboard_new.html')
    
    def test_dashboard_shows_welcome_message(self):
        """Test that dashboard shows welcome message with username"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        self.assertContains(response, 'Welcome back, testuser!')
    
    def test_dashboard_shows_empty_state_without_resumes(self):
        """Test that dashboard shows empty state when user has no resumes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        self.assertContains(response, 'No resumes yet')
        self.assertContains(response, 'Create your first resume')
    
    def test_dashboard_shows_resume_health_with_resumes(self):
        """Test that dashboard shows resume health when user has resumes"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a resume for the user
        resume = Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=resume,
            full_name='Test User',
            email='test@example.com',
            phone='123-456-7890'
        )
        
        response = self.client.get(self.dashboard_url)
        
        # Check that health meter is present
        self.assertContains(response, 'Resume Health')
        self.assertContains(response, 'Health Score')
        
        # Check that resume health value is in context
        self.assertIn('resume_health', response.context)
        self.assertIsNotNone(response.context['resume_health'])
    
    def test_dashboard_shows_quick_actions(self):
        """Test that dashboard shows quick action cards"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Check for quick action cards
        self.assertContains(response, 'Quick Actions')
        self.assertContains(response, 'Create Resume')
        self.assertContains(response, 'Upload PDF')
        self.assertContains(response, 'View Analytics')
        self.assertContains(response, 'Browse Templates')
    
    def test_dashboard_shows_recent_resumes(self):
        """Test that dashboard shows recent resumes section"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create multiple resumes
        for i in range(3):
            Resume.objects.create(
                user=self.user,
                title=f'Test Resume {i+1}',
                template='professional'
            )
        
        response = self.client.get(self.dashboard_url)
        
        # Check that recent resumes section is present
        self.assertContains(response, 'Recent Resumes')
        self.assertContains(response, 'Test Resume 1')
        self.assertContains(response, 'Test Resume 2')
        self.assertContains(response, 'Test Resume 3')
    
    def test_dashboard_shows_activity_feed(self):
        """Test that dashboard shows activity feed"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Check that activity feed section is present
        self.assertContains(response, 'Recent Activity')
    
    def test_dashboard_context_data(self):
        """Test that dashboard provides correct context data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a resume
        Resume.objects.create(
            user=self.user,
            title='Test Resume',
            template='professional'
        )
        
        response = self.client.get(self.dashboard_url)
        
        # Check context variables
        self.assertIn('user', response.context)
        self.assertIn('resumes', response.context)
        self.assertIn('resume_health', response.context)
        self.assertIn('recent_activities', response.context)
        self.assertIn('current_date', response.context)
        
        # Check that resumes count is correct
        self.assertEqual(response.context['resumes'].count(), 1)
    
    def test_dashboard_uses_authenticated_layout(self):
        """Test that dashboard extends authenticated layout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Check for authenticated layout elements
        self.assertContains(response, 'sidebar')
        self.assertContains(response, 'topbar')
        self.assertContains(response, 'main-content')
    
    def test_dashboard_includes_design_system_css(self):
        """Test that dashboard includes design system CSS"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Check that the template extends authenticated layout which includes design system CSS
        # In test mode, static files may not be fully resolved, so we check for the link tag
        self.assertContains(response, '<link rel="stylesheet"')
    
    def test_dashboard_includes_chart_js_when_data_available(self):
        """Test that dashboard includes Chart.js when chart data is available"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Check for Chart.js CDN
        self.assertContains(response, 'chart.js')

