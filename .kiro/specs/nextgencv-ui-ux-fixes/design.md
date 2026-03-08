# Design Document

## Overview

This design addresses critical UI/UX issues and missing functionality in the NextGenCV application. The solution focuses on five main areas:

1. **Landing Page Enhancement** - Adding visual assets and improving styling
2. **Form Input Visibility** - Fixing text color contrast issues
3. **Resume Wizard Completion** - Implementing Step 5 functionality and finish flow
4. **Analytics Dashboard** - Populating empty chart with actual data
5. **Template Gallery** - Adding preview images and interactive elements

The design prioritizes immediate user-facing fixes that prevent users from completing core workflows.

## Architecture

### Component Structure

```
NextGenCV Application
├── Public Pages
│   └── Landing Page (Enhanced)
│       ├── Hero Section (with images)
│       ├── Features Section (with icons)
│       └── CTA Section (optimized)
├── Authenticated Pages
│   ├── Resume Wizard
│   │   ├── Step 1-4 (Form fixes)
│   │   ├── Step 5 (Summary + Finish)
│   │   └── Wizard Navigation
│   ├── Analytics Dashboard
│   │   └── Score Trend Chart (populated)
│   └── Template Gallery
│       ├── Template Cards (with previews)
│       └── Preview Modal (new)
└── Shared Components
    ├── Form Inputs (styled)
    └── Design System (CSS variables)
```

### Technology Stack

- **Frontend**: Django Templates, HTML5, CSS3, JavaScript
- **Charts**: Chart.js 4.4.0
- **Icons**: Bootstrap Icons
- **Backend**: Django 4.x, Python 3.x
- **Database**: SQLite (existing)

## Components and Interfaces

### 1. Landing Page Enhancement

**Component**: `templates/landing_new.html`

**Changes**:
- Add hero section background image or illustration
- Add feature section icon images
- Add product screenshot/mockup images
- Enhance CSS for better visual hierarchy
- Add hover effects and animations

**Assets Required**:
- Hero background image (1920x1080px)
- Feature icons (3 icons, SVG or PNG)
- Product screenshots (2-3 images)

### 2. Form Input Styling System

**Component**: Global CSS in design system

**CSS Variables to Add/Update**:
```css
:root {
  /* Form Input Colors */
  --form-input-bg: #1a1a1a;
  --form-input-bg-focus: #242424;
  --form-input-text: #f5f5f5;
  --form-input-placeholder: #737373;
  --form-input-border: rgba(255, 255, 255, 0.08);
  --form-input-border-focus: #0066ff;
  --form-input-border-error: #ef4444;
}
```

**Form Input Classes**:
```css
.form-control, .form-input, input[type="text"], 
input[type="email"], input[type="tel"], 
input[type="url"], textarea, select {
  background-color: var(--form-input-bg);
  color: var(--form-input-text);
  border: 1px solid var(--form-input-border);
  /* ... other properties */
}

.form-control::placeholder {
  color: var(--form-input-placeholder);
  opacity: 0.7;
}
```

### 3. Resume Wizard Step 5 Implementation

**Component**: `apps/resumes/views.py` - Resume wizard view

**Backend Changes**:

```python
def resume_wizard_step_5(request, resume_id):
    """Handle Step 5: Professional Summary"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Handle AI summary generation
        if request.POST.get('action') == 'generate_summary':
            summary = generate_ai_summary(resume)
            return JsonResponse({'summary': summary})
        
        # Handle finish button
        if 'finish' in request.POST or request.POST.get('step') == 'finish':
            form = SummaryForm(request.POST, instance=resume)
            if form.is_valid():
                resume = form.save(commit=False)
                resume.is_draft = False
                resume.save()
                messages.success(request, 'Resume created successfully!')
                return redirect('resume_detail', pk=resume.id)
        
        # Handle autosave
        if request.POST.get('autosave'):
            form = SummaryForm(request.POST, instance=resume)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
    
    form = SummaryForm(instance=resume)
    return render(request, 'resumes/wizard_steps/step5_summary.html', {
        'form': form,
        'resume': resume,
        'step': 5
    })
```

**Form Class**:
```python
class SummaryForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['summary']
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 6,
                'maxlength': 500,
                'placeholder': 'Write a brief professional summary...'
            })
        }
```

