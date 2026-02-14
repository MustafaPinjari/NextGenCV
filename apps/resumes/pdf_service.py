"""
PDF Export Service for generating ATS-compatible PDF resumes.
"""
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from .models import Resume
import logging

logger = logging.getLogger(__name__)


class PDFExportService:
    """
    Service class for generating PDF exports of resumes.
    Uses WeasyPrint to convert HTML templates to PDF format.
    """

    @staticmethod
    def render_resume_html(resume):
        """
        Render resume to HTML string using Django template.
        Uses PDF-specific template with print-friendly CSS.
        
        Args:
            resume: Resume object to render
        
        Returns:
            str: HTML string of the rendered resume
        """
        # Prepare context with all resume sections
        context = {
            'resume': resume,
            'personal_info': getattr(resume, 'personal_info', None),
            'experiences': resume.experiences.all(),
            'education': resume.education.all(),
            'skills': resume.skills.all(),
            'projects': resume.projects.all()
        }
        
        # Use PDF-specific template with print-friendly CSS
        template_name = f'resumes/{resume.template}_pdf.html'
        html_string = render_to_string(template_name, context)
        
        return html_string

    @staticmethod
    def generate_pdf(resume_id):
        """
        Generate PDF from resume and return as bytes.
        
        Args:
            resume_id: ID of the resume to export
        
        Returns:
            bytes: PDF file content as bytes
        
        Raises:
            Resume.DoesNotExist: If resume with given ID doesn't exist
        """
        try:
            # Load resume with all related sections using select_related and prefetch_related
            resume = get_object_or_404(
                Resume.objects.prefetch_related(
                    'personal_info',
                    'experiences',
                    'education',
                    'skills',
                    'projects'
                ),
                id=resume_id
            )
            
            # Render HTML
            html_string = PDFExportService.render_resume_html(resume)
            
            # Generate PDF using WeasyPrint
            # Note: WeasyPrint 60.1 has simplified API
            pdf_bytes = HTML(string=html_string).write_pdf()
            
            logger.info(f'Successfully generated PDF for resume {resume_id}')
            return pdf_bytes, resume
            
        except Exception as e:
            logger.error(f'Failed to generate PDF for resume {resume_id}: {str(e)}', exc_info=True)
            raise
