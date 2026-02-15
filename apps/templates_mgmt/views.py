from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from apps.templates_mgmt.models import ResumeTemplate, TemplateCustomization
from apps.templates_mgmt.services.template_service import TemplateService
from apps.templates_mgmt.services.customization_service import CustomizationService
from apps.resumes.models import Resume


@login_required
def template_gallery(request):
    """
    Display all active templates in a gallery view.
    Shows thumbnails and allows preview/selection.
    """
    templates = TemplateService.get_all_templates()
    
    context = {
        'templates': templates,
        'page_title': 'Template Gallery'
    }
    
    return render(request, 'templates_mgmt/template_gallery.html', context)


@login_required
def template_preview(request, template_id):
    """
    Generate and display a preview of the template with sample data.
    Allows user to select the template for their resume.
    """
    template = get_object_or_404(ResumeTemplate, id=template_id, is_active=True)
    
    # Generate preview HTML with sample data
    preview_html = TemplateService.generate_preview_with_sample_data(template)
    
    # Get user's resumes for selection
    user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'template': template,
        'preview_html': preview_html,
        'user_resumes': user_resumes,
        'page_title': f'Preview: {template.name}'
    }
    
    return render(request, 'templates_mgmt/template_preview.html', context)


@login_required
def template_select(request, template_id, resume_id):
    """
    Select a template for a specific resume.
    Creates or updates the template customization.
    """
    template = get_object_or_404(ResumeTemplate, id=template_id, is_active=True)
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Create or update customization
    CustomizationService.create_or_update_customization(
        resume=resume,
        template=template
    )
    
    # Increment usage count
    TemplateService.increment_usage_count(template)
    
    messages.success(request, f'Template "{template.name}" has been applied to your resume.')
    return redirect('resume_detail', pk=resume_id)


@login_required
def template_customize(request, resume_id):
    """
    Customize template for a specific resume.
    Allows color scheme, font family, and custom CSS selection.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get or create customization
    try:
        customization = TemplateCustomization.objects.get(resume=resume)
        template = customization.template
    except TemplateCustomization.DoesNotExist:
        # Use default template if no customization exists
        template = TemplateService.get_default_template()
        if not template:
            messages.error(request, 'No templates available. Please contact support.')
            return redirect('resume_detail', pk=resume_id)
        customization = CustomizationService.create_or_update_customization(
            resume=resume,
            template=template
        )
    
    if request.method == 'POST':
        # Get form data
        color_scheme = request.POST.get('color_scheme', '')
        font_family = request.POST.get('font_family', '')
        custom_css = request.POST.get('custom_css', '')
        
        # Update customization
        CustomizationService.create_or_update_customization(
            resume=resume,
            template=template,
            color_scheme=color_scheme,
            font_family=font_family,
            custom_css=custom_css
        )
        
        messages.success(request, 'Template customization saved successfully!')
        return redirect('template_customize', resume_id=resume_id)
    
    # Get available options
    color_schemes = CustomizationService.get_available_color_schemes()
    fonts = CustomizationService.get_available_fonts()
    
    # Generate preview with current customization
    preview_html = _generate_customized_preview(resume, customization)
    
    context = {
        'resume': resume,
        'customization': customization,
        'template': template,
        'color_schemes': color_schemes,
        'fonts': fonts,
        'preview_html': preview_html,
        'page_title': f'Customize Template - {resume.title}'
    }
    
    return render(request, 'templates_mgmt/template_customize.html', context)


@login_required
def template_customize_preview(request, resume_id):
    """
    AJAX endpoint to generate live preview of customization changes.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get customization parameters from request
    color_scheme = request.POST.get('color_scheme', '')
    font_family = request.POST.get('font_family', '')
    custom_css = request.POST.get('custom_css', '')
    
    try:
        customization = TemplateCustomization.objects.get(resume=resume)
        template = customization.template
    except TemplateCustomization.DoesNotExist:
        template = TemplateService.get_default_template()
        if not template:
            return JsonResponse({'error': 'No template available'}, status=400)
    
    # Create temporary customization object (not saved)
    temp_customization = TemplateCustomization(
        resume=resume,
        template=template,
        color_scheme=color_scheme,
        font_family=font_family,
        custom_css=custom_css
    )
    
    # Generate preview
    preview_html = _generate_customized_preview(resume, temp_customization)
    
    return JsonResponse({'preview_html': preview_html})


def _generate_customized_preview(resume, customization):
    """
    Helper function to generate preview HTML with customization applied.
    
    Args:
        resume: Resume object
        customization: TemplateCustomization object
        
    Returns:
        str: Rendered HTML with customizations
    """
    # Get resume data
    context = {
        'resume': resume,
        'personal_info': resume.personal_info if hasattr(resume, 'personal_info') else None,
        'experiences': resume.experiences.all().order_by('-start_date'),
        'education': resume.education.all().order_by('-start_year'),
        'skills': resume.skills.all(),
        'projects': resume.projects.all()
    }
    
    # Render base template
    html = render_to_string(customization.template.template_file, context)
    
    # Apply customizations
    html = CustomizationService.apply_customization(html, customization)
    
    return html