### 4. Analytics Dashboard Chart Population

**Component**: `apps/analytics/views.py`

**Data Retrieval Logic**:

```python
def get_score_trend_data(user, days=30):
    """Get ATS score trend data for charts"""
    from datetime import timedelta
    from django.utils import timezone
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all resume analyses in date range
    analyses = ResumeAnalysis.objects.filter(
        resume__user=user,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('created_at')
    
    if not analyses.exists():
        return {
            'labels': [],
            'scores': [],
            'moving_average': []
        }
    
    labels = []
    scores = []
    
    for analysis in analyses:
        labels.append(analysis.created_at.strftime('%b %d'))
        scores.append(analysis.ats_score)
    
    # Calculate moving average
    moving_average = calculate_moving_average(scores, window=3)
    
    return {
        'labels': labels,
        'scores': scores,
        'moving_average': moving_average
    }
```

**View Update**:
```python
def analytics_dashboard(request):
    user = request.user
    resumes = Resume.objects.filter(user=user)
    
    if not resumes.exists():
        return render(request, 'analytics/dashboard_new.html', {
            'has_resumes': False,
            'message': 'No resumes found'
        })
    
    # Get chart data
    score_trend = get_score_trend_data(user)
    health_by_resume = get_health_by_resume(user)
    
    chart_data = {
        'score_trend': score_trend,
        'health_by_resume': health_by_resume
    }
    
    return render(request, 'analytics/dashboard_new.html', {
        'has_resumes': True,
        'chart_data_json': json.dumps(chart_data),
        'total_resumes': resumes.count(),
        # ... other stats
    })
```

### 5. Template Gallery Card Enhancement

**Component**: `templates/templates_mgmt/template_gallery_new.html`

**Template Card Structure**:
```html
<div class="template-card">
    <div class="template-card__preview">
        <img src="{{ template.thumbnail.url }}" alt="{{ template.name }}">
        <button class="template-card__preview-btn" onclick="openPreview({{ template.id }})">
            <i class="bi bi-eye"></i>
        </button>
    </div>
    <div class="template-card__body">
        <h3>{{ template.name }}</h3>
        <p>{{ template.description }}</p>
        <button class="btn btn-primary" onclick="useTemplate({{ template.id }})">
            Use Template
        </button>
    </div>
</div>
```

**Preview Modal Component**:
```html
<div id="templatePreviewModal" class="modal">
    <div class="modal__backdrop" onclick="closePreview()"></div>
    <div class="modal__content">
        <button class="modal__close" onclick="closePreview()">
            <i class="bi bi-x"></i>
        </button>
        <div class="modal__body" id="previewContent">
            <!-- Template preview loaded here -->
        </div>
        <div class="modal__footer">
            <button class="btn btn-outline" onclick="closePreview()">Close</button>
            <button class="btn btn-primary" onclick="useCurrentTemplate()">Use This Template</button>
        </div>
    </div>
</div>
```

**JavaScript Functions**:
```javascript
function openPreview(templateId) {
    fetch(`/templates/preview/${templateId}/`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('previewContent').innerHTML = html;
            document.getElementById('templatePreviewModal').classList.add('modal--open');
            document.body.style.overflow = 'hidden';
        });
}

function closePreview() {
    document.getElementById('templatePreviewModal').classList.remove('modal--open');
    document.body.style.overflow = '';
}

function useTemplate(templateId) {
    window.location.href = `/resumes/create/?template=${templateId}`;
}
```

## Data Models

### Existing Models (No Changes Required)

**Resume Model** - Already has `summary` field
```python
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)  # Already exists
    is_draft = models.BooleanField(default=True)
    # ... other fields
```

**ResumeAnalysis Model** - Already tracks ATS scores
```python
class ResumeAnalysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    ats_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    # ... other fields
```

**ResumeTemplate Model** - Needs thumbnail field
```python
class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='templates/', blank=True, null=True)  # ADD THIS
    # ... other fields
```

### Database Migration Required

```python
# Migration: Add thumbnail field to ResumeTemplate
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('templates_mgmt', '0003_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumetemplate',
            name='thumbnail',
            field=models.ImageField(upload_to='templates/', blank=True, null=True),
        ),
    ]
```



### 6. Template Preview Loading Reliability

