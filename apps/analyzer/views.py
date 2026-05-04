from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from apps.resumes.models import Resume
from .forms import JobDescriptionForm
from .services import ATSAnalyzerService
import logging

logger = logging.getLogger(__name__)


def _compute_completeness(resume):
    """Return 0-100 completeness score based on filled sections."""
    score = 0
    try:
        pi = resume.personal_info
        if pi.full_name: score += 10
        if pi.email: score += 8
        if pi.phone: score += 4
        if pi.location: score += 4
        if pi.linkedin: score += 4
    except Exception:
        pass
    if resume.summary: score += 10
    if resume.experiences.exists(): score += 20
    if resume.education.exists(): score += 15
    if resume.skills.exists(): score += 10
    if resume.projects.exists(): score += 8
    try:
        if resume.certifications.exists(): score += 7
    except Exception:
        pass
    return min(score, 100)


@login_required
def analyze_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    if resume.user != request.user:
        logger.warning(f'Unauthorized: {request.user.username} tried to analyze resume {resume_id}')
        return HttpResponseForbidden("You do not have permission to access this resume.")

    analysis_result = None

    # Load saved job descriptions for this user
    from apps.authentication.models import SavedJobDescription
    saved_jds = SavedJobDescription.objects.filter(user=request.user)[:8]

    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.cleaned_data['job_description']

            # Auto-save JD if user checked the box
            if request.POST.get('save_jd'):
                jd_title = request.POST.get('jd_title', '').strip() or job_description[:60] + '...'
                SavedJobDescription.objects.update_or_create(
                    user=request.user,
                    content=job_description,
                    defaults={'title': jd_title, 'last_used_at': __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()}
                )

            # Update last_used_at if loading a saved JD
            saved_id = request.POST.get('load_saved_jd')
            if saved_id:
                from django.utils import timezone
                SavedJobDescription.objects.filter(id=saved_id, user=request.user).update(last_used_at=timezone.now())
            try:
                analysis_result = ATSAnalyzerService.analyze_resume(resume_id, job_description)

                if analysis_result:
                    score_decimal = analysis_result['score'] / 100
                    analysis_result['stroke_dashoffset'] = 452.39 * (1 - score_decimal)

                    # Save score back to Resume (no duplicate analyses)
                    from apps.resumes.models import ResumeAnalysis
                    from django.utils import timezone
                    ResumeAnalysis.objects.update_or_create(
                        resume=resume,
                        job_description=job_description,
                        defaults={
                            'keyword_match_score': analysis_result['score'],
                            'skill_relevance_score': analysis_result['score'],
                            'section_completeness_score': analysis_result['score'],
                            'experience_impact_score': analysis_result['score'],
                            'quantification_score': analysis_result['score'],
                            'action_verb_score': analysis_result['score'],
                            'final_score': analysis_result['score'],
                            'matched_keywords': analysis_result['matched_keywords'],
                            'missing_keywords': analysis_result['missing_keywords'],
                            'suggestions': analysis_result['suggestions'],
                        }
                    )
                    # Cache score + completeness on Resume row
                    resume.latest_ats_score = round(analysis_result['score'], 1)
                    resume.last_analyzed_at = timezone.now()
                    resume.completeness_score = _compute_completeness(resume)
                    resume.save(update_fields=['latest_ats_score', 'last_analyzed_at', 'completeness_score'])

                from apps.authentication.models import ActivityLog
                ActivityLog.log(
                    request.user, 'resume_analyzed',
                    f'Analyzed "{resume.title}" — score {round(analysis_result["score"], 1)}',
                    resume=resume,
                    metadata={'score': analysis_result['score']}
                )
                logger.info(f'ATS analysis completed for resume {resume_id} by {request.user.username}')
                messages.success(request, 'Resume analysis completed successfully!')
            except Exception as e:
                logger.error(f'ATS analysis failed for resume {resume_id}: {str(e)}', exc_info=True)
                messages.error(request, f'Analysis failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = JobDescriptionForm()

    context = {
        'form': form,
        'resume': resume,
        'analysis_result': analysis_result,
        'saved_jds': saved_jds,
    }
    return render(request, 'analyzer/analyze_new.html', context)
