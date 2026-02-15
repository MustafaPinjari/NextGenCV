"""
Plain Text Export Service for generating ATS-optimized text resumes.
"""
from django.shortcuts import get_object_or_404
from ..models import Resume
import logging

logger = logging.getLogger(__name__)


class TextExportService:
    """
    Service class for generating plain text exports of resumes.
    Optimized for ATS parsing with clean, structured formatting.
    """

    @staticmethod
    def generate_text(resume_id, version_id=None):
        """
        Generate plain text from resume and return as string.
        
        Args:
            resume_id: ID of the resume to export
            version_id: Optional ID of specific version to export
        
        Returns:
            tuple: (str, Resume) - Plain text content and Resume object
        
        Raises:
            Resume.DoesNotExist: If resume with given ID doesn't exist
        """
        try:
            # Load resume with all related sections
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
                from ..models import ResumeVersion
                from .snapshot_utils import create_resume_from_snapshot
                version = get_object_or_404(ResumeVersion, id=version_id, resume=resume)
                resume = create_resume_from_snapshot(resume, version.snapshot_data)
            
            # Build text content
            text_parts = []
            
            # Add personal information
            personal_text = TextExportService._format_personal_info(resume)
            if personal_text:
                text_parts.append(personal_text)
            
            # Add experience section
            if resume.experiences.exists():
                experience_text = TextExportService._format_experiences(resume)
                text_parts.append(experience_text)
            
            # Add education section
            if resume.education.exists():
                education_text = TextExportService._format_education(resume)
                text_parts.append(education_text)
            
            # Add skills section
            if resume.skills.exists():
                skills_text = TextExportService._format_skills(resume)
                text_parts.append(skills_text)
            
            # Add projects section
            if resume.projects.exists():
                projects_text = TextExportService._format_projects(resume)
                text_parts.append(projects_text)
            
            # Join all sections with double line breaks
            text_content = '\n\n'.join(text_parts)
            
            logger.info(f'Successfully generated plain text for resume {resume_id}' +
                       (f' version {version_id}' if version_id else ''))
            return text_content, resume
            
        except Exception as e:
            logger.error(f'Failed to generate plain text for resume {resume_id}: {str(e)}', exc_info=True)
            raise

    @staticmethod
    def _format_personal_info(resume):
        """Format personal information section."""
        personal_info = getattr(resume, 'personal_info', None)
        if not personal_info:
            return ''
        
        lines = []
        
        # Name (uppercase for emphasis)
        lines.append(personal_info.full_name.upper())
        lines.append('=' * len(personal_info.full_name))
        lines.append('')
        
        # Contact information
        contact_parts = []
        if personal_info.phone:
            contact_parts.append(f"Phone: {personal_info.phone}")
        if personal_info.email:
            contact_parts.append(f"Email: {personal_info.email}")
        if personal_info.location:
            contact_parts.append(f"Location: {personal_info.location}")
        
        if contact_parts:
            lines.extend(contact_parts)
            lines.append('')
        
        # Links
        if personal_info.linkedin:
            lines.append(f"LinkedIn: {personal_info.linkedin}")
        if personal_info.github:
            lines.append(f"GitHub: {personal_info.github}")
        
        return '\n'.join(lines)

    @staticmethod
    def _format_experiences(resume):
        """Format work experience section."""
        lines = []
        lines.append('WORK EXPERIENCE')
        lines.append('=' * 15)
        lines.append('')
        
        for experience in resume.experiences.all():
            # Job title and company
            lines.append(f"{experience.role}")
            lines.append(f"{experience.company}")
            
            # Dates
            start_date = experience.start_date.strftime('%B %Y')
            end_date = experience.end_date.strftime('%B %Y') if experience.end_date else 'Present'
            lines.append(f"{start_date} - {end_date}")
            lines.append('')
            
            # Description (bullet points)
            if experience.description:
                bullets = [line.strip() for line in experience.description.split('\n') if line.strip()]
                for bullet in bullets:
                    # Remove existing bullet markers and add consistent formatting
                    bullet_text = bullet.lstrip('•-* ')
                    lines.append(f"- {bullet_text}")
                lines.append('')
        
        return '\n'.join(lines)

    @staticmethod
    def _format_education(resume):
        """Format education section."""
        lines = []
        lines.append('EDUCATION')
        lines.append('=' * 9)
        lines.append('')
        
        for edu in resume.education.all():
            # Degree and field
            lines.append(f"{edu.degree} in {edu.field}")
            
            # Institution
            lines.append(f"{edu.institution}")
            
            # Years
            end_year = edu.end_year if edu.end_year else 'Present'
            lines.append(f"{edu.start_year} - {end_year}")
            lines.append('')
        
        return '\n'.join(lines)

    @staticmethod
    def _format_skills(resume):
        """Format skills section."""
        lines = []
        lines.append('SKILLS')
        lines.append('=' * 6)
        lines.append('')
        
        # Group skills by category
        skills_by_category = {}
        for skill in resume.skills.all():
            category = skill.category or 'General'
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill.name)
        
        # Add each category
        for category, skill_names in skills_by_category.items():
            lines.append(f"{category}:")
            lines.append(', '.join(skill_names))
            lines.append('')
        
        return '\n'.join(lines)

    @staticmethod
    def _format_projects(resume):
        """Format projects section."""
        lines = []
        lines.append('PROJECTS')
        lines.append('=' * 8)
        lines.append('')
        
        for project in resume.projects.all():
            # Project name
            lines.append(project.name)
            
            # URL if available
            if project.url:
                lines.append(f"URL: {project.url}")
            
            # Description
            if project.description:
                lines.append(project.description)
            
            # Technologies
            if project.technologies:
                lines.append(f"Technologies: {project.technologies}")
            
            lines.append('')
        
        return '\n'.join(lines)
