from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from apps.resumes.models import Resume
from .forms import JobDescriptionForm
from .services import ATSAnalyzerService
import logging

logger = logging.getLogger(__name__)


@login_required
def analyze_resume(request, resume_id):
    """
    Analyze resume against job description using ATS keyword matching.
    
    Displays a form for job description input and shows analysis results
    including match score, matched keywords, missing keywords, and suggestions.
    
    Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6
    """
    # Get the resume and verify ownership
    resume = get_object_or_404(Resume, id=resume_id)
    
    # Authorization check - ensure resume belongs to authenticated user
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to analyze resume {resume_id} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to access this resume.")
    
    analysis_result = None
    
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.cleaned_data['job_description']
            
            # Call the ATS analyzer service
            try:
                analysis_result = ATSAnalyzerService.analyze_resume(resume_id, job_description)
                
                # Calculate stroke-dashoffset for circular progress (452.39 is circumference for r=72)
                # Formula: circumference * (1 - score/100)
                if analysis_result:
                    score_decimal = analysis_result['score'] / 100
                    analysis_result['stroke_dashoffset'] = 452.39 * (1 - score_decimal)
                
                logger.info(f'ATS analysis completed for resume {resume_id} by user {request.user.username}')
                messages.success(request, 'Resume analysis completed successfully!')
            except Exception as e:
                # Handle any analysis errors
                logger.error(f'ATS analysis failed for resume {resume_id}: {str(e)}', exc_info=True)
                messages.error(request, f"Analysis failed: {str(e)}")
                form.add_error(None, f"Analysis failed: {str(e)}")
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = JobDescriptionForm()
    
    context = {
        'form': form,
        'resume': resume,
        'analysis_result': analysis_result,
    }
    
    # Use new redesigned template
    return render(request, 'analyzer/analyze_new.html', context)