**Component**: `apps/templates_mgmt/views.py` and `apps/templates_mgmt/services/template_service.py`

**Problem Analysis**:
The template preview modal is failing to load with error "Failed to load preview. Please try again." This indicates one of the following issues:
1. Template file path in database doesn't exist or is incorrect
2. Template rendering is throwing an exception
3. Sample data structure doesn't match template expectations
4. Missing error handling in the view

**Solution Design**:

**Enhanced Error Handling in View**:
```python
@login_required
def template_preview(request, template_id):
    """
    Generate and display a preview of the template with sample data.
    Enhanced with comprehensive error handling and logging.
    """
    try:
        template = get_object_or_404(ResumeTemplate, id=template_id, is_active=True)
    except Http404:
        logger.error(f"Template {template_id} not found or inactive")
        return JsonResponse({
            'error': 'Template not found',
            'message': 'The requested template does not exist or is no longer available.'
        }, status=404)
    
    try:
        # Generate preview HTML with sample data
        preview_html = TemplateService.generate_preview_with_sample_data(template)
        
        # Validate that HTML was generated
        if not preview_html or preview_html.startswith("<p>Error"):
            raise ValueError("Template rendering failed")
        
        # Get user's resumes for selection
        user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
        
        context = {
            'template': template,
            'preview_html': preview_html,
            'user_resumes': user_resumes,
            'page_title': f'Preview: {template.name}'
        }
        
        return render(request, 'templates_mgmt/template_preview.html', context)
        
    except Exception as e:
        logger.error(f"Error generating preview for template {template_id}: {str(e)}", exc_info=True)
        
        # Return error response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Preview generation failed',
                'message': f'Unable to generate preview: {str(e)}',
                'template_id': template_id,
                'template_name': template.name if template else 'Unknown'
            }, status=500)
        
        # For regular requests, render error page
        return render(request, 'templates_mgmt/template_preview.html', {
            'error': True,
            'error_message': f'Unable to generate preview: {str(e)}',
            'template': template
        }, status=500)
```

**Enhanced Template Service**:
```python
@staticmethod
def generate_preview_with_sample_data(template):
    """
    Generate a preview of the template using sample data.
    Enhanced with validation and error handling.
    
    Args:
        template (ResumeTemplate): Template to preview
        
    Returns:
        str: Rendered HTML with sample data
        
    Raises:
        ValueError: If template file is invalid
        TemplateDoesNotExist: If template file not found
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate template file path
    if not template.template_file:
        logger.error(f"Template {template.id} has no template_file set")
        raise ValueError("Template file path is not configured")
    
    # Sample data for preview (same as before but validated)
    sample_data = {
        'resume': type('obj', (object,), {
            'title': 'Sample Resume',
            'summary': 'Experienced professional with expertise in software development...'
        })(),
        'personal_info': type('obj', (object,), {
            'full_name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '(555) 123-4567',
            'location': 'San Francisco, CA',
            'linkedin': 'linkedin.com/in/johndoe',
            'github': 'github.com/johndoe'
        })(),
        'experiences': [
            type('obj', (object,), {
                'role': 'Senior Software Engineer',
                'company': 'Tech Company Inc.',
                'start_date': '2021-01-01',
                'end_date': None,
                'description': 'Led development of scalable web applications...'
            })()
        ],
        'education': [
            type('obj', (object,), {
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'institution': 'University of California',
                'start_year': 2015,
                'end_year': 2019
            })()
        ],
        'skills': [
            type('obj', (object,), {'name': 'Python', 'category': 'Programming Languages'})(),
            type('obj', (object,), {'name': 'Django', 'category': 'Frameworks'})(),
        ],
        'projects': [
            type('obj', (object,), {
                'name': 'E-commerce Platform',
                'url': 'github.com/johndoe/ecommerce',
                'description': 'Built a full-stack e-commerce platform...',
                'technologies': 'Django, React, PostgreSQL'
            })()
        ]
    }
    
    # Render the template with sample data
    try:
        html = render_to_string(template.template_file, sample_data)
        logger.info(f"Successfully rendered preview for template {template.id}")
        return html
    except TemplateDoesNotExist as e:
        logger.error(f"Template file not found: {template.template_file}")
        raise ValueError(f"Template file '{template.template_file}' does not exist")
    except Exception as e:
        logger.error(f"Error rendering template {template.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Template rendering error: {str(e)}")
```

