from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import EmailVerificationToken
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def register(request):
    """User registration view — creates account and sends verification email."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            logger.info(f'New user registered: {username}')

            # Create verification token and send email asynchronously
            token_obj = EmailVerificationToken.create_for_user(user)
            try:
                from apps.resumes.tasks import send_verification_email_task
                base_url = request.build_absolute_uri('/').rstrip('/')
                send_verification_email_task.delay(user.id, token_obj.token, base_url)
            except Exception as e:
                # Celery may not be running in dev — log but don't block registration
                logger.warning(f'Could not queue verification email: {e}')

            messages.success(
                request,
                f'Account created for {username}! Check your email to verify your address, then log in.'
            )
            return redirect('login')
        else:
            logger.warning(f'Failed registration attempt with errors: {form.errors}')
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
        messages.info(request, 'Create an account to start building your ATS-optimized resumes.')

    return render(request, 'authentication/register.html', {'form': form})


def verify_email(request, token: str):
    """Verify a user's email address via the token link."""
    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    if token_obj.is_verified:
        messages.info(request, 'Your email is already verified. You can log in.')
        return redirect('login')

    if token_obj.is_expired:
        messages.error(request, 'This verification link has expired. Request a new one below.')
        return redirect('resend_verification')

    from django.utils import timezone
    token_obj.verified_at = timezone.now()
    token_obj.save(update_fields=['verified_at'])

    # Mark user as active (they were already active, but flag the profile)
    user = token_obj.user
    user.is_active = True
    user.save(update_fields=['is_active'])

    messages.success(request, 'Email verified! You can now log in.')
    return redirect('login')


def resend_verification(request):
    """Allow users to request a new verification email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            token_obj = EmailVerificationToken.create_for_user(user)
            try:
                from apps.resumes.tasks import send_verification_email_task
                base_url = request.build_absolute_uri('/').rstrip('/')
                send_verification_email_task.delay(user.id, token_obj.token, base_url)
            except Exception as e:
                logger.warning(f'Could not queue verification email: {e}')
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists

        messages.success(request, 'If that email is registered, a new verification link has been sent.')
        return redirect('login')

    return render(request, 'authentication/resend_verification.html')

@login_required
def profile(request):
    """User profile view with editable fields and password change."""
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            if email and email != user.email:
                from django.contrib.auth.models import User as AuthUser
                if AuthUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                    messages.error(request, 'That email is already in use.')
                    return redirect('profile')
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save(update_fields=['first_name', 'last_name', 'email'])
            messages.success(request, 'Profile updated successfully.')

        elif action == 'change_password':
            from django.contrib.auth import update_session_auth_hash
            current = request.POST.get('current_password')
            new_pw = request.POST.get('new_password')
            confirm = request.POST.get('confirm_password')
            if not user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')

        return redirect('profile')

    from apps.resumes.models import Resume
    resume_count = Resume.objects.filter(user=user).count()
    context = {
        'user': user,
        'resume_count': resume_count,
    }
    return render(request, 'authentication/profile.html', context)


@login_required
def settings(request):
    """User settings view with POST handlers for danger-zone actions."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_all_resumes':
            from apps.resumes.models import Resume
            count, _ = Resume.objects.filter(user=request.user).delete()
            logger.info(f'User {request.user.username} deleted all {count} resumes.')
            messages.success(request, f'Deleted {count} resume(s) successfully.')

        elif action == 'delete_account':
            from django.contrib.auth import logout
            user = request.user
            logout(request)
            user.delete()
            logger.info(f'Account deleted for user {user.username}.')
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('login')

        elif action == 'export_data':
            import json, io, zipfile
            from apps.resumes.models import Resume
            resumes = Resume.objects.filter(user=request.user).prefetch_related(
                'personal_info', 'experiences', 'education', 'skills', 'projects', 'certifications'
            )
            export = {
                'user': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'date_joined': request.user.date_joined.isoformat(),
                },
                'resumes': []
            }
            for r in resumes:
                pi = getattr(r, 'personal_info', None)
                export['resumes'].append({
                    'title': r.title,
                    'template': r.template,
                    'created_at': r.created_at.isoformat(),
                    'personal_info': {
                        'full_name': pi.full_name if pi else '',
                        'email': pi.email if pi else '',
                        'phone': pi.phone if pi else '',
                        'location': pi.location if pi else '',
                    } if pi else {},
                    'experiences': [{
                        'company': e.company, 'role': e.role,
                        'start_date': e.start_date.isoformat(),
                        'end_date': e.end_date.isoformat() if e.end_date else None,
                        'description': e.description,
                    } for e in r.experiences.all()],
                    'education': [{
                        'institution': ed.institution, 'degree': ed.degree,
                        'field': ed.field, 'start_year': ed.start_year, 'end_year': ed.end_year,
                    } for ed in r.education.all()],
                    'skills': [{'name': s.name, 'category': s.category} for s in r.skills.all()],
                })
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('nextgencv_export.json', json.dumps(export, indent=2))
            buf.seek(0)
            from django.http import HttpResponse
            response = HttpResponse(buf.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="nextgencv_data_export.zip"'
            return response

        return redirect('settings')

    context = {'user': request.user}
    return render(request, 'authentication/settings.html', context)

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
    
    # Get real activity log
    from apps.authentication.models import ActivityLog
    recent_activities_qs = ActivityLog.objects.filter(user=request.user)[:10]
    recent_activities = []
    icon_map = {
        'resume_created': 'created', 'resume_updated': 'updated',
        'resume_analyzed': 'analyzed', 'resume_deleted': 'delete',
        'resume_exported': 'updated', 'resume_optimized': 'updated',
        'pdf_imported': 'created', 'pdf_uploaded': 'updated',
        'version_restored': 'updated', 'cover_letter_generated': 'updated',
        'application_created': 'created', 'application_updated': 'updated',
    }
    for act in recent_activities_qs:
        recent_activities.append({
            'type': icon_map.get(act.action, 'updated'),
            'description': act.description,
            'timestamp': act.created_at,
        })
    
    # Prepare chart data if user has analyses
    show_charts = False
    chart_data_json = None
    
    if resumes.exists():
        from apps.resumes.models import ResumeAnalysis
        analyses = ResumeAnalysis.objects.filter(resume__user=request.user).order_by('analysis_timestamp')
        
        if analyses.count() >= 1:
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

