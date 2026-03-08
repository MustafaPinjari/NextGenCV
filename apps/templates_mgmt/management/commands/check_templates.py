"""
Management command to check all templates for validity.
Validates template files, thumbnails, and configuration.
"""
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from apps.templates_mgmt.models import ResumeTemplate


class Command(BaseCommand):
    help = 'Check all templates for validity and report issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information for all templates',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n=== Template Validation Report ===\n'))
        
        templates = ResumeTemplate.objects.all()
        
        if not templates.exists():
            self.stdout.write(self.style.WARNING('No templates found in database.'))
            return
        
        total_count = templates.count()
        active_count = templates.filter(is_active=True).count()
        issues_count = 0
        
        self.stdout.write(f'Total templates: {total_count}')
        self.stdout.write(f'Active templates: {active_count}\n')
        
        for template in templates:
            has_issues = False
            
            # Header for each template
            status_indicator = '✓' if template.is_active else '○'
            self.stdout.write(f'\n{status_indicator} Template: {template.name} (ID: {template.id})')
            
            if not template.is_active and verbose:
                self.stdout.write(self.style.WARNING('  ⚠ Template is inactive'))
            
            # Check template file
            if not template.template_file:
                self.stdout.write(self.style.ERROR('  ✗ No template_file set'))
                has_issues = True
            else:
                try:
                    get_template(template.template_file)
                    if verbose:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Template file exists: {template.template_file}'))
                except TemplateDoesNotExist:
                    self.stdout.write(self.style.ERROR(f'  ✗ Template file not found: {template.template_file}'))
                    has_issues = True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error loading template: {str(e)}'))
                    has_issues = True
            
            # Check thumbnail
            if template.thumbnail:
                if verbose:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Thumbnail exists: {template.thumbnail.name}'))
            else:
                self.stdout.write(self.style.WARNING('  ! No thumbnail set'))
                has_issues = True
            
            # Check description
            if not template.description:
                self.stdout.write(self.style.WARNING('  ! No description set'))
                has_issues = True
            elif verbose:
                self.stdout.write(self.style.SUCCESS('  ✓ Description exists'))
            
            # Check usage count
            if verbose:
                self.stdout.write(f'  ℹ Usage count: {template.usage_count}')
            
            # Check default status
            if template.is_default and verbose:
                self.stdout.write(self.style.SUCCESS('  ✓ Marked as default template'))
            
            if has_issues:
                issues_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(f'Templates checked: {total_count}')
        self.stdout.write(f'Templates with issues: {issues_count}')
        
        if issues_count == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ All templates are valid!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {issues_count} template(s) have issues that need attention.'))
        
        # Recommendations
        self.stdout.write(self.style.SUCCESS('\n=== Recommendations ==='))
        
        # Check for default template
        default_templates = ResumeTemplate.objects.filter(is_default=True, is_active=True)
        if not default_templates.exists():
            self.stdout.write(self.style.WARNING('⚠ No default template set. Consider marking one template as default.'))
        elif default_templates.count() > 1:
            self.stdout.write(self.style.WARNING(f'⚠ Multiple default templates found ({default_templates.count()}). Only one should be marked as default.'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Default template is properly configured.'))
        
        # Check for active templates
        if active_count == 0:
            self.stdout.write(self.style.ERROR('✗ No active templates available. Users cannot select templates.'))
        elif active_count < 3:
            self.stdout.write(self.style.WARNING(f'⚠ Only {active_count} active template(s). Consider adding more variety.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ {active_count} active templates available.'))
        
        self.stdout.write('')