**Frontend JavaScript Enhancement**:
```javascript
function openTemplatePreview(templateId) {
    currentTemplateId = templateId;
    const modal = document.getElementById('templatePreviewModal');
    const previewContent = document.getElementById('previewContent');
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Show loading state
    previewContent.innerHTML = `
        <div style="text-align: center; color: var(--color-text-secondary);">
            <i class="bi bi-hourglass-split" style="font-size: 48px; margin-bottom: 1rem; display: block; animation: spin 2s linear infinite;"></i>
            <p>Loading preview...</p>
        </div>
    `;
    
    // Fetch preview content with enhanced error handling
    fetch(`/templates/preview/${templateId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (!response.ok) {
                // Try to parse error JSON
                return response.json().then(errorData => {
                    throw new Error(errorData.message || 'Failed to load preview');
                }).catch(() => {
                    throw new Error(`Server error: ${response.status}`);
                });
            }
            return response.text();
        })
        .then(html => {
            // Create iframe to display preview
            previewContent.innerHTML = `<iframe srcdoc="${html.replace(/"/g, '&quot;')}"></iframe>`;
            
            // Update modal title
            const templateCard = event.target.closest('.card-elevated');
            if (templateCard) {
                const templateName = templateCard.querySelector('h3').textContent.trim();
                document.getElementById('modalTemplateName').textContent = templateName;
            }
        })
        .catch(error => {
            console.error('Error loading preview:', error);
            previewContent.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 48px; margin-bottom: 1rem; display: block; color: var(--color-danger, #ef4444);"></i>
                    <h3 style="color: var(--color-text-primary); margin-bottom: 0.5rem;">Preview Unavailable</h3>
                    <p style="color: var(--color-text-secondary); margin-bottom: 1.5rem;">${error.message}</p>
                    <div style="background: var(--color-base-bg-hover); padding: 1rem; border-radius: 8px; text-align: left; max-width: 500px; margin: 0 auto;">
                        <p style="font-size: 0.875rem; color: var(--color-text-tertiary); margin-bottom: 0.5rem;"><strong>Troubleshooting:</strong></p>
                        <ul style="font-size: 0.875rem; color: var(--color-text-tertiary); margin: 0; padding-left: 1.5rem;">
                            <li>Check that the template file exists</li>
                            <li>Verify template configuration in admin panel</li>
                            <li>Try refreshing the page</li>
                            <li>Contact support if the issue persists</li>
                        </ul>
                    </div>
                </div>
            `;
        });
}
```

**Diagnostic Management Command**:
```python
# management/commands/check_templates.py
from django.core.management.base import BaseCommand
from apps.templates_mgmt.models import ResumeTemplate
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

class Command(BaseCommand):
    help = 'Check all templates for validity'

    def handle(self, *args, **options):
        templates = ResumeTemplate.objects.all()
        
        for template in templates:
            self.stdout.write(f"\nChecking template: {template.name} (ID: {template.id})")
            
            # Check template file
            if not template.template_file:
                self.stdout.write(self.style.ERROR(f"  ✗ No template_file set"))
                continue
            
            try:
                get_template(template.template_file)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Template file exists: {template.template_file}"))
            except TemplateDoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ Template file not found: {template.template_file}"))
            
            # Check thumbnail
            if template.thumbnail:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Thumbnail exists"))
            else:
                self.stdout.write(self.style.WARNING(f"  ! No thumbnail set"))
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

- **Form Input Styling (2.1, 2.2, 2.3)**: These three criteria all relate to text contrast. They can be combined into one comprehensive contrast property.
- **Form Input Consistency (9.1, 9.2, 9.3, 9.4, 9.5)**: All five criteria test CSS consistency across form inputs. These can be combined into one property that checks multiple CSS properties.
- **Template Card Elements (7.2, 7.4)**: Both test that specific elements exist in template cards. These can be combined.
- **Modal Closing (8.3, 8.4)**: Both test modal closing behavior through different triggers. These can be combined.

### Properties

Property 1: Form Input Text Contrast
*For any* form input element with a background color, the text color should have a contrast ratio of at least 4.5:1 with the background, meeting WCAG AA standards
**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Form Input Focus Visibility
*For any* form input element, when it receives focus, it should have a visible focus indicator that differs from its default state (different border color, outline, or box-shadow)
**Validates: Requirements 2.4**

Property 3: Placeholder Color Distinction
*For any* form input with placeholder text, the placeholder color should be different from the input text color and have lower opacity or lighter shade
**Validates: Requirements 2.5**

Property 4: Form Label Positioning
*For any* form field in the resume wizard, the label element should appear before (above) its corresponding input element in the DOM structure
**Validates: Requirements 3.1**

Property 5: Form Input Padding Consistency
*For all* form input elements (text, email, tel, url, textarea, select), the padding values should be identical
**Validates: Requirements 3.2**

Property 6: Form Input Transition Definition
*For all* form input elements, the CSS transition property should be defined for smooth state changes
**Validates: Requirements 3.4**

Property 7: Responsive Layout Integrity
*For any* viewport width between 320px and 1920px, form elements in the resume wizard should not overflow their containers and should maintain minimum readable dimensions
**Validates: Requirements 3.5**

Property 8: Summary Field Data Persistence
*For any* text entered in the summary field, after saving and reloading the page, the same text should be retrieved from the database
**Validates: Requirements 4.2, 4.5**

Property 9: Live Preview Synchronization
*For any* text entered in the summary field, the live preview panel should display that exact text within 100ms
**Validates: Requirements 4.3**

Property 10: Resume Completion State
*For any* resume that goes through the finish action, the is_draft field should be set to False in the database
**Validates: Requirements 5.1, 5.5**

Property 11: Chart Data Chronological Ordering
*For any* set of resume analyses belonging to a user, when displayed in the ATS Score Trend chart, the data points should be ordered chronologically by creation date
**Validates: Requirements 6.1, 6.3**

Property 12: Template Card Required Elements
*For any* template card in the gallery, it should contain both a thumbnail image element and a "Use Template" button element
**Validates: Requirements 7.1, 7.2, 7.4**

Property 13: Landing Page Design System Consistency
*For all* elements on the landing page, spacing, typography, and colors should use CSS variables from the design system (--space-*, --font-*, --color-*)
**Validates: Requirements 1.4**

Property 14: Responsive Image Scaling
*For any* image on the landing page, at viewport widths below 768px, the image should have max-width: 100% and height: auto to scale appropriately
**Validates: Requirements 1.5**

Property 15: Form Input Style Consistency
*For all* form input elements across the application, the following CSS properties should have identical values: border-radius, font-size, font-family, and height
**Validates: Requirements 9.1, 9.2, 9.3**

Property 16: Form Input State Consistency
*For all* form input elements, focus state styling (border-color, box-shadow) and error state styling (border-color, background-color) should be consistent across all inputs
**Validates: Requirements 9.4, 9.5**

Property 17: CTA Button Contrast
*For all* call-to-action buttons on the landing page, the text color should have a contrast ratio of at least 4.5:1 with the button background color
**Validates: Requirements 10.4**

Property 18: CTA Button Hover State
*For all* call-to-action buttons, the hover state should have at least one CSS property (background-color, transform, or box-shadow) that differs from the default state
**Validates: Requirements 10.5**

Property 19: Template Preview Error Handling
*For any* template with an invalid or missing template file, when preview is requested, the system should return a structured error response with a helpful message rather than throwing an unhandled exception
**Validates: Requirements 11.2, 11.3**

Property 20: Template Preview Success Response
*For any* valid template with a properly configured template file, when preview is requested, the system should return rendered HTML within 3 seconds
**Validates: Requirements 11.1, 11.5**

Property 21: Template Preview Default Data
*For any* template that successfully renders, the preview should contain all required sections (personal info, experience, education, skills) even when using default sample data
**Validates: Requirements 11.4**

## Error Handling

### Form Validation Errors

**Scenario**: User submits Step 5 with invalid data
- Display field-specific error messages below each invalid field
- Maintain user's entered data (don't clear the form)
- Scroll to the first error
- Prevent navigation to next step

**Scenario**: Network error during autosave
- Display temporary error notification
- Retry autosave after 5 seconds
- Don't block user from continuing to type

### Database Errors

**Scenario**: Resume save fails on finish
- Display error message: "Failed to save resume. Please try again."
- Keep user on Step 5
- Log error details for debugging
- Preserve all form data

**Scenario**: Analytics data query fails
- Display empty state with message: "Unable to load analytics data"
- Provide retry button
- Log error for monitoring

### Asset Loading Errors

**Scenario**: Template thumbnail fails to load
- Display placeholder icon instead
- Don't break card layout
- Log missing thumbnail for admin review

**Scenario**: Chart.js library fails to load
- Display message: "Charts temporarily unavailable"
- Show raw data in table format as fallback
- Log error for monitoring

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples, edge cases, and error conditions:

**Landing Page Tests**:
- Test that hero section contains image element
- Test that feature section contains 3 icon elements
- Test that CTA buttons link to correct URLs
- Test responsive breakpoints trigger correct CSS

**Form Input Tests**:
- Test form input with white background has dark text
- Test form input with dark background has light text
- Test placeholder color differs from input text color
- Test focus state adds focus indicator class
- Test error state adds error class

**Resume Wizard Tests**:
- Test Step 5 renders summary textarea
- Test finish button submits form
- Test finish button redirects to resume detail
- Test error on save displays error message
- Test autosave triggers after 1 second of inactivity

**Analytics Tests**:
- Test empty state displays when no data
- Test chart renders with valid data
- Test date range filter updates chart
- Test chart data is ordered by date

**Template Gallery Tests**:
- Test template cards render for each template
- Test preview modal opens on eye icon click
- Test preview modal closes on backdrop click
- Test preview modal closes on Escape key
- Test use button navigates with template ID

### Property-Based Tests

Property-based tests will verify universal properties across all inputs using Hypothesis (Python):

**Test Configuration**:
- Minimum 100 iterations per property test
- Use Hypothesis for generating test data
- Tag each test with feature name and property number

**Property Test Examples**:

```python
from hypothesis import given, strategies as st
from hypothesis import settings

@settings(max_examples=100)
@given(
    bg_color=st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
    text_color=st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))
)
def test_form_input_contrast_property(bg_color, text_color):
    """
    Feature: nextgencv-ui-ux-fixes, Property 1: Form Input Text Contrast
    For any form input with background and text colors, contrast ratio >= 4.5:1
    """
    contrast_ratio = calculate_contrast_ratio(bg_color, text_color)
    assert contrast_ratio >= 4.5

@settings(max_examples=100)
@given(summary_text=st.text(min_size=1, max_size=500))
def test_summary_persistence_property(summary_text, client, user):
    """
    Feature: nextgencv-ui-ux-fixes, Property 8: Summary Field Data Persistence
    For any text entered in summary, it should persist after save and reload
    """
    resume = create_test_resume(user)
    
    # Save summary
    client.post(f'/resumes/wizard/{resume.id}/step5/', {
        'summary': summary_text,
        'finish': 'true'
    })
    
    # Reload from database
    resume.refresh_from_db()
    
    assert resume.summary == summary_text

@settings(max_examples=100)
@given(
    analyses=st.lists(
        st.tuples(st.datetimes(), st.integers(0, 100)),
        min_size=2,
        max_size=20
    )
)
def test_chart_chronological_ordering_property(analyses, user):
    """
    Feature: nextgencv-ui-ux-fixes, Property 11: Chart Data Chronological Ordering
    For any set of analyses, chart data should be ordered by date
    """
    # Create analyses in random order
    for date, score in analyses:
        create_analysis(user, date, score)
    
    # Get chart data
    chart_data = get_score_trend_data(user)
    
    # Verify chronological order
    dates = [parse_date(label) for label in chart_data['labels']]
    assert dates == sorted(dates)
```

### Integration Tests

Integration tests will verify end-to-end workflows:

- Complete resume creation flow from Step 1 to Step 5 finish
- Template selection to resume creation
- Analytics dashboard data flow from analysis to chart display
- Form autosave and recovery flow

### Manual Testing Checklist

- [ ] Landing page displays correctly on desktop and mobile
- [ ] All form inputs are readable with current color scheme
- [ ] Resume wizard completes successfully and redirects
- [ ] Analytics charts populate with real data
- [ ] Template gallery cards display thumbnails
- [ ] Template preview modal opens and closes correctly
- [ ] All hover states provide visual feedback
- [ ] Keyboard navigation works for modal and forms
