"""
Template Service
Handles template CRUD operations and preview generation.
"""
from django.template.loader import render_to_string
from apps.templates_mgmt.models import ResumeTemplate
from apps.resumes.models import Resume


class TemplateService:
    """Service for managing resume templates"""
    
    @staticmethod
    def get_all_templates():
        """
        Get all active templates ordered by default status and name.
        
        Returns:
            QuerySet: Active ResumeTemplate objects
        """
        return ResumeTemplate.objects.filter(is_active=True).order_by('-is_default', 'name')
    
    @staticmethod
    def get_template_by_id(template_id):
        """
        Get a specific template by ID.
        
        Args:
            template_id (int): Template ID
            
        Returns:
            ResumeTemplate: Template object or None if not found
        """
        try:
            return ResumeTemplate.objects.get(id=template_id, is_active=True)
        except ResumeTemplate.DoesNotExist:
            return None
    
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
        from django.template import TemplateDoesNotExist
        
        logger = logging.getLogger(__name__)
        
        # Validate template file path
        if not template.template_file:
            logger.error(f"Template {template.id} has no template_file set")
            raise ValueError("Template file path is not configured")
        
        # Sample data for preview - convert dictionaries to mock objects with attributes
        sample_data = {
            'resume': type('obj', (object,), {
                'title': 'Sample Resume',
                'summary': 'Experienced professional with expertise in software development and a proven track record of delivering high-quality solutions. Passionate about creating efficient, scalable applications and mentoring team members.'
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
                    'description': 'Led development of scalable web applications using Python and Django. Implemented CI/CD pipelines and improved system performance by 40%. Mentored junior developers and conducted code reviews.'
                })(),
                type('obj', (object,), {
                    'role': 'Software Engineer',
                    'company': 'Startup Solutions',
                    'start_date': '2019-06-01',
                    'end_date': '2020-12-31',
                    'description': 'Developed RESTful APIs and microservices. Collaborated with cross-functional teams to deliver features on time. Reduced API response time by 30% through optimization.'
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
                type('obj', (object,), {'name': 'JavaScript', 'category': 'Programming Languages'})(),
                type('obj', (object,), {'name': 'Django', 'category': 'Frameworks'})(),
                type('obj', (object,), {'name': 'React', 'category': 'Frameworks'})(),
                type('obj', (object,), {'name': 'PostgreSQL', 'category': 'Databases'})(),
                type('obj', (object,), {'name': 'Docker', 'category': 'Tools'})(),
                type('obj', (object,), {'name': 'Git', 'category': 'Tools'})()
            ],
            'projects': [
                type('obj', (object,), {
                    'name': 'E-commerce Platform',
                    'url': 'github.com/johndoe/ecommerce',
                    'description': 'Built a full-stack e-commerce platform with payment integration and inventory management.',
                    'technologies': 'Django, React, PostgreSQL, Stripe API'
                })(),
                type('obj', (object,), {
                    'name': 'Task Management App',
                    'url': 'github.com/johndoe/taskapp',
                    'description': 'Developed a collaborative task management application with real-time updates.',
                    'technologies': 'Node.js, Socket.io, MongoDB'
                })()
            ]
        }
        
        # Render the template with sample data
        try:
            html = render_to_string(template.template_file, sample_data)
            logger.info(f"Successfully rendered preview for template {template.id} ({template.name})")
            return html
        except TemplateDoesNotExist as e:
            logger.error(f"Template file not found: {template.template_file}")
            raise ValueError(f"Template file '{template.template_file}' does not exist")
        except Exception as e:
            logger.error(f"Error rendering template {template.id}: {str(e)}", exc_info=True)
            raise ValueError(f"Template rendering error: {str(e)}")
    
    @staticmethod
    def increment_usage_count(template):
        """
        Increment the usage count for a template.
        
        Args:
            template (ResumeTemplate): Template to increment
        """
        template.usage_count += 1
        template.save(update_fields=['usage_count'])
    
    @staticmethod
    def get_default_template():
        """
        Get the default template.
        
        Returns:
            ResumeTemplate: Default template or first active template
        """
        default = ResumeTemplate.objects.filter(is_default=True, is_active=True).first()
        if not default:
            # If no default, return first active template
            default = ResumeTemplate.objects.filter(is_active=True).first()
        return default
