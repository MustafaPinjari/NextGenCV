import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import JobApplication, CoverLetter, InterviewPrepSession, SkillGapAnalysis
from .forms import JobApplicationForm, CoverLetterForm, ScrapeJobForm
from .job_scraper import scrape_job_description
from .cover_letter_service import CoverLetterService
from .outcome_analytics import OutcomeAnalyticsService
from .interview_prep_service import InterviewPrepService
from .skill_gap_service import SkillGapService
from .salary_service import SalaryIntelligenceService
from apps.resumes.models import Resume


@login_required
def application_list(request):
    applications = JobApplication.objects.filter(user=request.user).select_related('resume')
    stats = OutcomeAnalyticsService().get_user_stats(request.user)
    return render(request, 'tracker/application_list.html', {
        'applications': applications,
        'stats': stats,
    })


@login_required
def application_create(request):
    # Pre-fill from query params (e.g. coming from resume detail page)
    initial = {
        'resume': request.GET.get('resume_id'),
        'job_url': request.GET.get('job_url', ''),
    }
    form = JobApplicationForm(request.user, request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        app = form.save(commit=False)
        app.user = request.user
        # Snapshot ATS score at time of application
        if app.resume:
            latest = app.resume.analyses.order_by('-analysis_timestamp').first()
            if latest:
                app.ats_score_at_apply = latest.final_score
        app.save()
        messages.success(request, f'Application to {app.company} saved.')
        return redirect('application_detail', pk=app.pk)

    return render(request, 'tracker/application_form.html', {'form': form, 'action': 'Add'})


@login_required
def application_detail(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    cover_letter = getattr(app, 'cover_letter', None)
    return render(request, 'tracker/application_detail.html', {
        'application': app,
        'cover_letter': cover_letter,
    })


@login_required
def application_update(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    form = JobApplicationForm(request.user, request.POST or None, instance=app)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Application updated.')
        return redirect('application_detail', pk=app.pk)
    return render(request, 'tracker/application_form.html', {'form': form, 'action': 'Edit', 'application': app})


@login_required
def application_delete(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        app.delete()
        messages.success(request, 'Application deleted.')
        return redirect('application_list')
    return render(request, 'tracker/application_confirm_delete.html', {'application': app})


@login_required
def scrape_job(request):
    """AJAX endpoint: scrape job description from a URL."""
    if request.method == 'POST':
        form = ScrapeJobForm(request.POST)
        if form.is_valid():
            result = scrape_job_description(form.cleaned_data['job_url'])
            return JsonResponse(result)
        return JsonResponse({'success': False, 'error': 'Invalid URL.'})
    return JsonResponse({'success': False, 'error': 'POST required.'})


@login_required
def generate_cover_letter(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if not app.resume:
        messages.error(request, 'Please link a resume to this application first.')
        return redirect('application_update', pk=pk)

    existing = getattr(app, 'cover_letter', None)

    if request.method == 'POST':
        form = CoverLetterForm(request.POST, instance=existing)
        if form.is_valid():
            cl = form.save(commit=False)
            cl.user = request.user
            cl.application = app
            cl.resume = app.resume
            cl.company = app.company
            cl.role = app.role
            cl.save()
            messages.success(request, 'Cover letter saved.')
            return redirect('application_detail', pk=pk)
    else:
        if existing:
            form = CoverLetterForm(instance=existing)
        else:
            # Auto-generate on first visit
            service = CoverLetterService()
            generated = service.generate(
                resume=app.resume,
                company=app.company,
                role=app.role,
                job_description=app.job_description,
            )
            form = CoverLetterForm(initial={'content': generated})

    return render(request, 'tracker/cover_letter_form.html', {
        'form': form,
        'application': app,
    })


@login_required
def outcome_dashboard(request):
    stats = OutcomeAnalyticsService().get_user_stats(request.user)
    chart_data = json.dumps({
        'score_vs_outcome': stats['score_vs_outcome'],
        'by_status': stats['by_status'],
    })
    return render(request, 'tracker/outcome_dashboard.html', {
        'stats': stats,
        'chart_data_json': chart_data,
    })


# ── INTERVIEW PREP ──────────────────────────────────────────────────────────

@login_required
def interview_prep(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    existing = InterviewPrepSession.objects.filter(application=app).first()

    if request.method == 'POST' or not existing:
        if not app.resume:
            messages.error(request, 'Link a resume to this application first.')
            return redirect('application_update', pk=pk)

        service = InterviewPrepService()
        questions = service.generate(
            resume=app.resume,
            role=app.role,
            job_description=app.job_description,
            company=app.company,
        )
        session = InterviewPrepSession.objects.update_or_create(
            application=app,
            defaults={
                'user': request.user,
                'resume': app.resume,
                'role': app.role,
                'company': app.company,
                'job_description': app.job_description,
                'questions': questions,
            }
        )[0]
        if request.method == 'POST':
            messages.success(request, 'Interview questions regenerated.')
        existing = session

    return render(request, 'tracker/interview_prep.html', {
        'application': app,
        'session': existing,
        'questions': existing.questions if existing else [],
    })


# ── SKILL GAP ANALYSIS ──────────────────────────────────────────────────────

@login_required
def skill_gap(request):
    resumes = request.user.resumes.all()

    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        target_role = request.POST.get('target_role', '').strip()
        jd_texts = [t.strip() for t in request.POST.get('job_descriptions', '').split('---') if t.strip()]

        if not resume_id or not target_role:
            messages.error(request, 'Please select a resume and enter a target role.')
            return render(request, 'tracker/skill_gap_form.html', {'resumes': resumes})

        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)

        if not jd_texts:
            jd_texts = ['']  # allow analysis with just resume skills

        service = SkillGapService()
        result = service.analyse(resume, target_role, jd_texts)

        analysis = SkillGapAnalysis.objects.create(
            user=request.user,
            resume=resume,
            target_role=target_role,
            job_descriptions=jd_texts,
            missing_skills=result['missing_skills'],
            present_skills=result['present_skills'],
            recommendations=result['recommendations'],
        )

        return render(request, 'tracker/skill_gap_result.html', {
            'analysis': analysis,
            'result': result,
            'resume': resume,
        })

    return render(request, 'tracker/skill_gap_form.html', {'resumes': resumes})


# ── SALARY INTELLIGENCE ─────────────────────────────────────────────────────

@login_required
def salary_intelligence(request):
    result = None
    role = request.GET.get('role', '')
    location = request.GET.get('location', '')

    if role:
        service = SalaryIntelligenceService()
        result = service.get_salary_range(role, location)

    # Pre-fill from application if coming from tracker
    app_id = request.GET.get('app_id')
    app = None
    if app_id:
        app = JobApplication.objects.filter(pk=app_id, user=request.user).first()
        if app and not role:
            result = SalaryIntelligenceService().get_salary_range(app.role)

    return render(request, 'tracker/salary_intelligence.html', {
        'result': result,
        'role': role or (app.role if app else ''),
        'location': location,
        'application': app,
    })


# ── FOLLOW-UP EMAIL GENERATOR ───────────────────────────────────────────────

@login_required
def followup_email(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    stage = request.GET.get('stage', 'after_apply')

    info = getattr(app.resume.personal_info, 'full_name', '') if app.resume else ''
    name = info or request.user.get_full_name() or request.user.username

    templates = {
        'after_apply': f"""Subject: Following Up on {app.role} Application — {name}

Dear Hiring Manager,

I wanted to follow up on my application for the {app.role} position at {app.company}, submitted on {app.applied_date or 'recently'}.

I remain very enthusiastic about this opportunity and believe my background aligns well with what you're looking for. I'd welcome the chance to discuss how I can contribute to your team.

Please let me know if you need any additional information. I look forward to hearing from you.

Best regards,
{name}""",

        'after_interview': f"""Subject: Thank You — {app.role} Interview at {app.company}

Dear Hiring Manager,

Thank you for taking the time to speak with me about the {app.role} role at {app.company}. I enjoyed learning more about the team and the challenges ahead.

Our conversation reinforced my excitement about this opportunity. I'm confident that my experience would allow me to make an immediate contribution.

I look forward to the next steps. Please don't hesitate to reach out if you have any further questions.

Best regards,
{name}""",

        'offer_negotiation': f"""Subject: Re: {app.role} Offer — {name}

Dear Hiring Manager,

Thank you so much for the offer to join {app.company} as {app.role}. I'm genuinely excited about this opportunity.

After careful consideration, I'd like to discuss the compensation package. Based on my research and experience, I was hoping we could explore a base salary closer to [YOUR TARGET]. I'm very flexible on other aspects of the package.

I'm committed to joining the team and am confident we can find a mutually agreeable arrangement.

Best regards,
{name}""",
    }

    email_content = templates.get(stage, templates['after_apply'])

    return render(request, 'tracker/followup_email.html', {
        'application': app,
        'email_content': email_content,
        'stage': stage,
        'stages': [
            ('after_apply', 'After Applying'),
            ('after_interview', 'After Interview'),
            ('offer_negotiation', 'Offer Negotiation'),
        ],
    })


# ── REJECTION ANALYSIS ──────────────────────────────────────────────────────

@login_required
def rejection_analysis(request):
    rejected = JobApplication.objects.filter(user=request.user, status='rejected')
    total_rejected = rejected.count()

    if total_rejected == 0:
        return render(request, 'tracker/rejection_analysis.html', {
            'total_rejected': 0, 'patterns': [], 'suggestions': []
        })

    # Pattern: rejection by ATS score bucket
    score_buckets = {'0-40': 0, '41-60': 0, '61-75': 0, '76+': 0}
    for app in rejected:
        s = app.ats_score_at_apply or 0
        if s <= 40:
            score_buckets['0-40'] += 1
        elif s <= 60:
            score_buckets['41-60'] += 1
        elif s <= 75:
            score_buckets['61-75'] += 1
        else:
            score_buckets['76+'] += 1

    # Pattern: rejection by stage (no response = screening rejection)
    stage_pattern = {
        'no_response': rejected.filter(notes='').count(),
        'after_screening': rejected.exclude(notes='').count(),
    }

    # Most common roles rejected
    from django.db.models import Count
    common_roles = (
        rejected.values('role')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
    )

    # Build suggestions
    suggestions = []
    most_rejections_bucket = max(score_buckets, key=score_buckets.get)
    if most_rejections_bucket in ('0-40', '41-60'):
        suggestions.append({
            'icon': 'bi-graph-up',
            'text': f"Most rejections happened with ATS scores below 60. Use 'Fix My Resume' to optimize for each job description before applying.",
            'priority': 'high',
        })
    if score_buckets['76+'] > 0:
        suggestions.append({
            'icon': 'bi-person-check',
            'text': "You're getting rejected even with high ATS scores — this suggests the issue may be at the interview stage, not the resume.",
            'priority': 'medium',
        })
    if total_rejected >= 5:
        suggestions.append({
            'icon': 'bi-briefcase',
            'text': "Consider broadening your search to adjacent roles or companies where your skills transfer well.",
            'priority': 'low',
        })

    return render(request, 'tracker/rejection_analysis.html', {
        'total_rejected': total_rejected,
        'score_buckets': score_buckets,
        'stage_pattern': stage_pattern,
        'common_roles': common_roles,
        'suggestions': suggestions,
    })
