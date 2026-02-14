from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import bleach


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with username, email, and password.
    
    Validates: Requirements 1.1, 1.2, 13.2, 14.1, 14.2, 14.3, 14.4
    """
    
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Please enter a valid email address.',
            'max_length': 'Email cannot exceed 254 characters.'
        }
    )
    
    username = forms.CharField(
        required=True,
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        error_messages={
            'required': 'Username is required.',
            'max_length': 'Username cannot exceed 150 characters.',
            'min_length': 'Username must be at least 3 characters long.'
        }
    )
    
    password1 = forms.CharField(
        required=True,
        label='Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    
    password2 = forms.CharField(
        required=True,
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        error_messages={
            'required': 'Please confirm your password.'
        }
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """
        Validate that email is unique and properly formatted.
        Sanitizes input to prevent XSS.
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        
        # Sanitize email to prevent XSS
        email = bleach.clean(email.strip())
        
        # Validate length
        if len(email) > 254:
            raise ValidationError('Email cannot exceed 254 characters.')
        
        # Check uniqueness
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        
        return email.lower()
    
    def clean_username(self):
        """
        Validate that username is unique, meets length requirements, and is sanitized.
        Sanitizes input to prevent XSS.
        """
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Username is required.')
        
        # Sanitize username to prevent XSS
        username = bleach.clean(username.strip())
        
        # Validate length
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        if len(username) > 150:
            raise ValidationError('Username cannot exceed 150 characters.')
        
        # Check uniqueness
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        
        return username
