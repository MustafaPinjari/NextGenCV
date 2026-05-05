from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.db import models, transaction
from django.utils import timezone
from .services import ResumeService
from .models import Resume, UploadedResume
from .services.pdf_parser import PDFParserService
from .services.section_parser import SectionParserService
from .utils.file_validators import validate_pdf_file, has_embedded_scripts
import logging
import re

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def resume_list(request):
    from django.core.paginator import Paginator
    from django.utils import timezone

    all_resumes = ResumeService.get_user_resumes(request.user)

    # Update completeness scores in bulk (cheap, no external calls)
    from apps.analyzer.views import _compute_completeness
    for r in all_resumes:
        new_score = _compute_completeness(r)
        if r.completeness_score != new_score:
            r.completeness_score = new_score
            r.save(update_fields=['completeness_score'])

    paginator = Paginator(all_resumes, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'resumes': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'resumes/resume_list.html', context)

@login_required
def resume_create(request):
    """
    Create new resume using a multi-step wizard interface.
    Stores data in session across steps.
    """
    # Initialize session data if not exists
    if 'resume_wizard' not in request.session:
        request.session['resume_wizard'] = {
            'step': 1,
            'data': {}
        }
        request.session.modified = True
    # Force session to be saved on every request (prevents data loss on refresh)
    request.session.modified = True
    
    wizard_data = request.session['resume_wizard']
    current_step = wizard_data['step']
    
    # Log current wizard state for debugging
    logger.debug(f'Wizard Step {current_step}, Data keys: {list(wizard_data["data"].keys())}')
    
    if request.method == 'POST':
        # Handle form submission based on current step
        if current_step == 1:
            # Step 1: Personal information
            from .forms import PersonalInfoForm
            form = PersonalInfoForm(request.POST)
            if form.is_valid():
                wizard_data['data']['personal_info'] = {
                    'full_name': form.cleaned_data['full_name'],
                    'phone': form.cleaned_data['phone'],
                    'email': form.cleaned_data['email'],
                    'linkedin': form.cleaned_data['linkedin'],
                    'github': form.cleaned_data['github'],
                    'location': form.cleaned_data['location']
                }
                wizard_data['step'] = 2
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 2:
            # Step 2: Experience entries
            action = request.POST.get('action')
            if action == 'add_experience':
                from .forms import ExperienceForm
                form = ExperienceForm(request.POST)
                if form.is_valid():
                    if 'experiences' not in wizard_data['data']:
                        wizard_data['data']['experiences'] = []
                    wizard_data['data']['experiences'].append({
                        'company': form.cleaned_data['company'],
                        'role': form.cleaned_data['role'],
                        'start_date': form.cleaned_data['start_date'].isoformat(),
                        'end_date': form.cleaned_data['end_date'].isoformat() if form.cleaned_data['end_date'] else None,
                        'description': form.cleaned_data['description']
                    })
                    request.session.modified = True
                    messages.success(request, 'Experience added successfully!')
                    return redirect('resume_create')
            elif action == 'next':
                wizard_data['step'] = 3
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 3:
            # Step 3: Education entries
            action = request.POST.get('action')
            if action == 'add_education':
                from .forms import EducationForm
                form = EducationForm(request.POST)
                if form.is_valid():
                    if 'education' not in wizard_data['data']:
                        wizard_data['data']['education'] = []
                    wizard_data['data']['education'].append({
                        'institution': form.cleaned_data['institution'],
                        'degree': form.cleaned_data['degree'],
                        'field': form.cleaned_data['field'],
                        'start_year': form.cleaned_data['start_year'],
                        'end_year': form.cleaned_data['end_year']
                    })
                    request.session.modified = True
                    messages.success(request, 'Education added successfully!')
                    return redirect('resume_create')
            elif action == 'next':
                wizard_data['step'] = 4
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 4:
            # Step 4: Skills
            action = request.POST.get('action')
            if action == 'add_skill':
                from .forms import SkillForm
                form = SkillForm(request.POST)
                if form.is_valid():
                    if 'skills' not in wizard_data['data']:
                        wizard_data['data']['skills'] = []
                    wizard_data['data']['skills'].append({
                        'name': form.cleaned_data['name'],
                        'category': form.cleaned_data['category']
                    })
                    request.session.modified = True
                    messages.success(request, 'Skill added successfully!')
                    return redirect('resume_create')
            elif action == 'next':
                wizard_data['step'] = 5
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 5:
            # Step 5: Summary and finish
            action = request.POST.get('action')
            if action == 'save' or action == 'next' or 'finish' in request.POST:
                # Get summary if provided
                summary = request.POST.get('summary', '')
                if summary:
                    wizard_data['data']['summary'] = summary
                    request.session.modified = True
                
                # Log wizard data for debugging
                logger.info(f'Creating resume with wizard data: {wizard_data["data"]}')
                
                # Convert date strings back to date objects for experiences
                from datetime import date
                if 'experiences' in wizard_data['data']:
                    for exp in wizard_data['data']['experiences']:
                        try:
                            if isinstance(exp['start_date'], str) and exp['start_date']:
                                exp['start_date'] = date.fromisoformat(exp['start_date'])
                            if exp.get('end_date') and isinstance(exp['end_date'], str):
                                exp['end_date'] = date.fromisoformat(exp['end_date'])
                        except (ValueError, TypeError):
                            pass  # Keep as string if parsing fails
                
                # Set default title and template if not provided
                if 'title' not in wizard_data['data']:
                    wizard_data['data']['title'] = f"{wizard_data['data'].get('personal_info', {}).get('full_name', 'My')} Resume"
                if 'template' not in wizard_data['data']:
                    wizard_data['data']['template'] = 'professional'
                
                # Mark resume as complete (not draft) - Requirements: 4.2, 5.1, 5.5
                wizard_data['data']['is_draft'] = False
                
                # Create the resume
                resume = ResumeService.create_resume(request.user, wizard_data['data'])

                # Log activity
                from apps.authentication.models import ActivityLog
                ActivityLog.log(request.user, 'resume_created', f'Created resume "{resume.title}"', resume=resume)

                # Log what was created
                logger.info(f'Resume created: ID={resume.id}, Experiences={resume.experiences.count()}, Education={resume.education.count()}, Skills={resume.skills.count()}')
                
                # Clear wizard data
                del request.session['resume_wizard']
                request.session.modified = True
                
                # Requirement: 5.3 - Display success message
                messages.success(request, 'Resume created successfully!')
                
                # Requirement: 5.2 - Redirect to resume detail page
                return redirect('resume_detail', pk=resume.id)
    
    # Handle back button
    if request.GET.get('back'):
        if current_step > 1:
            wizard_data['step'] = current_step - 1
            request.session.modified = True
            return redirect('resume_create')
    
    # Handle AJAX requests for autosave and AI generation
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        import json
        from django.http import JsonResponse
        from django.template.loader import render_to_string
        
        # Handle real-time preview updates
        if request.POST.get('preview_update'):
            # Update wizard data with current form values for ALL steps
            if current_step == 1:
                wizard_data['data']['personal_info'] = {
                    'full_name': request.POST.get('full_name', ''),
                    'email': request.POST.get('email', ''),
                    'phone': request.POST.get('phone', ''),
                    'location': request.POST.get('location', ''),
                    'linkedin': request.POST.get('linkedin', ''),
                    'github': request.POST.get('github', '')
                }
            elif current_step == 2:
                # Show current form values in preview (not yet saved)
                preview_exp = list(wizard_data['data'].get('experiences', []))
                current = {
                    'company': request.POST.get('company', ''),
                    'role': request.POST.get('role', ''),
                    'start_date': request.POST.get('start_date', ''),
                    'end_date': request.POST.get('end_date', ''),
                    'description': request.POST.get('description', ''),
                }
                if current['company'] or current['role']:
                    # Show as a "draft" entry in preview
                    wizard_data['data']['_preview_exp'] = current
            elif current_step == 3:
                preview_edu = list(wizard_data['data'].get('education', []))
                current = {
                    'institution': request.POST.get('institution', ''),
                    'degree': request.POST.get('degree', ''),
                    'field': request.POST.get('field', ''),
                    'start_year': request.POST.get('start_year', ''),
                    'end_year': request.POST.get('end_year', ''),
                }
                if current['institution'] or current['degree']:
                    wizard_data['data']['_preview_edu'] = current
            elif current_step == 4:
                current_skill = {
                    'name': request.POST.get('name', ''),
                    'category': request.POST.get('category', ''),
                }
                if current_skill['name']:
                    wizard_data['data']['_preview_skill'] = current_skill
            elif current_step == 5:
                wizard_data['data']['summary'] = request.POST.get('summary', '')
            
            request.session.modified = True
            
            # Build preview data including draft entries
            preview_data = dict(wizard_data['data'])
            
            # Merge draft experience into preview
            if '_preview_exp' in preview_data:
                draft = preview_data.pop('_preview_exp')
                if draft.get('company') or draft.get('role'):
                    exps = list(preview_data.get('experiences', []))
                    exps_preview = exps + [draft]
                    preview_data['experiences'] = exps_preview
            
            # Merge draft education into preview
            if '_preview_edu' in preview_data:
                draft = preview_data.pop('_preview_edu')
                if draft.get('institution') or draft.get('degree'):
                    edus = list(preview_data.get('education', []))
                    preview_data['education'] = edus + [draft]
            
            # Merge draft skill into preview
            if '_preview_skill' in preview_data:
                draft = preview_data.pop('_preview_skill')
                if draft.get('name'):
                    skills = list(preview_data.get('skills', []))
                    preview_data['skills'] = skills + [draft]
            
            # Render preview HTML
            preview_html = render_to_string('resumes/partials/wizard_preview.html', {
                'wizard_data': preview_data
            })
            
            return JsonResponse({
                'success': True,
                'preview_html': preview_html
            })
        
        if request.POST.get('autosave'):
            # Save current form data to session
            request.session.modified = True
            return JsonResponse({'success': True, 'message': 'Autosaved'})
        
        if request.POST.get('save_draft'):
            # Save draft (same as autosave for now)
            request.session.modified = True
            return JsonResponse({'success': True, 'message': 'Draft saved'})
        
        # Requirement: 4.4 - AI summary generation endpoint
        if request.POST.get('action') == 'generate_summary':
            try:
                # Generate AI summary based on experience and skills
                summary = generate_ai_summary(wizard_data['data'])
                return JsonResponse({'summary': summary, 'success': True})
            except Exception as e:
                logger.error(f'Failed to generate AI summary: {str(e)}', exc_info=True)
                return JsonResponse({
                    'success': False, 
                    'error': 'Failed to generate summary. Please try again.'
                }, status=500)
    
    # Prepare context based on current step
    context = {
        'step': current_step,
        'wizard_data': wizard_data['data']
    }
    
    # Add appropriate form and template for current step
    if current_step == 1:
        from .forms import PersonalInfoForm
        context['form'] = PersonalInfoForm(initial=wizard_data['data'].get('personal_info', {}))
        return render(request, 'resumes/wizard_steps/step1_personal.html', context)
    elif current_step == 2:
        from .forms import ExperienceForm
        context['form'] = ExperienceForm()
        context['experiences'] = wizard_data['data'].get('experiences', [])
        
        # Handle remove experience action
        if request.POST.get('action') == 'remove_experience':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(context['experiences']):
                wizard_data['data']['experiences'].pop(index)
                request.session.modified = True
                messages.success(request, 'Experience removed successfully!')
                return redirect('resume_create')
        
        return render(request, 'resumes/wizard_steps/step2_experience.html', context)
    elif current_step == 3:
        from .forms import EducationForm
        context['form'] = EducationForm()
        context['education'] = wizard_data['data'].get('education', [])
        
        # Handle remove education action
        if request.POST.get('action') == 'remove_education':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(context['education']):
                wizard_data['data']['education'].pop(index)
                request.session.modified = True
                messages.success(request, 'Education removed successfully!')
                return redirect('resume_create')
        
        return render(request, 'resumes/wizard_steps/step3_education.html', context)
    elif current_step == 4:
        from .forms import SkillForm
        context['form'] = SkillForm()
        context['skills'] = wizard_data['data'].get('skills', [])
        
        # Handle remove skill action
        if request.POST.get('action') == 'remove_skill':
            index = int(request.POST.get('index', -1))
            if 0 <= index < len(context['skills']):
                wizard_data['data']['skills'].pop(index)
                request.session.modified = True
                messages.success(request, 'Skill removed successfully!')
                return redirect('resume_create')
        
        return render(request, 'resumes/wizard_steps/step4_skills.html', context)
    elif current_step == 5:
        from .forms import SummaryForm
        context['form'] = SummaryForm(initial={'summary': wizard_data['data'].get('summary', '')})
        return render(request, 'resumes/wizard_steps/step5_summary.html', context)
    
    # Fallback to old template if step is out of range
    return render(request, 'resumes/resume_create.html', context)


