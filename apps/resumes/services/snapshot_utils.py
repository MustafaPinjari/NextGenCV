"""
Utility functions for working with resume version snapshots.
"""
from datetime import date


class MockQuerySet:
    """Mock queryset for temporary resume objects."""
    def __init__(self, items):
        self._items = items
    
    def all(self):
        return self._items
    
    def exists(self):
        return len(self._items) > 0


def create_resume_from_snapshot(resume, snapshot_data):
    """
    Create a temporary resume object from version snapshot data.
    Uses simple objects instead of Django models to avoid database constraints.
    
    Args:
        resume: Original resume object
        snapshot_data: Version snapshot data
        
    Returns:
        Object: Temporary resume object with snapshot data
    """
    # Create a simple object to hold resume data
    class TempResume:
        pass
    
    temp_resume = TempResume()
    temp_resume.id = resume.id
    temp_resume.user = resume.user
    temp_resume.title = snapshot_data.get('title', resume.title)
    temp_resume.template = snapshot_data.get('template', resume.template)
    temp_resume.created_at = resume.created_at
    temp_resume.updated_at = resume.updated_at
    
    # Create temporary personal info
    if 'personal_info' in snapshot_data:
        pi_data = snapshot_data['personal_info']
        class TempPersonalInfo:
            pass
        temp_personal_info = TempPersonalInfo()
        temp_personal_info.full_name = pi_data.get('full_name', '')
        temp_personal_info.phone = pi_data.get('phone', '')
        temp_personal_info.email = pi_data.get('email', '')
        temp_personal_info.linkedin = pi_data.get('linkedin', '')
        temp_personal_info.github = pi_data.get('github', '')
        temp_personal_info.location = pi_data.get('location', '')
        temp_resume.personal_info = temp_personal_info
    
    # Create temporary experiences list
    temp_experiences = []
    for exp_data in snapshot_data.get('experiences', []):
        class TempExperience:
            pass
        exp = TempExperience()
        exp.company = exp_data.get('company', '')
        exp.role = exp_data.get('role', '')
        exp.start_date = date.fromisoformat(exp_data['start_date']) if exp_data.get('start_date') else date.today()
        exp.end_date = date.fromisoformat(exp_data['end_date']) if exp_data.get('end_date') else None
        exp.description = exp_data.get('description', '')
        exp.order = exp_data.get('order', 0)
        temp_experiences.append(exp)
    
    temp_resume.experiences = MockQuerySet(temp_experiences)
    
    # Create temporary education list
    temp_education = []
    for edu_data in snapshot_data.get('education', []):
        class TempEducation:
            pass
        edu = TempEducation()
        edu.institution = edu_data.get('institution', '')
        edu.degree = edu_data.get('degree', '')
        edu.field = edu_data.get('field', '')
        edu.start_year = edu_data.get('start_year', 2020)
        edu.end_year = edu_data.get('end_year')
        edu.order = edu_data.get('order', 0)
        temp_education.append(edu)
    
    temp_resume.education = MockQuerySet(temp_education)
    
    # Create temporary skills list
    temp_skills = []
    for skill_data in snapshot_data.get('skills', []):
        class TempSkill:
            pass
        skill = TempSkill()
        skill.name = skill_data.get('name', '')
        skill.category = skill_data.get('category', '')
        temp_skills.append(skill)
    
    temp_resume.skills = MockQuerySet(temp_skills)
    
    # Create temporary projects list
    temp_projects = []
    for proj_data in snapshot_data.get('projects', []):
        class TempProject:
            pass
        proj = TempProject()
        proj.name = proj_data.get('name', '')
        proj.description = proj_data.get('description', '')
        proj.technologies = proj_data.get('technologies', '')
        proj.url = proj_data.get('url', '')
        proj.order = proj_data.get('order', 0)
        temp_projects.append(proj)
    
    temp_resume.projects = MockQuerySet(temp_projects)
    
    return temp_resume
