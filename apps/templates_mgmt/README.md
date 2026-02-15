# Template Management System

This module provides comprehensive template management functionality for NextGenCV, including template selection, customization, and preview capabilities.

## Features

- **Template Gallery**: Browse and preview available resume templates
- **Template Customization**: Customize colors, fonts, and add custom CSS
- **Live Preview**: Real-time preview of customization changes
- **ATS-Safe**: All templates and customizations are ATS-friendly

## Available Templates

1. **Professional** (Default) - Clean and professional template suitable for corporate positions
2. **Modern** - Contemporary design with modern styling for tech roles
3. **Classic** - Traditional format ideal for conservative industries
4. **Creative** - Eye-catching design for creative professionals
5. **Minimal** - Simple and clean layout focusing on content

## Services

### TemplateService

Handles template CRUD operations and preview generation.

```python
from apps.templates_mgmt.services import TemplateService

# Get all active templates
templates = TemplateService.get_all_templates()

# Get specific template
template = TemplateService.get_template_by_id(template_id)

# Get default template
default = TemplateService.get_default_template()

# Generate preview with sample data
preview_html = TemplateService.generate_preview_with_sample_data(template)

# Increment usage count
TemplateService.increment_usage_count(template)
```

### CustomizationService

Handles template customization including colors, fonts, and custom CSS.

```python
from apps.templates_mgmt.services import CustomizationService

# Apply customization to HTML
customized_html = CustomizationService.apply_customization(html, customization)

# Apply color scheme
html = CustomizationService.apply_color_scheme(html, 'professional')

# Apply font family
html = CustomizationService.apply_font_family(html, 'Arial')

# Inject custom CSS
html = CustomizationService.inject_custom_css(html, custom_css)

# Get available options
color_schemes = CustomizationService.get_available_color_schemes()
fonts = CustomizationService.get_available_fonts()

# Create or update customization
customization = CustomizationService.create_or_update_customization(
    resume=resume,
    template=template,
    color_scheme='modern',
    font_family='Calibri',
    custom_css='/* custom styles */'
)
```

## URL Patterns

- `/templates/gallery/` - Template gallery view
- `/templates/preview/<template_id>/` - Preview specific template
- `/templates/select/<template_id>/<resume_id>/` - Select template for resume
- `/templates/customize/<resume_id>/` - Customize template for resume
- `/templates/customize/<resume_id>/preview/` - AJAX endpoint for live preview

## Models

### ResumeTemplate

Stores template metadata and configuration.

Fields:
- `name` - Template name (unique)
- `description` - Template description
- `template_file` - Path to HTML template file
- `thumbnail` - Template thumbnail image
- `is_active` - Whether template is active
- `is_default` - Whether template is default
- `usage_count` - Number of times template has been used
- `supports_color_customization` - Whether template supports color customization
- `supports_font_customization` - Whether template supports font customization
- `available_colors` - List of available color schemes
- `available_fonts` - List of available fonts

### TemplateCustomization

Stores user-specific template customizations.

Fields:
- `resume` - One-to-one relationship with Resume
- `template` - Foreign key to ResumeTemplate
- `color_scheme` - Selected color scheme
- `font_family` - Selected font family
- `custom_css` - Custom CSS code
- `created_at` - Creation timestamp

## Color Schemes

Available color schemes:
- `professional` - Blue and gray tones
- `modern` - Dark and blue tones
- `creative` - Colorful with blue accents
- `minimal` - Black and white

## ATS-Safe Fonts

All fonts are ATS-safe:
- Arial
- Helvetica
- Calibri
- Times New Roman
- Georgia
- Verdana

## Management Commands

### populate_templates

Populates the database with default templates.

```bash
python manage.py populate_templates
```

## Usage Example

```python
from apps.templates_mgmt.services import TemplateService, CustomizationService
from apps.resumes.models import Resume

# Get user's resume
resume = Resume.objects.get(id=1)

# Get template
template = TemplateService.get_template_by_id(2)

# Create customization
customization = CustomizationService.create_or_update_customization(
    resume=resume,
    template=template,
    color_scheme='modern',
    font_family='Calibri'
)

# Generate customized HTML
from django.template.loader import render_to_string

context = {
    'resume': resume,
    'personal_info': resume.personal_info,
    'experiences': resume.experiences.all(),
    'education': resume.education.all(),
    'skills': resume.skills.all(),
    'projects': resume.projects.all()
}

html = render_to_string(template.template_file, context)
customized_html = CustomizationService.apply_customization(html, customization)
```

## Security

- Custom CSS is sanitized to prevent XSS attacks
- Only ATS-safe fonts are allowed
- Template files are validated before rendering
- User data isolation is enforced at the database level

## Future Enhancements

- Template marketplace for user-created templates
- More color schemes and customization options
- Template versioning
- A/B testing for template effectiveness
- Template analytics and recommendations
