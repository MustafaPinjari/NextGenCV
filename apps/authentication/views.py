from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user with hashed password (handled by UserCreationForm)
            user = form.save()
            username = form.cleaned_data.get('username')
            logger.info(f'New user registered: {username}')
            messages.success(request, f'Account created successfully for {username}! You can now log in.')
            return redirect('login')
        else:
            logger.warning(f'Failed registration attempt with errors: {form.errors}')
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
        messages.info(request, 'Create an account to start building your ATS-optimized resumes.')
    
    return render(request, 'authentication/register.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's resumes (will be implemented when resume app is ready)
    from apps.resumes.services import ResumeService
    resumes = ResumeService.get_user_resumes(request.user)
    
    # Add info message if no resumes exist
    if not resumes.exists():
        messages.info(request, 'Welcome! Get started by creating your first resume.')
    
    context = {
        'user': request.user,
        'resumes': resumes,
    }
    return render(request, 'authentication/dashboard.html', context)
