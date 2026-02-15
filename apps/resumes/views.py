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
    """
    Display all resumes for the authenticated user.
    Shows resume title, template, last updated timestamp.
    Handles empty state with welcome message.
    """
    resumes = ResumeService.get_user_resumes(request.user)
    context = {
        'resumes': resumes,
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
    
    wizard_data = request.session['resume_wizard']
    current_step = wizard_data['step']
    
    # Log current wizard state for debugging
    logger.debug(f'Wizard Step {current_step}, Data keys: {list(wizard_data["data"].keys())}')
    
    if request.method == 'POST':
        # Handle form submission based on current step
        if current_step == 1:
            # Step 1: Resume title and template
            from .forms import ResumeForm
            form = ResumeForm(request.POST)
            if form.is_valid():
                wizard_data['data']['title'] = form.cleaned_data['title']
                wizard_data['data']['template'] = form.cleaned_data['template']
                wizard_data['step'] = 2
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 2:
            # Step 2: Personal information
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
                wizard_data['step'] = 3
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 3:
            # Step 3: Experience entries
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
                wizard_data['step'] = 4
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 4:
            # Step 4: Education entries
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
                wizard_data['step'] = 5
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 5:
            # Step 5: Skills
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
                wizard_data['step'] = 6
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 6:
            # Step 6: Projects
            action = request.POST.get('action')
            if action == 'add_project':
                from .forms import ProjectForm
                form = ProjectForm(request.POST)
                if form.is_valid():
                    if 'projects' not in wizard_data['data']:
                        wizard_data['data']['projects'] = []
                    wizard_data['data']['projects'].append({
                        'name': form.cleaned_data['name'],
                        'description': form.cleaned_data['description'],
                        'technologies': form.cleaned_data['technologies'],
                        'url': form.cleaned_data['url']
                    })
                    request.session.modified = True
                    messages.success(request, 'Project added successfully!')
                    return redirect('resume_create')
            elif action == 'next':
                wizard_data['step'] = 7
                request.session.modified = True
                return redirect('resume_create')
        
        elif current_step == 7:
            # Step 7: Review and save
            action = request.POST.get('action')
            if action == 'save':
                # Log wizard data for debugging
                logger.info(f'Creating resume with wizard data: {wizard_data["data"]}')
                
                # Convert date strings back to date objects for experiences
                from datetime import date
                if 'experiences' in wizard_data['data']:
                    for exp in wizard_data['data']['experiences']:
                        exp['start_date'] = date.fromisoformat(exp['start_date'])
                        if exp['end_date']:
                            exp['end_date'] = date.fromisoformat(exp['end_date'])
                
                # Create the resume
                resume = ResumeService.create_resume(request.user, wizard_data['data'])
                
                # Log what was created
                logger.info(f'Resume created: ID={resume.id}, Experiences={resume.experiences.count()}, Education={resume.education.count()}, Skills={resume.skills.count()}, Projects={resume.projects.count()}')
                
                # Clear wizard data
                del request.session['resume_wizard']
                request.session.modified = True
                
                messages.success(request, 'Resume created successfully!')
                return redirect('resume_detail', pk=resume.id)
    
    # Handle back button
    if request.GET.get('back'):
        if current_step > 1:
            wizard_data['step'] = current_step - 1
            request.session.modified = True
            return redirect('resume_create')
    
    # Prepare context based on current step
    context = {
        'step': current_step,
        'wizard_data': wizard_data['data']
    }
    
    # Add appropriate form for current step
    if current_step == 1:
        from .forms import ResumeForm
        context['form'] = ResumeForm(initial=wizard_data['data'])
    elif current_step == 2:
        from .forms import PersonalInfoForm
        context['form'] = PersonalInfoForm(initial=wizard_data['data'].get('personal_info', {}))
    elif current_step == 3:
        from .forms import ExperienceForm
        context['form'] = ExperienceForm()
        context['experiences'] = wizard_data['data'].get('experiences', [])
    elif current_step == 4:
        from .forms import EducationForm
        context['form'] = EducationForm()
        context['education'] = wizard_data['data'].get('education', [])
    elif current_step == 5:
        from .forms import SkillForm
        context['form'] = SkillForm()
        context['skills'] = wizard_data['data'].get('skills', [])
    elif current_step == 6:
        from .forms import ProjectForm
        context['form'] = ProjectForm()
        context['projects'] = wizard_data['data'].get('projects', [])
    
    return render(request, 'resumes/resume_create.html', context)

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
            'projects'
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
        'projects': resume.projects.all()
    }
    
    # Check if user wants to view the formatted template preview
    view_mode = request.GET.get('view', 'preview')
    
    if view_mode == 'template':
        # Render using the selected template (e.g., professional.html)
        template_name = f'resumes/{resume.template}.html'
        return render(request, template_name, context)
    else:
        # Default: show the detail view with action buttons
        return render(request, 'resumes/resume_detail.html', context)

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
    
    return render(request, 'resumes/resume_update.html', context)

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
    """
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to duplicate resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to duplicate this resume.")
    
    # Duplicate the resume
    duplicate = ResumeService.duplicate_resume(pk)
    messages.success(request, f'Resume duplicated successfully as "{duplicate.title}"')
    return redirect('resume_detail', pk=duplicate.id)

@login_required
def resume_export(request, pk):
    """
    Export resume to PDF.
    Verify resume belongs to authenticated user.
    Calls PDFExportService to generate PDF and returns as downloadable file.
    Supports optional version parameter to export specific version.
    """
    from .pdf_service import PDFExportService
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    
    try:
        # Generate PDF using the service
        pdf_bytes, resume = PDFExportService.generate_pdf(pk, version_id=version_id)
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        
        # Set headers for download
        filename = f"{resume.title.replace(' ', '_')}"
        if version_id:
            filename += f"_v{version_id}"
        filename += ".pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'PDF generated successfully for resume {pk}' + 
                   (f' version {version_id}' if version_id else '') +
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
    
    Requirements: 21.2, 21.5, 21.6
    """
    from .services.docx_export_service import DOCXExportService
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    
    try:
        # Generate DOCX using the service
        docx_bytes, resume = DOCXExportService.generate_docx(pk, version_id=version_id)
        
        # Create HTTP response with DOCX content
        response = HttpResponse(
            docx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Set headers for download
        filename = f"{resume.title.replace(' ', '_')}"
        if version_id:
            filename += f"_v{version_id}"
        filename += ".docx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'DOCX generated successfully for resume {pk}' +
                   (f' version {version_id}' if version_id else '') +
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
    
    Requirements: 21.3, 21.6
    """
    from .services.text_export_service import TextExportService
    
    resume = get_object_or_404(Resume, id=pk)
    
    # Authorization check
    if resume.user != request.user:
        logger.warning(f'Unauthorized access attempt: User {request.user.username} tried to export resume {pk} owned by {resume.user.username}')
        return HttpResponseForbidden("You do not have permission to export this resume.")
    
    # Get optional version parameter
    version_id = request.GET.get('version')
    
    try:
        # Generate plain text using the service
        text_content, resume = TextExportService.generate_text(pk, version_id=version_id)
        
        # Create HTTP response with plain text content
        response = HttpResponse(text_content, content_type='text/plain; charset=utf-8')
        
        # Set headers for download
        filename = f"{resume.title.replace(' ', '_')}"
        if version_id:
            filename += f"_v{version_id}"
        filename += ".txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f'Plain text generated successfully for resume {pk}' +
                   (f' version {version_id}' if version_id else '') +
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
# PDF Upload Module Views
# ============================================================================

@login_required
def pdf_upload(request):
    """
    Handle PDF resume upload with validation and parsing.
    
    GET: Display upload form
    POST: Validate file, extract text, parse sections, redirect to review
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.8
    """
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
    
    return render(request, 'resumes/parse_review.html', context)


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
        
        # Add personal info if available
        personal_info = parsed_data.get('personal_info', {})
        if personal_info and personal_info.get('name'):
            resume_data['personal_info'] = {
                'full_name': personal_info.get('name', ''),
                'email': personal_info.get('email', ''),
                'phone': personal_info.get('phone', ''),
                'linkedin': personal_info.get('linkedin', ''),
                'github': personal_info.get('website', ''),  # Map website to github field
                'location': personal_info.get('location', ''),
            }
        
        # Add experiences if available
        experiences = parsed_data.get('experiences', [])
        if experiences:
            resume_data['experiences'] = []
            for exp in experiences:
                # Convert date strings to date objects if possible
                from datetime import datetime
                start_date = None
                end_date = None
                
                # Try to parse start date
                if exp.get('start_date'):
                    try:
                        # Try various date formats
                        for fmt in ['%B %Y', '%m/%Y', '%Y']:
                            try:
                                start_date = datetime.strptime(exp['start_date'], fmt).date()
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
                
                # Try to parse end date
                if exp.get('end_date') and exp['end_date'].lower() not in ['present', 'current']:
                    try:
                        for fmt in ['%B %Y', '%m/%Y', '%Y']:
                            try:
                                end_date = datetime.strptime(exp['end_date'], fmt).date()
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
                
                # Use today's date as fallback for start_date if not parsed
                if not start_date:
                    start_date = datetime.today().date()
                
                resume_data['experiences'].append({
                    'company': exp.get('company', 'Unknown Company'),
                    'role': exp.get('title', 'Unknown Role'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': exp.get('description', ''),
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
                    'field': edu.get('field_of_study', 'Unknown Field'),
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
    context = {
        'resume': resume,
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
