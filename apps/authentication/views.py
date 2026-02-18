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
    from apps.analytics.services.analytics_service import AnalyticsService
    from django.utils import timezone
    from datetime import timedelta
    import json
    
    resumes = ResumeService.get_user_resumes(request.user)
    
    # Calculate resume health for the first resume (or average if multiple)
    resume_health = None
    average_score = None
    health_dashoffset = 439.8  # Full circle (no progress)
    
    if resumes.exists():
        # Calculate health for the most recent resume
        latest_resume = resumes.first()
        resume_health = AnalyticsService.calculate_resume_health(latest_resume)
        
        # Calculate stroke-dashoffset for circular progress
        # circumference = 2 * PI * radius = 2 * 3.14159 * 70 = 439.8
        circumference = 439.8
        health_dashoffset = circumference - (resume_health / 100) * circumference
        
        # Get average score from analyses
        from apps.resumes.models import ResumeAnalysis
        analyses = ResumeAnalysis.objects.filter(resume__user=request.user)
        if analyses.exists():
            from django.db.models import Avg
            avg_score = analyses.aggregate(Avg('final_score'))['final_score__avg']
            average_score = round(avg_score, 1) if avg_score else None
    
    # Get recent activities
    recent_activities = []
    
    # Add resume creation activities
    for resume in resumes[:5]:
        recent_activities.append({
            'type': 'created' if resume.created_at == resume.updated_at else 'updated',
            'description': f"{'Created' if resume.created_at == resume.updated_at else 'Updated'} resume: {resume.title}",
            'timestamp': resume.updated_at
        })
    
    # Sort by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Prepare chart data if user has analyses
    show_charts = False
    chart_data_json = None
    
    if resumes.exists():
        from apps.resumes.models import ResumeAnalysis
        analyses = ResumeAnalysis.objects.filter(resume__user=request.user).order_by('analysis_timestamp')
        
        if analyses.count() >= 2:
            show_charts = True
            
            # Score trend data
            score_labels = [a.analysis_timestamp.strftime('%m/%d') for a in analyses[:10]]
            score_values = [float(a.final_score) for a in analyses[:10]]
            
            # Keyword match data (example categories)
            chart_data = {
                'score_trend': {
                    'labels': score_labels,
                    'scores': score_values
                },
                'keyword_match': {
                    'labels': ['Technical Skills', 'Soft Skills', 'Experience', 'Education', 'Achievements'],
                    'data': [75, 60, 85, 90, 70]  # Example data
                }
            }
            
            # Serialize to JSON for template
            chart_data_json = json.dumps(chart_data)
    
    # Add info message if no resumes exist
    if not resumes.exists():
        messages.info(request, 'Welcome! Get started by creating your first resume.')
    
    context = {
        'user': request.user,
        'resumes': resumes,
        'resume_health': resume_health,
        'health_dashoffset': health_dashoffset,
        'average_score': average_score,
        'recent_activities': recent_activities,
        'show_charts': show_charts,
        'chart_data_json': chart_data_json,
        'current_date': timezone.now(),
    }
    return render(request, 'authentication/dashboard_new.html', context)

