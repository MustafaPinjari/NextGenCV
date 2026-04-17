"""
PDF Export Service for generating ATS-compatible PDF resumes.
"""
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from .models import Resume
import logging

logger = logging.getLogger(__name__)


class PDFExportService:
    """
    Service class for generating PDF exports of resumes.
    Uses WeasyPrint to convert HTML templates to PDF format.
    Falls back to plain HTML download if WeasyPrint is unavailable (e.g. missing GTK on Windows).
    """

    @staticmethod
    def render_resume_html(resume):
        """
        Render resume to HTML string using Django template.
        Uses PDF-specific template with print-friendly CSS.
        Applies custom colors and fonts from resume settings.
        
        Args:
            resume: Resume object to render
        
        Returns:
            str: HTML string of the rendered resume
        """
        from apps.resumes.services.template_customization_service import TemplateCustomizationService
        
        # Get customization settings
        color_scheme = TemplateCustomizationService.get_color_scheme(resume.color_scheme)
        font_info = TemplateCustomizationService.get_font_family(resume.font_family)
        
        # Prepare context with all resume sections and customization
        context = {
            'resume': resume,
            'personal_info': getattr(resume, 'personal_info', None),
            'experiences': resume.experiences.all(),
            'education': resume.education.all(),
            'skills': resume.skills.all(),
            'projects': resume.projects.all(),
            # Add customization data
            'color_scheme': color_scheme,
            'font_info': font_info,
        }
        
        # Use PDF-specific template with print-friendly CSS
        template_name = f'resumes/{resume.template}_pdf.html'
        html_string = render_to_string(template_name, context)
        
        return html_string

    @staticmethod
    def generate_pdf(resume_id, version_id=None):
        """
        Generate PDF from resume and return as bytes.
        
        Args:
            resume_id: ID of the resume to export
            version_id: Optional ID of specific version to export
        
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
            
            # If version_id is provided, create a temporary resume from version snapshot
            if version_id:
                from .models import ResumeVersion
                from .services.snapshot_utils import create_resume_from_snapshot
                version = get_object_or_404(ResumeVersion, id=version_id, resume=resume)
                resume = create_resume_from_snapshot(resume, version.snapshot_data)
            
            # Render HTML
            html_string = PDFExportService.render_resume_html(resume)
            
            # Generate PDF using WeasyPrint (requires GTK/Pango on Windows)
            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html_string).write_pdf()
            except OSError as e:
                # WeasyPrint missing system libraries (common on Windows without GTK)
                logger.warning(f'WeasyPrint unavailable ({e}), returning HTML as fallback')
                # Return HTML bytes with a flag so the view can serve as HTML download
                pdf_bytes = html_string.encode('utf-8')
                resume._pdf_fallback = True
            
            logger.info(f'Successfully generated PDF for resume {resume_id}' + 
                       (f' version {version_id}' if version_id else ''))
            return pdf_bytes, resume
            
        except Exception as e:
            logger.error(f'Failed to generate PDF for resume {resume_id}: {str(e)}', exc_info=True)
            raise
