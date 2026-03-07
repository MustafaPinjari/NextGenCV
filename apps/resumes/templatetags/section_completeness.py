"""
Template tags for section completeness checking.
"""
from django import template

register = template.Library()


@register.inclusion_tag('resumes/partials/section_completeness_banner.html')
def section_completeness_banner(resume):
    """
    Display a warning banner for missing required sections.
    
    Args:
        resume: Resume instance
        
    Returns:
        Context dict with missing sections and recommendations
    """
    # Check required sections
    missing_sections = []
    
    # Check Personal Info
    try:
        pi = resume.personal_info
        if not pi or not pi.full_name or not pi.email:
            missing_sections.append({
                'name': 'Personal Information',
                'importance': 'Required for ATS systems to identify and contact you',
                'icon': 'person-circle',
                'url_name': 'resume_update',  # Goes to main form
            })
    except:
        missing_sections.append({
            'name': 'Personal Information',
            'importance': 'Required for ATS systems to identify and contact you',
            'icon': 'person-circle',
            'url_name': 'resume_update',
        })
    
    # Check Experience
    if not resume.experiences.exists():
        missing_sections.append({
            'name': 'Work Experience',
            'importance': 'Critical for demonstrating your professional background',
            'icon': 'briefcase',
            'url_name': 'experience_add',
        })
    
    # Check Education
    if not resume.education.exists():
        missing_sections.append({
            'name': 'Education',
            'importance': 'Required by most ATS systems and employers',
            'icon': 'mortarboard',
            'url_name': 'education_add',
        })
    
    # Check Skills
    if not resume.skills.exists():
        missing_sections.append({
            'name': 'Skills',
            'importance': 'Essential for keyword matching in ATS systems',
            'icon': 'star',
            'url_name': 'skill_add',
        })
    
    # Calculate completeness percentage
    total_required = 4
    completed = total_required - len(missing_sections)
    completeness_percentage = (completed / total_required) * 100
    
    # Optional section recommendations
    optional_recommendations = []
    
    if not resume.projects.exists():
        optional_recommendations.append({
            'name': 'Projects',
            'benefit': 'Showcase your practical experience and technical skills',
            'icon': 'folder',
            'url_name': 'project_add',
        })
    
    # Could add more optional sections here (Certifications, Publications, Awards)
    # For now, keeping it simple with just Projects
    
    return {
        'resume': resume,
        'missing_sections': missing_sections,
        'completeness_percentage': completeness_percentage,
        'optional_recommendations': optional_recommendations[:3],  # Limit to 3
        'show_banner': len(missing_sections) > 0,
    }


@register.simple_tag
def section_completeness_percentage(resume):
    """
    Calculate section completeness percentage.
    
    Args:
        resume: Resume instance
        
    Returns:
        Float percentage (0-100)
    """
    total_required = 4
    completed = 0
    
    # Check Personal Info
    try:
        pi = resume.personal_info
        if pi and pi.full_name and pi.email:
            completed += 1
    except:
        pass
    
    # Check Experience
    if resume.experiences.exists():
        completed += 1
    
    # Check Education
    if resume.education.exists():
        completed += 1
    
    # Check Skills
    if resume.skills.exists():
        completed += 1
    
    return (completed / total_required) * 100
