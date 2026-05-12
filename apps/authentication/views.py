from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import EmailVerificationToken
import logging

logger = logging.getLogger(__name__)


def _rate_limit_check(request, group: str, rate: str = '10/m') -> bool:
    """Returns True if the request is rate-limited. Soft-fails if django-ratelimit not installed."""
    try:
        from ratelimit.utils import is_ratelimited
        return is_ratelimited(request, group=group, key='ip', rate=rate, method='POST', increment=True)
    except ImportError:
        return False


def register(request):
    """User registration view — creates account and sends verification email."""
    if request.method == 'POST':
        if _rate_limit_check(request, group='register', rate='5/m'):
            messages.error(request, 'Too many registration attempts. Please wait a minute.')
            return render(request, 'authentication/register.html', {'form': UserRegistrationForm()})
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

    # Mark user as active
    user = token_obj.user
    user.is_active = True
    user.save(update_fields=['is_active'])

    # Send welcome email now that email is confirmed
    try:
        from apps.resumes.tasks import send_welcome_email_task
        base_url = request.build_absolute_uri('/').rstrip('/')
        send_welcome_email_task.delay(user.id, base_url)
    except Exception as e:
        logger.warning(f'Could not queue welcome email for {user.username}: {e}')

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
    """User dashboard view — enriched with tracker stats and score breakdown."""
    from apps.resumes.services import ResumeService
    from apps.analytics.services.analytics_service import AnalyticsService
    from apps.resumes.models import ResumeAnalysis
    from apps.tracker.models import JobApplication
    from django.utils import timezone
    from django.db.models import Avg, Count, Q
    import json

    resumes = ResumeService.get_user_resumes(request.user)
    # Slice at DB level (LIMIT 3 in SQL) — don't fetch all then slice in template
    resumes_for_display = resumes[:3]

    # ── Resume health & ATS score ─────────────────────────────────────────────
    resume_health = None
    average_score = None
    score_breakdown = None

    if resumes.exists():
        latest_resume = resumes.first()
        resume_health = AnalyticsService.calculate_resume_health(latest_resume)

        analyses_qs = ResumeAnalysis.objects.filter(resume__user=request.user)
        if analyses_qs.exists():
            agg = analyses_qs.aggregate(Avg('final_score'))
            average_score = round(agg['final_score__avg'], 1) if agg['final_score__avg'] else None

            # Latest analysis breakdown for radar/bar chart
            latest_analysis = analyses_qs.order_by('-analysis_timestamp').first()
            if latest_analysis:
                score_breakdown = {
                    'keyword_match': round(latest_analysis.keyword_match_score, 1),
                    'skill_relevance': round(latest_analysis.skill_relevance_score, 1),
                    'section_completeness': round(latest_analysis.section_completeness_score, 1),
                    'experience_impact': round(latest_analysis.experience_impact_score, 1),
                    'quantification': round(latest_analysis.quantification_score, 1),
                    'action_verbs': round(latest_analysis.action_verb_score, 1),
                }

    # ── Job tracker stats ─────────────────────────────────────────────────────
    apps_qs = JobApplication.objects.filter(user=request.user)
    tracker_stats = {
        'total': apps_qs.count(),
        'applied': apps_qs.filter(status__in=['applied', 'interview', 'offer', 'rejected']).count(),
        'interviews': apps_qs.filter(status__in=['interview', 'offer']).count(),
        'offers': apps_qs.filter(status='offer').count(),
    }
    tracker_stats['callback_rate'] = (
        round(tracker_stats['interviews'] / tracker_stats['applied'] * 100, 1)
        if tracker_stats['applied'] else 0
    )
    recent_apps = list(apps_qs.select_related('resume').order_by('-updated_at')[:4].values(
        'id', 'company', 'role', 'status', 'updated_at', 'ats_score_at_apply'
    ))

    # ── Activity log ──────────────────────────────────────────────────────────
    from apps.authentication.models import ActivityLog
    icon_map = {
        'resume_created': 'created', 'resume_updated': 'updated',
        'resume_analyzed': 'analyzed', 'resume_deleted': 'delete',
        'resume_exported': 'updated', 'resume_optimized': 'updated',
        'pdf_imported': 'created', 'pdf_uploaded': 'updated',
        'version_restored': 'updated', 'cover_letter_generated': 'updated',
        'application_created': 'created', 'application_updated': 'updated',
    }
    recent_activities = [
        {
            'type': icon_map.get(act.action, 'updated'),
            'description': act.description,
            'timestamp': act.created_at,
            'action': act.action,
        }
        for act in ActivityLog.objects.filter(user=request.user)[:8]
    ]

    # ── Score trend chart ─────────────────────────────────────────────────────
    show_charts = False
    chart_data_json = None

    if resumes.exists():
        analyses = ResumeAnalysis.objects.filter(
            resume__user=request.user
        ).order_by('analysis_timestamp')[:12]

        if analyses.count() >= 1:
            show_charts = True
            chart_data_json = json.dumps({
                'score_trend': {
                    'labels': [a.analysis_timestamp.strftime('%b %d') for a in analyses],
                    'scores': [float(a.final_score) for a in analyses],
                },
                'breakdown': score_breakdown or {},
            })

    context = {
        'user': request.user,
        'resumes': resumes,
        'resumes_for_display': resumes_for_display,
        'resume_health': resume_health,
        'average_score': average_score,
        'score_breakdown': score_breakdown,
        'tracker_stats': tracker_stats,
        'recent_apps': recent_apps,
        'recent_activities': recent_activities,
        'show_charts': show_charts,
        'chart_data_json': chart_data_json,
        'current_date': timezone.now(),
        'is_new_user': not resumes.exists(),
    }
    return render(request, 'authentication/dashboard_new.html', context)