def generate_ai_summary(wizard_data):
    """
    Generate an AI-powered professional summary based on user data.
    
    Requirement: 4.4 - Generate AI summary based on experience and skills
    
    Args:
        wizard_data: Dictionary containing user's resume data
        
    Returns:
        str: Generated professional summary
    """
    # This is a placeholder. In production, this would call an AI service
    experiences = wizard_data.get('experiences', [])
    skills = wizard_data.get('skills', [])
    education = wizard_data.get('education', [])
    
    # Build a simple summary based on available data
    summary_parts = []
    
    if experiences:
        years = len(experiences)
        latest_role = experiences[0].get('role', 'Professional')
        summary_parts.append(f"Experienced {latest_role} with {years}+ years in the industry")
    
    if skills:
        skill_names = [s['name'] for s in skills[:3]]
        if skill_names:
            summary_parts.append(f"skilled in {', '.join(skill_names)}")
    
    if education:
        latest_edu = education[0]
        degree = latest_edu.get('degree', '')
        field = latest_edu.get('field', '')
        if degree and field:
            summary_parts.append(f"holding a {degree} in {field}")
    
    if summary_parts:
        return '. '.join(summary_parts) + '. Seeking opportunities to leverage expertise and drive impactful results.'
    else:
        return "Motivated professional with a proven track record of success. Seeking opportunities to contribute skills and expertise to a dynamic team."

@login_required
def resume_detail(request, pk):
    """
    View resume detail with preview.
    Render resume using selected template.
    Verify resume belongs to authenticated user.
    """
    # Optimize query with prefetch_related to reduce database hits
    resume = get_object_or_404(
        Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects',
            'certifications',
        ),
        id=pk
    )
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to view resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to view this resume.")
    
    # Prepare context for template rendering
    context = {
        'resume': resume,
        'personal_info': getattr(resume, 'personal_info', None),
        'experiences': resume.experiences.all(),
        'education': resume.education.all(),
        'skills': resume.skills.all(),
        'projects': resume.projects.all(),
        'certifications': resume.certifications.all(),
    }
    
    # Check if user wants to view the formatted template preview
    view_mode = request.GET.get('view', 'preview')
    
    if view_mode == 'template':
        # Render using the selected template (e.g., professional.html)
        template_name = f'resumes/{resume.template}.html'
        return render(request, template_name, context)
    else:
        # Default: show the detail view with action buttons
        return render(request, 'resumes/resume_detail_new.html', context)

@login_required
def resume_update(request, pk):
    """
    Update existing resume with all sections.
    Load existing data and allow editing.
    """
    # Optimize query with prefetch_related to reduce database hits
    resume = get_object_or_404(
        Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        ),
        id=pk
    )
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to edit resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import ResumeForm, PersonalInfoForm
        from datetime import date
        
        # Prepare data for update
        data = {
            'title': request.POST.get('title'),
            'template': request.POST.get('template')
        }
        
        # Personal info
        if request.POST.get('full_name'):
            data['personal_info'] = {
                'full_name': request.POST.get('full_name'),
                'phone': request.POST.get('phone', ''),
                'email': request.POST.get('email'),
                'linkedin': request.POST.get('linkedin', ''),
                'github': request.POST.get('github', ''),
                'location': request.POST.get('location', '')
            }
        
        # Update the resume
        ResumeService.update_resume(pk, data)
        # Log activity
        from apps.authentication.models import ActivityLog
        ActivityLog.log(request.user, 'resume_updated', f'Updated resume "{resume.title}"', resume=resume)
        messages.success(request, 'Resume updated successfully!')
        return redirect('resume_detail', pk=pk)
    
    # GET request - load existing data
    context = {
        'resume': resume,
        'personal_info': getattr(resume, 'personal_info', None),
        'experiences': resume.experiences.all(),
        'education': resume.education.all(),
        'skills': resume.skills.all(),
        'projects': resume.projects.all()
    }
    
    return render(request, 'resumes/resume_update_new.html', context)

@login_required
def resume_delete(request, pk):
    """
    Delete resume with confirmation prompt.
    Cascades to all associated sections.
    """
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to delete resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to delete this resume.")
    
    if request.method == 'POST':
        # User confirmed deletion
        resume_title = resume.title
        ResumeService.delete_resume(pk)
        from apps.authentication.models import ActivityLog
        ActivityLog.log(request.user, 'resume_deleted', f'Deleted resume "{resume_title}"')
        messages.success(request, f'Resume "{resume_title}" has been deleted successfully.')
        return redirect('resume_list')
    
    # GET request - show confirmation page
    context = {
        'resume': resume
    }
    return render(request, 'resumes/resume_delete.html', context)

@login_required
def resume_duplicate(request, pk):
    """
    Duplicate an existing resume.
    Verify resume belongs to authenticated user.
    Redirects to edit page after duplication.
    
    Requirements: 25.1, 25.2, 25.3, 25.4, 25.5, 25.6
    """
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to duplicate resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to duplicate this resume.")
    
    # Duplicate the resume (uses optimized query with prefetch_related)
    duplicate = ResumeService.duplicate_resume(pk)
    messages.success(request, f'Resume duplicated successfully as "{duplicate.title}"')
    
    # Redirect to edit page (Requirement: 25.5)
    return redirect('resume_update', pk=duplicate.id)

@login_required
def resume_export(request, pk):
    """
    Export resume to PDF.
    Verify resume belongs to authenticated user.
    Calls PDFExportService to generate PDF and returns as downloadable file.
    Supports optional version parameter to export specific version.
    
    Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
    """
    from .pdf_service import PDFExportService
    from .models import ResumeVersion
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    version_number = None
    
    if version_id:
        # Get version number for filename (Requirement: 16.3)
        try:
            version = ResumeVersion.objects.get(id=version_id, resume=resume)
            version_number = version.version_number
        except ResumeVersion.DoesNotExist:
            messages.error(request, 'Version not found.')
            return redirect('resume_detail', pk=pk)
    
    try:
        # Generate PDF using the service (Requirement: 16.2, 16.4)
        pdf_bytes, resume = PDFExportService.generate_pdf(pk, version_id=version_id)
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        
        # Set headers for download with version number in filename (Requirement: 16.3)
        filename = f"{resume.title.replace(' ', '_')}"
        if version_number:
            filename += f"_v{version_number}"
        
        # Check if WeasyPrint fell back to HTML
        if getattr(resume, '_pdf_fallback', False):
            filename += ".html"
            response = HttpResponse(pdf_bytes, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            messages.warning(request, 'PDF export requires GTK libraries on Windows. Downloaded as HTML instead. Open in browser and use Ctrl+P to print as PDF.')
        else:
            filename += ".pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'PDF generated successfully for resume {pk}' + 
                   (f' version {version_number}' if version_number else '') +
                   f' by user {request.user.username}')
        return response
        
    except Exception as e:
        # Handle errors gracefully
        logger.error(f'PDF generation failed for resume {pk}: {str(e)}', exc_info=True)
        messages.error(request, f'Unable to generate PDF: {str(e)}')
        return redirect('resume_detail', pk=pk)


