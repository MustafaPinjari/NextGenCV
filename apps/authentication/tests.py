from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticationIntegrationTest(TestCase):
    """Integration tests for authentication system"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')
    
    def test_registration_flow(self):
        """Test user can register with valid data"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should redirect to login after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_duplicate_username_rejected(self):
        """Test registration with duplicate username is rejected"""
        User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'another@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_duplicate_email_rejected(self):
        """Test registration with duplicate email is rejected"""
        User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        
        response = self.client.post(self.register_url, {
            'username': 'anotheruser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
    
    def test_login_with_valid_credentials(self):
        """Test user can login with valid credentials"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials is rejected"""
        User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
    
    def test_logout_terminates_session(self):
        """Test logout terminates user session"""
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        # User should be authenticated
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.get(self.logout_url)
        
        # After logout, accessing dashboard should redirect to login
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))
    
    def test_protected_resource_requires_authentication(self):
        """Test unauthenticated users are redirected to login"""
        response = self.client.get(self.dashboard_url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))
    
    def test_password_is_hashed(self):
        """Test passwords are stored hashed, not in plaintext"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        user = User.objects.get(username='testuser')
        # Password should not be stored in plaintext
        self.assertNotEqual(user.password, 'testpass123')
        # Password should be hashed (starts with algorithm identifier)
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
