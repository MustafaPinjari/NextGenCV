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
        
        Args:
            template (ResumeTemplate): Template to preview
            
        Returns:
            str: Rendered HTML with sample data
        """
        # Sample data for preview
        sample_data = {
            'resume': {
                'title': 'Sample Resume'
            },
            'personal_info': {
                'full_name': 'John Doe',
                'email': 'john.doe@email.com',
                'phone': '(555) 123-4567',
                'location': 'San Francisco, CA',
                'linkedin': 'linkedin.com/in/johndoe',
                'github': 'github.com/johndoe'
            },
            'experiences': [
                {
                    'role': 'Senior Software Engineer',
                    'company': 'Tech Company Inc.',
                    'start_date': '2021-01-01',
                    'end_date': None,
                    'description': 'Led development of scalable web applications using Python and Django. Implemented CI/CD pipelines and improved system performance by 40%. Mentored junior developers and conducted code reviews.'
                },
                {
                    'role': 'Software Engineer',
                    'company': 'Startup Solutions',
                    'start_date': '2019-06-01',
                    'end_date': '2020-12-31',
                    'description': 'Developed RESTful APIs and microservices. Collaborated with cross-functional teams to deliver features on time. Reduced API response time by 30% through optimization.'
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science',
                    'field': 'Computer Science',
                    'institution': 'University of California',
                    'start_year': 2015,
                    'end_year': 2019
                }
            ],
            'skills': [
                {'name': 'Python', 'category': 'Programming Languages'},
                {'name': 'JavaScript', 'category': 'Programming Languages'},
                {'name': 'Django', 'category': 'Frameworks'},
                {'name': 'React', 'category': 'Frameworks'},
                {'name': 'PostgreSQL', 'category': 'Databases'},
                {'name': 'Docker', 'category': 'Tools'},
                {'name': 'Git', 'category': 'Tools'}
            ],
            'projects': [
                {
                    'name': 'E-commerce Platform',
                    'url': 'github.com/johndoe/ecommerce',
                    'description': 'Built a full-stack e-commerce platform with payment integration and inventory management.',
                    'technologies': 'Django, React, PostgreSQL, Stripe API'
                },
                {
                    'name': 'Task Management App',
                    'url': 'github.com/johndoe/taskapp',
                    'description': 'Developed a collaborative task management application with real-time updates.',
                    'technologies': 'Node.js, Socket.io, MongoDB'
                }
            ]
        }
        
        # Render the template with sample data
        try:
            html = render_to_string(template.template_file, sample_data)
            return html
        except Exception as e:
            # Return error message if template rendering fails
            return f"<p>Error rendering template: {str(e)}</p>"
    
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