@login_required
def resume_export_docx(request, pk):
    """
    Export resume to DOCX (Word document).
    Verify resume belongs to authenticated user.
    Supports optional version parameter to export specific version.
    
    Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 21.2, 21.5, 21.6
    """
    from .services.docx_export_service import DOCXExportService
    from .models import ResumeVersion
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    version_number = None
    
    if version_id:
        # Get version number for filename (Requirement: 16.3)
        try:
            version = ResumeVersion.objects.get(id=version_id, resume=resume)
            version_number = version.version_number
        except ResumeVersion.DoesNotExist:
            messages.error(request, 'Version not found.')
            return redirect('resume_detail', pk=pk)
    
    try:
        # Generate DOCX using the service (Requirement: 16.2, 16.4)
        docx_bytes, resume = DOCXExportService.generate_docx(pk, version_id=version_id)
        
        # Create HTTP response with DOCX content
        response = HttpResponse(
            docx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Set headers for download with version number in filename (Requirement: 16.3)
        filename = f"{resume.title.replace(' ', '_')}"
        if version_number:
            filename += f"_v{version_number}"
        filename += ".docx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'DOCX generated successfully for resume {pk}' +
                   (f' version {version_number}' if version_number else '') +
                   f' by user {request.user.username}')
        return response
        
    except Exception as e:
        # Handle errors gracefully
        logger.error(f'DOCX generation failed for resume {pk}: {str(e)}', exc_info=True)
        messages.error(request, f'Unable to generate DOCX: {str(e)}')
        return redirect('resume_detail', pk=pk)


@login_required
def resume_export_text(request, pk):
    """
    Export resume to plain text format.
    Verify resume belongs to authenticated user.
    Optimized for ATS parsing.
    Supports optional version parameter to export specific version.
    
    Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 21.3, 21.6
    """
    from .services.text_export_service import TextExportService
    from .models import ResumeVersion
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    version_number = None
    
    if version_id:
        # Get version number for filename (Requirement: 16.3)
        try:
            version = ResumeVersion.objects.get(id=version_id, resume=resume)
            version_number = version.version_number
        except ResumeVersion.DoesNotExist:
            messages.error(request, 'Version not found.')
            return redirect('resume_detail', pk=pk)
    
    try:
        # Generate plain text using the service (Requirement: 16.2, 16.4)
        text_content, resume = TextExportService.generate_text(pk, version_id=version_id)
        
        # Create HTTP response with plain text content
        response = HttpResponse(text_content, content_type='text/plain; charset=utf-8')
        
        # Set headers for download with version number in filename (Requirement: 16.3)
        filename = f"{resume.title.replace(' ', '_')}"
        if version_number:
            filename += f"_v{version_number}"
        filename += ".txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'Plain text generated successfully for resume {pk}' +
                   (f' version {version_number}' if version_number else '') +
                   f' by user {request.user.username}')
        return response
        
    except Exception as e:
        # Handle errors gracefully
        logger.error(f'Plain text generation failed for resume {pk}: {str(e)}', exc_info=True)
        messages.error(request, f'Unable to generate plain text: {str(e)}')
        return redirect('resume_detail', pk=pk)


@login_required
def batch_export(request):
    """
    Export multiple resumes in a single ZIP file.
    Supports multiple formats (PDF, DOCX, TXT).
    
    POST parameters:
    - resume_ids: List of resume IDs to export
    - format: Export format ('pdf', 'docx', 'txt', or 'all')
    
    Requirements: 22.1, 22.4
    """
    import zipfile
    import io
    from .pdf_service import PDFExportService
    from .services.docx_export_service import DOCXExportService
    from .services.text_export_service import TextExportService
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('resume_list')
    
    # Get resume IDs from POST data
    resume_ids = request.POST.getlist('resume_ids')
    export_format = request.POST.get('format', 'pdf')
    
    if not resume_ids:
        messages.error(request, 'Please select at least one resume to export.')
        return redirect('resume_list')
    
    # Validate that all resumes belong to the user
    resumes = Resume.objects.filter(id__in=resume_ids, user=request.user)
    
    if resumes.count() != len(resume_ids):
        messages.error(request, 'Some selected resumes do not exist or do not belong to you.')
        return redirect('resume_list')
    
    try:
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            failed_exports = []
            
            for resume in resumes:
                resume_filename_base = f"{resume.title.replace(' ', '_')}"
                
                try:
                    # Export in requested format(s)
                    if export_format in ['pdf', 'all']:
                        pdf_bytes, _ = PDFExportService.generate_pdf(resume.id)
                        zip_file.writestr(f"{resume_filename_base}.pdf", pdf_bytes)
                    
                    if export_format in ['docx', 'all']:
                        docx_bytes, _ = DOCXExportService.generate_docx(resume.id)
                        zip_file.writestr(f"{resume_filename_base}.docx", docx_bytes)
                    
                    if export_format in ['txt', 'all']:
                        text_content, _ = TextExportService.generate_text(resume.id)
                        zip_file.writestr(f"{resume_filename_base}.txt", text_content.encode('utf-8'))
                    
                    logger.info(f'Successfully exported resume {resume.id} in batch export')
                    
                except Exception as e:
                    logger.error(f'Failed to export resume {resume.id} in batch: {str(e)}', exc_info=True)
                    failed_exports.append(resume.title)
        
        # Prepare ZIP file for download
        zip_buffer.seek(0)
        
        # Create HTTP response with ZIP content
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        
        # Set headers for download
        format_suffix = export_format if export_format != 'all' else 'all_formats'
        filename = f"resumes_export_{format_suffix}.zip"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Show success message with any failures
        if failed_exports:
            messages.warning(
                request,
                f'Batch export completed with {len(failed_exports)} failures: {", ".join(failed_exports)}'
            )
        else:
            messages.success(
                request,
                f'Successfully exported {resumes.count()} resume(s) in {export_format} format.'
            )
        
        logger.info(
            f'Batch export completed for user {request.user.username}: '
            f'{resumes.count()} resumes, format: {export_format}, '
            f'failures: {len(failed_exports)}'
        )
        
        return response
        
    except Exception as e:
        logger.error(f'Batch export failed for user {request.user.username}: {str(e)}', exc_info=True)
        messages.error(request, f'Batch export failed: {str(e)}')
        return redirect('resume_list')


@login_required
def batch_analysis(request):
    """
    Analyze multiple resumes against the same job description.
    Compare scores and highlight the best-scoring resume.
    
    POST parameters:
    - resume_ids: List of resume IDs to analyze
    - job_description: Job description text to compare against
    
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6
    """
    from apps.analyzer.services.scoring_engine import ScoringEngineService
    import time
    
    if request.method == 'POST':
        # Get resume IDs and job description from POST data
        resume_ids = request.POST.getlist('resume_ids')
        job_description = request.POST.get('job_description', '').strip()
        
        # Validation
        if not resume_ids:
            messages.error(request, 'Please select at least one resume to analyze.')
            return redirect('resume_list')
        
        if not job_description:
            messages.error(request, 'Please provide a job description.')
            return redirect('resume_list')
        
        if len(job_description) < 50:
            messages.error(request, 'Job description is too short. Please provide at least 50 characters.')
            return redirect('resume_list')
        
        # Validate that all resumes belong to the user
        resumes = Resume.objects.filter(
            id__in=resume_ids, 
            user=request.user
        ).prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        )
        
        if resumes.count() != len(resume_ids):
            messages.error(request, 'Some selected resumes do not exist or do not belong to you.')
            return redirect('resume_list')
        
        try:
            # Analyze all resumes
            analysis_results = []
            start_time = time.time()
            
            for resume in resumes:
                try:
                    # Run comprehensive ATS analysis
                    analysis = ScoringEngineService.calculate_ats_score(resume, job_description)
                    
                    analysis_results.append({
                        'resume': resume,
                        'final_score': analysis['final_score'],
                        'keyword_match_score': analysis['keyword_match_score'],
                        'skill_relevance_score': analysis['skill_relevance_score'],
                        'section_completeness_score': analysis['section_completeness_score'],
                        'experience_impact_score': analysis['experience_impact_score'],
                        'quantification_score': analysis['quantification_score'],
                        'action_verb_score': analysis['action_verb_score'],
                        'matched_keywords': analysis['matched_keywords'][:10],  # Top 10
                        'missing_keywords': analysis['missing_keywords'][:10],  # Top 10
                    })
                    
                    logger.info(
                        f'Analyzed resume {resume.id} in batch: score {analysis["final_score"]:.2f}'
                    )
                    
                except Exception as e:
                    logger.error(f'Failed to analyze resume {resume.id} in batch: {str(e)}', exc_info=True)
                    # Add placeholder with error
                    analysis_results.append({
                        'resume': resume,
                        'final_score': 0,
                        'error': str(e),
                    })
            
            elapsed_time = time.time() - start_time
            avg_time_per_resume = elapsed_time / len(resumes) if resumes else 0
            
            # Sort by score (highest first)
            analysis_results.sort(key=lambda x: x['final_score'], reverse=True)
            
            # Identify best resume
            best_resume = analysis_results[0] if analysis_results else None
            
            # Calculate key differences
            if len(analysis_results) > 1:
                for result in analysis_results[1:]:
                    # Find keywords that best resume has but this one doesn't
                    if best_resume and 'matched_keywords' in best_resume and 'matched_keywords' in result:
                        best_keywords = set(best_resume['matched_keywords'])
                        current_keywords = set(result['matched_keywords'])
                        result['missing_from_best'] = list(best_keywords - current_keywords)[:5]
            
            logger.info(
                f'Batch analysis completed for user {request.user.username}: '
                f'{len(resumes)} resumes analyzed in {elapsed_time:.2f}s '
                f'(avg {avg_time_per_resume:.2f}s per resume)'
            )
            
            # Check performance requirement (< 5s per resume)
            if avg_time_per_resume > 5:
                logger.warning(
                    f'Batch analysis performance issue: {avg_time_per_resume:.2f}s per resume '
                    f'(target: < 5s)'
                )
            
            context = {
                'analysis_results': analysis_results,
                'job_description': job_description,
                'best_resume': best_resume,
                'total_analyzed': len(resumes),
                'elapsed_time': elapsed_time,
                'avg_time_per_resume': avg_time_per_resume,
            }
            
            return render(request, 'resumes/batch_analysis_results.html', context)
            
        except Exception as e:
            logger.error(f'Batch analysis failed for user {request.user.username}: {str(e)}', exc_info=True)
            messages.error(request, f'Batch analysis failed: {str(e)}')
            return redirect('resume_list')
    
    # GET request - show form
    # Get user's resumes for selection
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'resumes': resumes,
    }
    
    return render(request, 'resumes/batch_analysis_form.html', context)


