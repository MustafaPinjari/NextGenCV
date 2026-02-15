"""
Management command to populate the database with default resume templates.
Usage: python manage.py populate_templates
"""
from django.core.management.base import BaseCommand
from apps.templates_mgmt.models import ResumeTemplate, DEFAULT_COLOR_SCHEMES, ATS_SAFE_FONTS


class Command(BaseCommand):
    help = 'Populate the database with default resume templates'

    def handle(self, *args, **options):
        self.stdout.write('Populating resume templates...')
        
        templates_data = [
            {
                'name': 'Professional',
                'description': 'Clean and professional template suitable for corporate positions',
                'template_file': 'resumes/professional.html',
                'is_default': True,
                'available_colors': list(DEFAULT_COLOR_SCHEMES.keys()),
                'available_fonts': ATS_SAFE_FONTS
            },
            {
                'name': 'Modern',
                'description': 'Contemporary design with modern styling for tech roles',
                'template_file': 'resumes/modern.html',
                'is_default': False,
                'available_colors': list(DEFAULT_COLOR_SCHEMES.keys()),
                'available_fonts': ATS_SAFE_FONTS
            },
            {
                'name': 'Classic',
                'description': 'Traditional format ideal for conservative industries',
                'template_file': 'resumes/classic.html',
                'is_default': False,
                'available_colors': list(DEFAULT_COLOR_SCHEMES.keys()),
                'available_fonts': ATS_SAFE_FONTS
            },
            {
                'name': 'Creative',
                'description': 'Eye-catching design for creative professionals',
                'template_file': 'resumes/creative.html',
                'is_default': False,
                'available_colors': list(DEFAULT_COLOR_SCHEMES.keys()),
                'available_fonts': ATS_SAFE_FONTS
            },
            {
                'name': 'Minimal',
                'description': 'Simple and clean layout focusing on content',
                'template_file': 'resumes/minimal.html',
                'is_default': False,
                'available_colors': list(DEFAULT_COLOR_SCHEMES.keys()),
                'available_fonts': ATS_SAFE_FONTS
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates_data:
            template, created = ResumeTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'template_file': template_data['template_file'],
                    'is_default': template_data['is_default'],
                    'is_active': True,
                    'supports_color_customization': True,
                    'supports_font_customization': True,
                    'available_colors': template_data['available_colors'],
                    'available_fonts': template_data['available_fonts']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated template: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created: {created_count}, Updated: {updated_count}'
            )
        )