@login_required
def experience_add(request, resume_pk):
    """
    Add a new experience entry to a resume.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import ExperienceForm
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.resume = resume
            # Set order to be the highest + 1
            max_order = resume.experiences.aggregate(models.Max('order'))['order__max']
            experience.order = (max_order or 0) + 1
            experience.save()
            messages.success(request, 'Experience added successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import ExperienceForm
        form = ExperienceForm()
    
    context = {
        'form': form,
        'resume': resume,
        'action': 'Add'
    }
    return render(request, 'resumes/experience_form.html', context)


@login_required
def experience_edit(request, resume_pk, experience_pk):
    """
    Edit an existing experience entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    experience = get_object_or_404(resume.experiences, id=experience_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import ExperienceForm
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experience updated successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import ExperienceForm
        form = ExperienceForm(instance=experience)
    
    context = {
        'form': form,
        'resume': resume,
        'experience': experience,
        'action': 'Edit'
    }
    return render(request, 'resumes/experience_form.html', context)


@login_required
def experience_delete(request, resume_pk, experience_pk):
    """
    Delete an experience entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    experience = get_object_or_404(resume.experiences, id=experience_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Experience deleted successfully!')
        return redirect('resume_update', pk=resume_pk)
    
    context = {
        'resume': resume,
        'experience': experience
    }
    return render(request, 'resumes/experience_confirm_delete.html', context)


@login_required
def education_add(request, resume_pk):
    """
    Add a new education entry to a resume.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import EducationForm
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.resume = resume
            # Set order to be the highest + 1
            max_order = resume.education.aggregate(models.Max('order'))['order__max']
            education.order = (max_order or 0) + 1
            education.save()
            messages.success(request, 'Education added successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import EducationForm
        form = EducationForm()
    
    context = {
        'form': form,
        'resume': resume,
        'action': 'Add'
    }
    return render(request, 'resumes/education_form.html', context)


@login_required
def education_edit(request, resume_pk, education_pk):
    """
    Edit an existing education entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    education = get_object_or_404(resume.education, id=education_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import EducationForm
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import EducationForm
        form = EducationForm(instance=education)
    
    context = {
        'form': form,
        'resume': resume,
        'education': education,
        'action': 'Edit'
    }
    return render(request, 'resumes/education_form.html', context)


@login_required
def education_delete(request, resume_pk, education_pk):
    """
    Delete an education entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    education = get_object_or_404(resume.education, id=education_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education deleted successfully!')
        return redirect('resume_update', pk=resume_pk)
    
    context = {
        'resume': resume,
        'education': education
    }
    return render(request, 'resumes/education_confirm_delete.html', context)


@login_required
def skill_add(request, resume_pk):
    """
    Add a new skill entry to a resume.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import SkillForm
        form = SkillForm(request.POST, resume=resume)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.resume = resume
            skill.save()
            messages.success(request, 'Skill added successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import SkillForm
        form = SkillForm(resume=resume)
    
    context = {
        'form': form,
        'resume': resume,
        'action': 'Add'
    }
    return render(request, 'resumes/skill_form.html', context)


@login_required
def skill_edit(request, resume_pk, skill_pk):
    """
    Edit an existing skill entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    skill = get_object_or_404(resume.skills, id=skill_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import SkillForm
        form = SkillForm(request.POST, instance=skill, resume=resume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import SkillForm
        form = SkillForm(instance=skill, resume=resume)
    
    context = {
        'form': form,
        'resume': resume,
        'skill': skill,
        'action': 'Edit'
    }
    return render(request, 'resumes/skill_form.html', context)


@login_required
def skill_delete(request, resume_pk, skill_pk):
    """
    Delete a skill entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    skill = get_object_or_404(resume.skills, id=skill_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted successfully!')
        return redirect('resume_update', pk=resume_pk)
    
    context = {
        'resume': resume,
        'skill': skill
    }
    return render(request, 'resumes/skill_confirm_delete.html', context)


@login_required
def project_add(request, resume_pk):
    """
    Add a new project entry to a resume.
    Preserves order of project additions.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import ProjectForm
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.resume = resume
            # Set order to be the highest + 1 to preserve addition order
            max_order = resume.projects.aggregate(models.Max('order'))['order__max']
            project.order = (max_order or 0) + 1
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import ProjectForm
        form = ProjectForm()
    
    context = {
        'form': form,
        'resume': resume,
        'action': 'Add'
    }
    return render(request, 'resumes/project_form.html', context)


@login_required
def project_edit(request, resume_pk, project_pk):
    """
    Edit an existing project entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    project = get_object_or_404(resume.projects, id=project_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        from .forms import ProjectForm
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('resume_update', pk=resume_pk)
    else:
        from .forms import ProjectForm
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'resume': resume,
        'project': project,
        'action': 'Edit'
    }
    return render(request, 'resumes/project_form.html', context)


@login_required
def project_delete(request, resume_pk, project_pk):
    """
    Delete a project entry.
    """
    resume = get_object_or_404(Resume, id=resume_pk)
    project = get_object_or_404(resume.projects, id=project_pk)
    
    # Authorization check
    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this resume.")
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('resume_update', pk=resume_pk)
    
    context = {
        'resume': resume,
        'project': project
    }
    return render(request, 'resumes/project_confirm_delete.html', context)


# ============================================================================
# Resume Sharing
# ============================================================================

@login_required
def resume_share(request, pk):
    """Generate or revoke a public share link for a resume."""
    import secrets
    resume = get_object_or_404(Resume, id=pk, user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'generate':
            resume.share_token = secrets.token_urlsafe(32)
            resume.save(update_fields=['share_token'])
            messages.success(request, 'Share link generated.')
        elif action == 'revoke':
            resume.share_token = ''
            resume.save(update_fields=['share_token'])
            messages.success(request, 'Share link revoked.')
    return redirect('resume_detail', pk=pk)


def resume_public_view(request, token):
    """Public read-only resume view via share token."""
    resume = get_object_or_404(Resume, share_token=token)
    if not resume.share_token:
        from django.http import Http404
        raise Http404
    context = {
        'resume': resume,
        'personal_info': getattr(resume, 'personal_info', None),
        'experiences': resume.experiences.all(),
        'education': resume.education.all(),
        'skills': resume.skills.all(),
        'projects': resume.projects.all(),
        'is_public': True,
    }
    return render(request, 'resumes/resume_public.html', context)


# ============================================================================
# PDF Upload Module Views
# ============================================================================

@login_required
def pdf_upload(request):
    """
    Handle PDF resume upload with validation, rate limiting, and parsing.
    """
    # Rate limiting: max 5 uploads per hour per user
    from django.utils import timezone
    from datetime import timedelta
    recent_uploads = UploadedResume.objects.filter(
        user=request.user,
        uploaded_at__gte=timezone.now() - timedelta(hours=1)
    ).count()
    if recent_uploads >= 5:
        messages.error(request, 'Upload limit reached (5 per hour). Please try again later.')
        return render(request, 'resumes/pdf_upload.html')

    if request.method == 'POST':
        # Check if file was uploaded
        if 'resume_file' not in request.FILES:
            messages.error(request, 'Please select a PDF file to upload.')
            return render(request, 'resumes/pdf_upload.html')
        
        uploaded_file = request.FILES['resume_file']
        
        # Step 1: Validate file type and size
        is_valid, error_message = validate_pdf_file(uploaded_file)
        if not is_valid:
            messages.error(request, error_message)
            return render(request, 'resumes/pdf_upload.html')
        
        # Step 2: Check for embedded scripts
        if has_embedded_scripts(uploaded_file):
            messages.error(
                request,
                'The uploaded file contains potentially malicious content and cannot be processed.'
            )
            return render(request, 'resumes/pdf_upload.html')
        
        # Step 3: Create UploadedResume record
        try:
            uploaded_resume = UploadedResume.objects.create(
                user=request.user,
                original_filename=uploaded_file.name,
                file_path=uploaded_file,
                file_size=uploaded_file.size,
                status='uploaded'
            )
            
            logger.info(
                f'PDF uploaded successfully: {uploaded_file.name} '
                f'by user {request.user.username} (ID: {uploaded_resume.id})'
            )
            
        except Exception as e:
            logger.error(f'Failed to save uploaded file: {e}', exc_info=True)
            messages.error(request, 'Failed to save uploaded file. Please try again.')
            return render(request, 'resumes/pdf_upload.html')
        
        # Step 4: Extract text from PDF
        try:
            uploaded_resume.status = 'parsing'
            uploaded_resume.save()
            
            # Reset file pointer to beginning before extraction
            uploaded_file.seek(0)
            
            # Extract text using PDFParserService
            raw_text = PDFParserService.extract_text_from_pdf(uploaded_file)
            
            # Clean extracted text
            cleaned_text = PDFParserService.clean_extracted_text(raw_text)
            
            uploaded_resume.extracted_text = cleaned_text
            uploaded_resume.save()
            
            logger.info(f'Text extracted successfully from upload ID: {uploaded_resume.id}')
            
        except Exception as e:
            logger.error(f'PDF text extraction failed for upload ID {uploaded_resume.id}: {e}', exc_info=True)
            uploaded_resume.status = 'failed'
            uploaded_resume.error_message = f'Text extraction failed: {str(e)}'
            uploaded_resume.save()
            
            messages.error(
                request,
                'Failed to extract text from PDF. Please ensure the file is a text-based PDF (not a scanned image).'
            )
            return redirect('pdf_upload')
        
        # Step 5: Parse sections using SectionParserService
        try:
            parsed_data = SectionParserService.parse_resume(cleaned_text)
            
            # Calculate parsing confidence
            confidence = PDFParserService.calculate_parsing_confidence(
                cleaned_text,
                parsed_data
            )
            
            uploaded_resume.parsed_data = parsed_data
            uploaded_resume.parsing_confidence = confidence
            uploaded_resume.status = 'parsed'
            uploaded_resume.save()
            
            logger.info(
                f'Resume parsed successfully (ID: {uploaded_resume.id}, '
                f'Confidence: {confidence:.2f})'
            )
            
            # Show confidence warning if low
            if confidence < 0.7:
                messages.warning(
                    request,
                    f'Parsing confidence is {confidence*100:.0f}%. '
                    'Please review the extracted data carefully.'
                )
            else:
                messages.success(
                    request,
                    f'Resume parsed successfully with {confidence*100:.0f}% confidence!'
                )
            
        except Exception as e:
            logger.error(f'Resume parsing failed for upload ID {uploaded_resume.id}: {e}', exc_info=True)
            uploaded_resume.status = 'failed'
            uploaded_resume.error_message = f'Parsing failed: {str(e)}'
            uploaded_resume.save()
            
            messages.error(
                request,
                'Failed to parse resume sections. Please review the extracted data manually.'
            )
            # Still redirect to review page so user can see what was extracted
        
        # Step 6: Redirect to review page
        return redirect('pdf_parse_review', upload_id=uploaded_resume.id)
    
    # GET request - display upload form
    return render(request, 'resumes/pdf_upload.html')


@login_required
def pdf_parse_review(request, upload_id):
    """
    Display parsed resume data for user review and editing.
    
    Shows:
    - Parsing confidence score
    - Extracted personal information (editable)
    - Extracted experiences (editable)
    - Extracted education (editable)
    - Extracted skills (editable)
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    # Load UploadedResume
    uploaded_resume = get_object_or_404(UploadedResume, id=upload_id)
    
    # Authorization check
    if uploaded_resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view upload {upload_id} owned by {uploaded_resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view this upload.")
    
    # Check if resume has been parsed
    if uploaded_resume.status not in ['parsed', 'failed']:
        messages.warning(request, 'Resume is still being processed. Please wait.')
        return redirect('pdf_upload')
    
    # Get parsed data
    parsed_data = uploaded_resume.parsed_data or {}
    
    # Prepare context
    context = {
        'uploaded_resume': uploaded_resume,
        'parsed_data': parsed_data,
        'personal_info': parsed_data.get('personal_info', {}),
        'experiences': parsed_data.get('experiences', []),
        'education': parsed_data.get('education', []),
        'skills': parsed_data.get('skills', []),
        'summary': parsed_data.get('summary', ''),
        'confidence': uploaded_resume.parsing_confidence or 0.0,
        'confidence_percent': int((uploaded_resume.parsing_confidence or 0.0) * 100),
    }
    
    return render(request, 'resumes/parse_review_new.html', context)


@login_required
def pdf_import_confirm(request, upload_id):
    """
    Create Resume from parsed PDF data.
    
    POST only: Creates Resume, ResumeVersion, and runs initial ATS analysis.
    
    Requirements: 4.8, 5.4
    """
    if request.method != 'POST':
        return redirect('pdf_parse_review', upload_id=upload_id)
    
    # Load UploadedResume
    uploaded_resume = get_object_or_404(UploadedResume, id=upload_id)
    
    # Authorization check
    if uploaded_resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to import upload {upload_id} owned by {uploaded_resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to import this upload.")
    
    # Check if already imported
    if uploaded_resume.status == 'imported':
        messages.warning(request, 'This resume has already been imported.')
        return redirect('resume_list')
    
    try:
        # Get parsed data (may have been edited by user in review page)
        parsed_data = uploaded_resume.parsed_data or {}
        
        # Prepare resume data for creation
        resume_data = {
            'title': request.POST.get('title', f"Resume from {uploaded_resume.original_filename}"),
            'template': request.POST.get('template', 'professional'),
        }

        # Personal info — read from POST (user may have edited the review form)
        personal_info = parsed_data.get('personal_info') or {}
        full_name = request.POST.get('full_name', '').strip() or personal_info.get('name', '')
        email = request.POST.get('email', '').strip() or personal_info.get('email', '')
        phone = request.POST.get('phone', '').strip() or personal_info.get('phone', '')
        location = request.POST.get('location', '').strip() or personal_info.get('location', '')
        linkedin = request.POST.get('linkedin', '').strip() or personal_info.get('linkedin', '') or None
        github = request.POST.get('github', '').strip() or personal_info.get('website', '') or None

        resume_data['personal_info'] = {
            'full_name': full_name or 'Unknown',
            'email': email or '',
            'phone': phone,
            'location': location,
            'linkedin': linkedin if linkedin else None,
            'github': github if github else None,
        }
        
        # Add experiences if available
        experiences = parsed_data.get('experiences', [])
        if experiences:
            resume_data['experiences'] = []
            for exp in experiences:
                from datetime import datetime
                start_date = None
                end_date = None

                def _parse_date(s):
                    if not s:
                        return None
                    s = str(s).strip()
                    if s.lower() in ('present', 'current', 'now'):
                        return None
                    for fmt in ('%B %Y', '%b %Y', '%b. %Y', '%m/%Y', '%Y'):
                        try:
                            return datetime.strptime(s, fmt).date()
                        except ValueError:
                            continue
                    # Try extracting just the year
                    ym = re.search(r'(\d{4})', s)
                    if ym:
                        try:
                            return datetime(int(ym.group(1)), 1, 1).date()
                        except Exception:
                            pass
                    return None

                start_date = _parse_date(exp.get('start_date'))
                end_date = _parse_date(exp.get('end_date'))
                if not start_date:
                    start_date = datetime.today().date()

                resume_data['experiences'].append({
                    'company': exp.get('company') or 'Unknown Company',
                    'role': exp.get('title') or exp.get('role') or 'Unknown Role',
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': exp.get('description', ''),
                    'achievements': exp.get('achievements', ''),
                    'location': exp.get('location', ''),
                })
        
        # Add education if available
        education = parsed_data.get('education', [])
        if education:
            resume_data['education'] = []
            for edu in education:
                # Extract year from graduation_date
                year = None
                if edu.get('graduation_date'):
                    try:
                        year = int(re.search(r'\d{4}', edu['graduation_date']).group(0))
                    except Exception:
                        year = datetime.today().year
                
                if not year:
                    year = datetime.today().year
                
                resume_data['education'].append({
                    'institution': edu.get('institution', 'Unknown Institution'),
                    'degree': edu.get('degree', 'Unknown Degree'),
                    'field': edu.get('field_of_study', ''),  # Allow empty field
                    'start_year': year - 4,  # Assume 4-year program
                    'end_year': year,
                })
        
        # Add skills if available
        skills = parsed_data.get('skills', [])
        if skills:
            resume_data['skills'] = []
            for skill in skills:
                resume_data['skills'].append({
                    'name': skill.get('name', ''),
                    'category': skill.get('category') or 'General',
                })
        
        # Create the resume using ResumeService
        resume = ResumeService.create_resume(request.user, resume_data)
        
        # Mark upload as imported
        uploaded_resume.status = 'imported'
        uploaded_resume.save()

        from apps.authentication.models import ActivityLog
        ActivityLog.log(request.user, 'pdf_imported', f'Imported PDF as "{resume.title}"', resume=resume)
        
        logger.info(
            f'Resume created from upload ID {upload_id}: '
            f'Resume ID {resume.id} for user {request.user.username}'
        )
        
        messages.success(
            request,
            f'Resume "{resume.title}" has been created successfully from your uploaded PDF!'
        )
        
        # Redirect to resume detail
        return redirect('resume_detail', pk=resume.id)
        
    except Exception as e:
        logger.error(f'Failed to create resume from upload ID {upload_id}: {e}', exc_info=True)
        messages.error(
            request,
            f'Failed to create resume: {str(e)}. Please try creating a resume manually.'
        )
        return redirect('pdf_parse_review', upload_id=upload_id)


# ============================================================================
# Resume Optimization Module Views
# ============================================================================

@login_required
def fix_resume(request, pk):
    """
    Display job description form for resume optimization.
    
    GET: Display form to enter job description
    POST: Store job description in session and redirect to preview
    
    Requirements: 8.1
    """
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to optimize resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to optimize this resume.")
    
    if request.method == 'POST':
        # Get job description from form
        job_description = request.POST.get('job_description', '').strip()
        
        # Validate job description
        if not job_description:
            messages.error(request, 'Please enter a job description.')
            return render(request, 'resumes/fix_resume.html', {'resume': resume})
        
        if len(job_description) < 50:
            messages.error(request, 'Job description is too short. Please enter at least 50 characters.')
            return render(request, 'resumes/fix_resume.html', {
                'resume': resume,
                'job_description': job_description
            })
        
        # Store job description in session
        request.session[f'fix_resume_{pk}_job_description'] = job_description
        request.session.modified = True
        
        logger.info(
            f'Job description stored for resume {pk} optimization by user {request.user.username}'
        )
        
        # Redirect to optimization preview
        return redirect('fix_preview', pk=pk)
    
    # GET request - display form
    from apps.authentication.models import SavedJobDescription
    saved_jds = SavedJobDescription.objects.filter(user=request.user)[:8]
    context = {
        'resume': resume,
        'saved_jds': saved_jds,
    }
    return render(request, 'resumes/fix_resume.html', context)



@login_required
def fix_preview(request, pk):
    """
    Run optimization and display side-by-side comparison.
    
    Loads resume and job description, runs ResumeOptimizerService,
    calculates new score, stores results in session, and displays comparison.
    
    Requirements: 9.1, 9.2, 9.3, 9.4
    """
    from .services.resume_optimizer import ResumeOptimizerService
    
    # Load resume with all related data
    resume = get_object_or_404(
        Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        ),
        id=pk
    )
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view optimization preview for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view this optimization.")
    
    # Get job description from session
    session_key = f'fix_resume_{pk}_job_description'
    job_description = request.session.get(session_key)
    
    if not job_description:
        messages.error(request, 'Job description not found. Please start the optimization process again.')
        return redirect('fix_resume', pk=pk)
    
    # Check if optimization results are already in session
    results_key = f'fix_resume_{pk}_results'
    optimization_results = request.session.get(results_key)
    
    if not optimization_results:
        # Run optimization
        try:
            logger.info(f'Running optimization for resume {pk} by user {request.user.username}')
            
            optimization_results = ResumeOptimizerService.optimize_resume(
                resume=resume,
                job_description=job_description
            )
            
            # Store results in session
            request.session[results_key] = optimization_results
            request.session.modified = True
            
            logger.info(
                f'Optimization completed for resume {pk}: '
                f'Original score: {optimization_results["original_score"]}, '
                f'Optimized score: {optimization_results["optimized_score"]}, '
                f'Delta: {optimization_results["improvement_delta"]}'
            )
            
        except Exception as e:
            logger.error(f'Optimization failed for resume {pk}: {e}', exc_info=True)
            messages.error(
                request,
                f'Resume optimization failed: {str(e)}. Please try again or contact support.'
            )
            return redirect('resume_detail', pk=pk)
    
    # Prepare context for template
    context = {
        'resume': resume,
        'job_description': job_description,
        'original_score': optimization_results['original_score'],
        'optimized_score': optimization_results['optimized_score'],
        'improvement_delta': optimization_results['improvement_delta'],
        'changes_summary': optimization_results['changes_summary'],
        'detailed_changes': optimization_results['detailed_changes'],
        'optimized_data': optimization_results['optimized_data'],
        'original_analysis': optimization_results.get('original_analysis', {}),
        
        # Group changes by type for easier display
        'bullet_changes': [c for c in optimization_results['detailed_changes'] if c['type'] == 'bullet_rewrite'],
        'keyword_changes': [c for c in optimization_results['detailed_changes'] if c['type'] == 'keyword_injection'],
        'quantification_changes': [c for c in optimization_results['detailed_changes'] if c['type'] == 'quantification_suggestion'],
        'formatting_changes': [c for c in optimization_results['detailed_changes'] if c['type'] == 'formatting_standardization'],
    }
    
    return render(request, 'resumes/fix_comparison.html', context)



@login_required
def fix_accept(request, pk):
    """
    Accept optimization changes and create new resume version.
    
    POST only: Creates new ResumeVersion with optimized data,
    creates OptimizationHistory record, clears session, and redirects.
    
    Requirements: 9.6, 10.1, 10.2, 10.3
    """
    from .services.version_service import VersionService
    from .models import OptimizationHistory
    from datetime import datetime
    
    if request.method != 'POST':
        return redirect('fix_preview', pk=pk)
    
    # Load resume
    resume = get_object_or_404(
        Resume.objects.prefetch_related(
            'personal_info',
            'experiences',
            'education',
            'skills',
            'projects'
        ),
        id=pk
    )
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to accept optimization for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to accept this optimization.")
    
    # Get optimization results from session
    results_key = f'fix_resume_{pk}_results'
    job_desc_key = f'fix_resume_{pk}_job_description'
    
    optimization_results = request.session.get(results_key)
    job_description = request.session.get(job_desc_key)
    
    if not optimization_results or not job_description:
        messages.error(request, 'Optimization data not found. Please start the optimization process again.')
        return redirect('fix_resume', pk=pk)
    
    try:
        with transaction.atomic():
            # Step 1: Create version of current state (before optimization)
            original_version = VersionService.create_version(
                resume=resume,
                modification_type='manual',
                user_notes='Version before AI optimization',
                ats_score=optimization_results['original_score']
            )
            
            logger.info(f'Created original version {original_version.version_number} for resume {pk}')
            
            # Step 2: Apply optimized changes to resume
            optimized_data = optimization_results['optimized_data']
            
            # Update experiences with optimized descriptions
            for exp in resume.experiences.all():
                # Find matching optimized experience
                for opt_exp in optimized_data.get('experiences', []):
                    if (opt_exp.get('company') == exp.company and 
                        opt_exp.get('role') == exp.role):
                        # Update description if changed
                        if opt_exp.get('description') and opt_exp['description'] != exp.description:
                            exp.description = opt_exp['description']
                            exp.save()
                            logger.debug(f'Updated experience: {exp.company} - {exp.role}')
                        break
            
            # Update projects with optimized descriptions
            for proj in resume.projects.all():
                # Find matching optimized project
                for opt_proj in optimized_data.get('projects', []):
                    if opt_proj.get('name') == proj.name:
                        # Update description if changed
                        if opt_proj.get('description') and opt_proj['description'] != proj.description:
                            proj.description = opt_proj['description']
                            proj.save()
                            logger.debug(f'Updated project: {proj.name}')
                        break
            
            # Add new skills from keyword injections
            from .models import Skill
            existing_skill_names = set(resume.skills.values_list('name', flat=True))
            
            for opt_skill in optimized_data.get('skills', []):
                skill_name = opt_skill.get('name')
                if skill_name and skill_name not in existing_skill_names:
                    # This is a new skill from keyword injection
                    Skill.objects.create(
                        resume=resume,
                        name=skill_name,
                        category='General'  # Default category
                    )
                    logger.debug(f'Added new skill: {skill_name}')
            
            # Update resume timestamp
            resume.last_optimized_at = timezone.now()
            resume.save(update_fields=['last_optimized_at'])
            
            # Step 3: Create version of optimized state
            optimized_version = VersionService.create_version(
                resume=resume,
                modification_type='optimized',
                user_notes='AI-optimized version',
                ats_score=optimization_results['optimized_score']
            )
            
            logger.info(f'Created optimized version {optimized_version.version_number} for resume {pk}')
            
            # Step 4: Create OptimizationHistory record
            optimization_history = OptimizationHistory.objects.create(
                resume=resume,
                original_version=original_version,
                optimized_version=optimized_version,
                job_description=job_description,
                original_score=optimization_results['original_score'],
                optimized_score=optimization_results['optimized_score'],
                improvement_delta=optimization_results['improvement_delta'],
                changes_summary=optimization_results['changes_summary'],
                detailed_changes=optimization_results['detailed_changes'],
                accepted_changes=optimization_results['detailed_changes'],  # All changes accepted
                rejected_changes=[],
                user_notes='All optimization suggestions accepted'
            )
            
            logger.info(
                f'Created optimization history record {optimization_history.id} for resume {pk}: '
                f'Delta: {optimization_history.improvement_delta}'
            )
            
            # Step 5: Clear session data
            if results_key in request.session:
                del request.session[results_key]
            if job_desc_key in request.session:
                del request.session[job_desc_key]
            request.session.modified = True
            
            # Success message
            messages.success(
                request,
                f'Resume optimized successfully! ATS score improved by {optimization_results["improvement_delta"]:.1f} points '
                f'(from {optimization_results["original_score"]:.1f} to {optimization_results["optimized_score"]:.1f}).'
            )
            
            logger.info(f'Optimization accepted for resume {pk} by user {request.user.username}')
            
            # Redirect to resume detail
            return redirect('resume_detail', pk=pk)
            
    except Exception as e:
        logger.error(f'Failed to accept optimization for resume {pk}: {e}', exc_info=True)
        messages.error(
            request,
            f'Failed to apply optimization: {str(e)}. Please try again or contact support.'
        )
        return redirect('fix_preview', pk=pk)



@login_required
def fix_reject(request, pk):
    """
    Reject optimization changes and clear session.
    
    POST only: Clears session data and redirects to resume detail.
    
    Requirements: 9.5
    """
    if request.method != 'POST':
        return redirect('fix_preview', pk=pk)
    
    # Load resume for authorization check
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to reject optimization for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to reject this optimization.")
    
    # Clear session data
    results_key = f'fix_resume_{pk}_results'
    job_desc_key = f'fix_resume_{pk}_job_description'
    
    if results_key in request.session:
        del request.session[results_key]
    if job_desc_key in request.session:
        del request.session[job_desc_key]
    request.session.modified = True
    
    logger.info(f'Optimization rejected for resume {pk} by user {request.user.username}')
    
    messages.info(request, 'Optimization changes have been discarded.')
    
    # Redirect to resume detail
    return redirect('resume_detail', pk=pk)


# ============================================================================
# Keyword & Achievement Assistance Module Views
# ============================================================================

@login_required
def keyword_suggestions(request, pk):
    """
    Display keyword suggestions for a resume based on industry and job description.
    
    GET: Display form to enter job description (optional)
    POST: Show keyword suggestions
    
    Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6
    """
    from apps.analyzer.services.keyword_suggester import KeywordSuggesterService
    
    # Load resume
    resume = get_object_or_404(
        Resume.objects.prefetch_related(
            'experiences',
            'education',
            'skills',
            'projects'
        ),
        id=pk
    )
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view keyword suggestions for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view keyword suggestions for this resume.")
    
    if request.method == 'POST':
        # Get job description (optional)
        job_description = request.POST.get('job_description', '').strip()
        
        if not job_description:
            # Use generic suggestions based on industry
            job_description = ''
        
        # Get keyword suggestions
        try:
            suggestions = KeywordSuggesterService.suggest_keywords(
                resume, 
                job_description, 
                max_suggestions=15
            )
            
            # Extract industry info
            industry_info = KeywordSuggesterService.extract_industry_and_role(resume)
            
            # Group suggestions by category
            suggestions_by_category = {
                'technical': [],
                'soft_skills': [],
                'certifications': []
            }
            
            for suggestion in suggestions:
                category = suggestion['category']
                if category in suggestions_by_category:
                    suggestions_by_category[category].append(suggestion)
            
            logger.info(
                f'Generated {len(suggestions)} keyword suggestions for resume {pk} '
                f'(industry: {industry_info["industry"]})'
            )
            
            context = {
                'resume': resume,
                'suggestions': suggestions,
                'suggestions_by_category': suggestions_by_category,
                'industry_info': industry_info,
                'job_description': job_description,
                'has_job_description': bool(job_description),
            }
            
            return render(request, 'resumes/keyword_suggestions.html', context)
            
        except Exception as e:
            logger.error(f'Failed to generate keyword suggestions for resume {pk}: {str(e)}', exc_info=True)
            messages.error(request, f'Failed to generate keyword suggestions: {str(e)}')
            return redirect('resume_detail', pk=pk)
    
    # GET request - show form
    context = {
        'resume': resume,
    }
    
    return render(request, 'resumes/keyword_suggestions_form.html', context)


@login_required
def add_keyword(request, pk):
    """
    Add a suggested keyword to the resume.
    
    POST only: Adds keyword to appropriate section
    
    Requirements: 17.6, 18.1, 18.2, 18.3
    """
    from apps.resumes.models import Skill
    
    if request.method != 'POST':
        return redirect('keyword_suggestions', pk=pk)
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to add keyword to resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to modify this resume.")
    
    # Get keyword and placement
    keyword = request.POST.get('keyword', '').strip()
    placement = request.POST.get('placement', 'skills')
    
    if not keyword:
        messages.error(request, 'No keyword provided.')
        return redirect('keyword_suggestions', pk=pk)
    
    try:
        # Add keyword based on placement
        if placement == 'skills':
            # Check if skill already exists
            existing_skill = Skill.objects.filter(
                resume=resume,
                name__iexact=keyword
            ).first()
            
            if existing_skill:
                messages.info(request, f'Skill "{keyword}" already exists in your resume.')
            else:
                # Add new skill
                Skill.objects.create(
                    resume=resume,
                    name=keyword,
                    category='Technical'  # Default category
                )
                messages.success(request, f'Added "{keyword}" to your Skills section.')
                logger.info(f'Added keyword "{keyword}" to resume {pk} skills')
        
        # For other placements, we'd need to modify experience descriptions
        # For now, just add to skills
        
        # Redirect back to keyword suggestions
        return redirect('keyword_suggestions', pk=pk)
        
    except Exception as e:
        logger.error(f'Failed to add keyword to resume {pk}: {str(e)}', exc_info=True)
        messages.error(request, f'Failed to add keyword: {str(e)}')
        return redirect('keyword_suggestions', pk=pk)


# ============================================================================
# Optimization History Module Views
# ============================================================================

@login_required
def optimization_history_list(request, pk):
    """
    Display all optimization sessions for a resume in reverse chronological order.
    
    Shows optimization history with metadata including:
    - Optimization dates
    - Job description snippets
    - Score improvements
    - Change summaries
    
    Requirements: 3.3, 10.3
    """
    from .models import OptimizationHistory
    from django.core.paginator import Paginator
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view optimization history for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view this optimization history.")
    
    # Get all optimization sessions for this resume
    optimizations = OptimizationHistory.objects.filter(
        resume=resume
    ).select_related(
        'original_version',
        'optimized_version'
    ).order_by('-optimization_timestamp')
    
    # Paginate results (10 per page)
    paginator = Paginator(optimizations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare optimization data with truncated job descriptions
    optimization_data = []
    for opt in page_obj:
        # Truncate job description to 150 characters
        job_desc_snippet = opt.job_description[:150] + '...' if len(opt.job_description) > 150 else opt.job_description
        
        optimization_data.append({
            'id': opt.id,
            'created_at': opt.optimization_timestamp,
            'job_description_snippet': job_desc_snippet,
            'original_score': opt.original_score,
            'optimized_score': opt.optimized_score,
            'improvement_delta': opt.improvement_delta,
            'changes_summary': opt.changes_summary,
            'original_version': opt.original_version,
            'optimized_version': opt.optimized_version,
        })
    
    logger.info(
        f'Displaying optimization history for resume {pk}: '
        f'{optimizations.count()} total sessions'
    )
    
    context = {
        'resume': resume,
        'page_obj': page_obj,
        'optimization_data': optimization_data,
        'total_optimizations': optimizations.count(),
    }
    
    return render(request, 'resumes/optimization_history_list.html', context)


@login_required
def optimization_history_detail(request, pk, optimization_id):
    """
    Display detailed view of a specific optimization session.
    
    Shows complete optimization metadata including:
    - Full job description
    - All changes with accept/reject status
    - Original and optimized scores
    - Links to original and optimized versions
    
    Requirements: 3.4, 3.5, 10.4, 10.5
    """
    from .models import OptimizationHistory
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view optimization detail for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view this optimization detail.")
    
    # Load optimization history record
    optimization = get_object_or_404(
        OptimizationHistory.objects.select_related(
            'original_version',
            'optimized_version'
        ),
        id=optimization_id,
        resume=resume
    )
    
    # Group changes by type for easier display
    changes_by_type = {
        'bullet_rewrites': [],
        'keyword_injections': [],
        'quantification_suggestions': [],
        'formatting_fixes': [],
    }
    
    for change in optimization.detailed_changes:
        change_type = change.get('type', '')
        if change_type == 'bullet_rewrite':
            changes_by_type['bullet_rewrites'].append(change)
        elif change_type == 'keyword_injection':
            changes_by_type['keyword_injections'].append(change)
        elif change_type == 'quantification_suggestion':
            changes_by_type['quantification_suggestions'].append(change)
        elif change_type == 'formatting_standardization':
            changes_by_type['formatting_fixes'].append(change)
    
    # Determine which changes were accepted vs rejected
    accepted_change_ids = set()
    rejected_change_ids = set()
    
    for change in optimization.accepted_changes:
        # Create a unique identifier for the change
        change_id = f"{change.get('type')}_{change.get('section')}_{change.get('old_text', '')[:50]}"
        accepted_change_ids.add(change_id)
    
    for change in optimization.rejected_changes:
        change_id = f"{change.get('type')}_{change.get('section')}_{change.get('old_text', '')[:50]}"
        rejected_change_ids.add(change_id)
    
    logger.info(
        f'Displaying optimization detail {optimization_id} for resume {pk} '
        f'by user {request.user.username}'
    )
    
    context = {
        'resume': resume,
        'optimization': optimization,
        'changes_by_type': changes_by_type,
        'accepted_change_ids': accepted_change_ids,
        'rejected_change_ids': rejected_change_ids,
    }
    
    return render(request, 'resumes/optimization_history_detail.html', context)


# ============================================================================
# Version Management Module Views
# ============================================================================

@login_required
def version_list(request, pk):
    """
    Display all versions for a resume in reverse chronological order.
    
    Shows version history with metadata including:
    - Version numbers
    - Creation dates
    - ATS scores
    - Modification types
    
    Requirements: 1.3, 1.6
    """
    from .services.version_service import VersionService
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view versions for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view these versions.")
    
    # Get all versions for this resume
    versions = VersionService.get_version_history(resume)
    
    logger.info(
        f'Version history loaded for resume {pk} by user {request.user.username}: '
        f'{len(versions)} versions found'
    )
    
    context = {
        'resume': resume,
        'versions': versions,
        'current_version_number': resume.current_version_number,
    }
    
    return render(request, 'resumes/version_list.html', context)


@login_required
def version_detail(request, pk, version_id):
    """
    Display a specific version in read-only mode.
    
    Shows:
    - Complete historical state of the resume
    - Version metadata (number, date, type, score)
    - Read-only view of all sections
    
    Requirements: 1.4
    """
    from .models import ResumeVersion
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to view version for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to view this version.")
    
    # Load specific version
    version = get_object_or_404(ResumeVersion, id=version_id, resume=resume)
    
    # Get snapshot data
    snapshot = version.snapshot_data
    
    logger.info(
        f'Version {version.version_number} loaded for resume {pk} '
        f'by user {request.user.username}'
    )
    
    context = {
        'resume': resume,
        'version': version,
        'snapshot': snapshot,
        'personal_info': snapshot.get('personal_info', {}),
        'experiences': snapshot.get('experiences', []),
        'education': snapshot.get('education', []),
        'skills': snapshot.get('skills', []),
        'projects': snapshot.get('projects', []),
        'is_current_version': version.version_number == resume.current_version_number,
    }
    
    return render(request, 'resumes/version_detail.html', context)


@login_required
def version_compare(request, pk):
    """
    Compare two versions side-by-side with diff highlighting.
    
    GET parameters:
    - version1: ID of first version (typically older)
    - version2: ID of second version (typically newer)
    
    Shows:
    - Side-by-side comparison
    - Highlighted differences (additions in green, deletions in red, modifications in yellow)
    - Section-by-section changes
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    from .services.version_service import VersionService
    from .models import ResumeVersion
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to compare versions for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to compare these versions.")
    
    # Get version IDs from query parameters
    version1_id = request.GET.get('version1')
    version2_id = request.GET.get('version2')
    
    if not version1_id or not version2_id:
        messages.error(request, 'Please select two versions to compare.')
        return redirect('version_list', pk=pk)
    
    # Load versions
    try:
        version1 = ResumeVersion.objects.get(id=version1_id, resume=resume)
        version2 = ResumeVersion.objects.get(id=version2_id, resume=resume)
    except ResumeVersion.DoesNotExist:
        messages.error(request, 'One or both versions not found.')
        return redirect('version_list', pk=pk)
    
    # Ensure version1 is older than version2 for consistent display
    if version1.version_number > version2.version_number:
        version1, version2 = version2, version1
    
    # Generate diff using VersionService
    diff = VersionService.compare_versions(version1, version2)
    
    logger.info(
        f'Comparing versions {version1.version_number} and {version2.version_number} '
        f'for resume {pk} by user {request.user.username}: '
        f'{len(diff["changes"])} changes found'
    )
    
    # Organize changes by section for easier display
    changes_by_section = {}
    for change in diff['changes']:
        section = change['section']
        if section not in changes_by_section:
            changes_by_section[section] = []
        changes_by_section[section].append(change)
    
    context = {
        'resume': resume,
        'version1': version1,
        'version2': version2,
        'diff': diff,
        'changes_by_section': changes_by_section,
        'snapshot1': version1.snapshot_data,
        'snapshot2': version2.snapshot_data,
        'total_changes': len(diff['changes']),
    }
    
    return render(request, 'resumes/version_compare.html', context)


@login_required
def version_restore(request, pk, version_id):
    """
    Restore a resume to a specific historical version.
    
    POST only: Creates a new version based on the selected historical version.
    This is non-destructive - it creates a new version rather than overwriting.
    
    Requirements: 1.5
    """
    from .services.version_service import VersionService
    from .models import ResumeVersion
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('version_list', pk=pk)
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to restore version for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to restore this version.")
    
    # Load version to restore
    try:
        version = ResumeVersion.objects.get(id=version_id, resume=resume)
    except ResumeVersion.DoesNotExist:
        messages.error(request, 'Version not found.')
        return redirect('version_list', pk=pk)
    
    # Check if trying to restore current version
    if version.version_number == resume.current_version_number:
        messages.info(request, 'This is already the current version.')
        return redirect('version_detail', pk=pk, version_id=version_id)
    
    try:
        # Restore the version (creates a new version)
        restored_resume = VersionService.restore_version(version)
        
        logger.info(
            f'Version {version.version_number} restored for resume {pk} '
            f'by user {request.user.username}. New version: {restored_resume.current_version_number}'
        )
        
        messages.success(
            request,
            f'Resume restored to version {version.version_number}. '
            f'A new version ({restored_resume.current_version_number}) has been created.'
        )
        
        # Redirect to resume edit page
        return redirect('resume_update', pk=pk)
        
    except Exception as e:
        logger.error(
            f'Failed to restore version {version.version_number} for resume {pk}: {e}',
            exc_info=True
        )
        messages.error(
            request,
            f'Failed to restore version: {str(e)}. Please try again or contact support.'
        )
        return redirect('version_detail', pk=pk, version_id=version_id)


# ============================================================================
# Template Customization Module Views
# ============================================================================

@login_required
def customize_template(request, pk):
    """
    Customize resume template with color scheme and font selection.
    
    GET: Display customization form with current settings
    POST: Apply customization changes
    
    Requirements: 13.1, 13.2, 13.3, 14.1, 14.3
    """
    from apps.resumes.services.template_customization_service import TemplateCustomizationService
    
    # Load resume
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(
            f'Unauthorized access attempt: User {request.user.username} '
            f'tried to customize template for resume {pk} owned by {resume.user.username}'
        )
        return HttpResponseForbidden("You do not have permission to customize this resume.")
    
    if request.method == 'POST':
        # Get customization settings
        color_scheme = request.POST.get('color_scheme')
        font_family = request.POST.get('font_family')
        
        try:
            # Apply customization
            TemplateCustomizationService.apply_customization_to_resume(
                resume,
                color_scheme=color_scheme,
                font_family=font_family
            )
            
            logger.info(
                f'Template customization applied to resume {pk}: '
                f'color={color_scheme}, font={font_family}'
            )
            
            messages.success(request, 'Template customization applied successfully!')
            
            # Check if this is an AJAX request for preview
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': 'Customization applied',
                    'css': TemplateCustomizationService.get_css_variables(resume)
                })
            
            return redirect('resume_detail', pk=pk)
            
        except Exception as e:
            logger.error(f'Failed to apply template customization to resume {pk}: {str(e)}', exc_info=True)
            messages.error(request, f'Failed to apply customization: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
    
    # GET request - show customization form
    color_schemes = TemplateCustomizationService.get_all_color_schemes()
    fonts = TemplateCustomizationService.get_all_fonts()
    current_css = TemplateCustomizationService.get_css_variables(resume)
    
    context = {
        'resume': resume,
        'color_schemes': color_schemes,
        'fonts': fonts,
        'current_color_scheme': resume.color_scheme,
        'current_font': resume.font_family,
        'current_css': current_css,
    }
    
    return render(request, 'resumes/customize_template.html', context)


# ── Server-Sent Events (SSE) Progress ─────────────────────────────────────────

@login_required
def task_progress_sse(request, task_id: str):
    """
    Server-Sent Events endpoint for real-time task progress.
    Streams task status updates to the browser without polling.

    Usage in JS:
        const es = new EventSource(`/resumes/task/${taskId}/progress/`);
        es.onmessage = (e) => { const data = JSON.parse(e.data); ... };
    """
    import json
    import time
    from django.http import StreamingHttpResponse

    def event_stream():
        max_polls = 60  # 60 seconds max
        for _ in range(max_polls):
            try:
                from celery.result import AsyncResult
                result = AsyncResult(task_id)
                data = {
                    'task_id': task_id,
                    'status': result.status,
                    'ready': result.ready(),
                }
                if result.ready():
                    if result.successful():
                        data['result'] = result.result
                    else:
                        data['error'] = str(result.result)
                    yield f"data: {json.dumps(data)}\n\n"
                    break
                else:
                    yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'status': 'ERROR', 'error': str(e)})}\n\n"
                break
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
def fix_resume_async(request, pk):
    """
    Async version of fix_resume — queues optimization as a Celery task
    and returns a task_id for SSE progress tracking.
    """
    from django.http import JsonResponse
    resume = get_object_or_404(Resume, id=pk)

    if resume.user != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    job_description = request.POST.get('job_description', '').strip()
    if not job_description:
        return JsonResponse({'error': 'Job description is required'}, status=400)

    try:
        from apps.resumes.tasks import optimize_resume_task
        task = optimize_resume_task.delay(resume.id, job_description, request.user.id)
        return JsonResponse({
            'task_id': task.id,
            'status': 'queued',
            'progress_url': f'/resumes/task/{task.id}/progress/',
        })
    except Exception as e:
        logger.warning(f"Celery unavailable, falling back to sync optimization: {e}")
        # Fall back to synchronous optimization
        return fix_resume(request, pk)


@login_required
def pdf_upload_async(request):
    """
    Async PDF upload — saves file and queues parsing as a Celery task.
    Returns task_id for SSE progress tracking.
    """
    from django.http import JsonResponse
    from .utils.file_validators import validate_pdf_file, has_embedded_scripts
    from .models import UploadedResume

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    pdf_file = request.FILES.get('pdf_file')
    if not pdf_file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    # Validate
    is_valid, error_msg = validate_pdf_file(pdf_file)
    if not is_valid:
        return JsonResponse({'error': error_msg}, status=400)

    if has_embedded_scripts(pdf_file):
        return JsonResponse({'error': 'PDF contains embedded scripts and cannot be processed'}, status=400)

    # Save upload record
    upload = UploadedResume.objects.create(
        user=request.user,
        original_filename=pdf_file.name,
        file_path=pdf_file,
        file_size=pdf_file.size,
        status='uploaded',
    )

    # Queue async parsing
    try:
        from apps.resumes.tasks import parse_pdf_task
        task = parse_pdf_task.delay(upload.id)
        return JsonResponse({
            'upload_id': upload.id,
            'task_id': task.id,
            'status': 'queued',
            'progress_url': f'/resumes/task/{task.id}/progress/',
            'review_url': f'/resumes/upload/{upload.id}/review/',
        })
    except Exception as e:
        logger.warning(f"Celery unavailable for PDF parsing: {e}")
        # Fall back to sync — redirect to existing upload view
        return JsonResponse({
            'upload_id': upload.id,
            'status': 'sync_fallback',
            'review_url': f'/resumes/upload/{upload.id}/review/',
        })


# ── ATS System Simulation View ────────────────────────────────────────────────

@login_required
def ats_simulate(request, pk):
    """
    Show ATS system simulation results for a resume.
    Simulates Taleo, Workday, Greenhouse, Lever, and iCIMS.
    """
    from django.http import JsonResponse
    resume = get_object_or_404(Resume, id=pk)

    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to view this resume.")

    job_description = request.GET.get('job_description', '') or request.POST.get('job_description', '')

    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from apps.analyzer.services.ats_simulator import ATSSystemSimulator
        results = ATSSystemSimulator.simulate_all(resume, job_description)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(results)
        context = {
            'resume': resume,
            'simulation': results,
            'job_description': job_description,
        }
        return render(request, 'resumes/ats_simulate.html', context)

    return render(request, 'resumes/ats_simulate.html', {
        'resume': resume,
        'job_description': job_description,
    })


# ── LinkedIn Import View ──────────────────────────────────────────────────────

@login_required
def linkedin_import(request):
    """
    Import a LinkedIn profile and pre-fill the resume creation wizard.
    """
    from django.http import JsonResponse

    if request.method == 'POST':
        url = request.POST.get('linkedin_url', '').strip()
        if not url:
            return JsonResponse({'success': False, 'error': 'LinkedIn URL is required'})

        from apps.resumes.services.linkedin_importer import LinkedInImporter
        result = LinkedInImporter().import_profile(url)

        if result['success']:
            # Pre-populate wizard session with imported data
            data = result['data']
            request.session['resume_wizard'] = {
                'step': 1,
                'data': {
                    'personal_info': {
                        'full_name': data.get('name', ''),
                        'email': '',
                        'phone': '',
                        'location': data.get('location', ''),
                        'linkedin': url,
                        'github': '',
                    },
                    'experiences': [
                        {
                            'company': exp.get('company', ''),
                            'role': exp.get('role', ''),
                            'description': exp.get('description', ''),
                            'start_date': None,
                            'end_date': None,
                        }
                        for exp in data.get('experiences', [])
                    ],
                    'skills': data.get('skills', []),
                    'summary': data.get('summary', ''),
                }
            }
            request.session.modified = True

        return JsonResponse(result)

    return render(request, 'resumes/linkedin_import.html')


# ── AI Summary Generation (updated to use LLM) ───────────────────────────────

@login_required
def generate_summary_ai(request):
    """
    AJAX endpoint: generate a professional summary using LLM.
    Falls back to rule-based if AI is unavailable.
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        wizard_data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        wizard_data = request.session.get('resume_wizard', {}).get('data', {})

    from apps.resumes.services.llm_service import LLMService
    result = LLMService.generate_summary(wizard_data)
    return JsonResponse({'summary': result['summary'], 'ai_powered': result['ai_powered']})


# ── Rejection Analysis View ───────────────────────────────────────────────────

@login_required
def rejection_analysis_resume(request, pk):
    """
    AI-powered analysis of why a resume may have been rejected for a specific role.
    """
    from django.http import JsonResponse
    resume = get_object_or_404(Resume, id=pk)

    if resume.user != request.user:
        return HttpResponseForbidden("You do not have permission to view this resume.")

    if request.method == 'POST':
        job_description = request.POST.get('job_description', '')
        company = request.POST.get('company', '')
        role = request.POST.get('role', '')

        from apps.resumes.services.llm_service import LLMService
        result = LLMService.analyse_rejection(resume, job_description, company, role)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(result)

        return render(request, 'resumes/rejection_analysis.html', {
            'resume': resume,
            'result': result,
            'job_description': job_description,
            'company': company,
            'role': role,
        })

    return render(request, 'resumes/rejection_analysis.html', {'resume': resume})
