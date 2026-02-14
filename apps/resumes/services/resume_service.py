"""
Business logic services for resume management.
"""
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project


class ResumeService:
    """
    Service class containing business logic for resume operations.
    Handles CRUD operations and ensures data integrity.
    """

    @staticmethod
    def create_resume(user, data):
        """
        Create a new resume with all sections.
        
        Args:
            user: User object who owns the resume
            data: Dictionary containing resume data with structure:
                {
                    'title': str,
                    'template': str (optional, defaults to 'professional'),
                    'personal_info': dict (optional),
                    'experiences': list of dicts (optional),
                    'education': list of dicts (optional),
                    'skills': list of dicts (optional),
                    'projects': list of dicts (optional)
                }
        
        Returns:
            Resume: The created resume object
        """
        with transaction.atomic():
            # Create the resume
            resume = Resume.objects.create(
                user=user,
                title=data.get('title', 'Untitled Resume'),
                template=data.get('template', 'professional')
            )
            
            # Create personal info if provided
            if 'personal_info' in data:
                PersonalInfo.objects.create(
                    resume=resume,
                    **data['personal_info']
                )
            
            # Create experiences if provided
            if 'experiences' in data:
                for idx, exp_data in enumerate(data['experiences']):
                    Experience.objects.create(
                        resume=resume,
                        order=idx,
                        **exp_data
                    )
            
            # Create education entries if provided
            if 'education' in data:
                for idx, edu_data in enumerate(data['education']):
                    Education.objects.create(
                        resume=resume,
                        order=idx,
                        **edu_data
                    )
            
            # Create skills if provided
            if 'skills' in data:
                for skill_data in data['skills']:
                    Skill.objects.create(
                        resume=resume,
                        **skill_data
                    )
            
            # Create projects if provided
            if 'projects' in data:
                for idx, proj_data in enumerate(data['projects']):
                    Project.objects.create(
                        resume=resume,
                        order=idx,
                        **proj_data
                    )
            
            return resume

    @staticmethod
    def get_user_resumes(user):
        """
        Retrieve all resumes for a user, ordered by updated_at descending.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: Resumes belonging to the user
        """
        return Resume.objects.filter(user=user).order_by('-updated_at')

    @staticmethod
    def update_resume(resume_id, data):
        """
        Update an existing resume and its sections.
        
        Args:
            resume_id: ID of the resume to update
            data: Dictionary containing updated resume data
        
        Returns:
            Resume: The updated resume object
        """
        with transaction.atomic():
            resume = get_object_or_404(Resume, id=resume_id)
            
            # Update resume metadata
            if 'title' in data:
                resume.title = data['title']
            if 'template' in data:
                resume.template = data['template']
            resume.save()
            
            # Update personal info if provided
            if 'personal_info' in data:
                personal_info, created = PersonalInfo.objects.get_or_create(resume=resume)
                for key, value in data['personal_info'].items():
                    setattr(personal_info, key, value)
                personal_info.save()
            
            # Update experiences if provided
            if 'experiences' in data:
                # Delete existing experiences
                resume.experiences.all().delete()
                # Create new experiences
                for idx, exp_data in enumerate(data['experiences']):
                    Experience.objects.create(
                        resume=resume,
                        order=idx,
                        **exp_data
                    )
            
            # Update education if provided
            if 'education' in data:
                # Delete existing education
                resume.education.all().delete()
                # Create new education entries
                for idx, edu_data in enumerate(data['education']):
                    Education.objects.create(
                        resume=resume,
                        order=idx,
                        **edu_data
                    )
            
            # Update skills if provided
            if 'skills' in data:
                # Delete existing skills
                resume.skills.all().delete()
                # Create new skills
                for skill_data in data['skills']:
                    Skill.objects.create(
                        resume=resume,
                        **skill_data
                    )
            
            # Update projects if provided
            if 'projects' in data:
                # Delete existing projects
                resume.projects.all().delete()
                # Create new projects
                for idx, proj_data in enumerate(data['projects']):
                    Project.objects.create(
                        resume=resume,
                        order=idx,
                        **proj_data
                    )
            
            return resume

    @staticmethod
    def delete_resume(resume_id):
        """
        Delete a resume and all associated sections (cascade).
        
        Args:
            resume_id: ID of the resume to delete
        
        Returns:
            bool: True if deletion was successful
        """
        resume = get_object_or_404(Resume, id=resume_id)
        resume.delete()
        return True

    @staticmethod
    def duplicate_resume(resume_id):
        """
        Create a copy of an existing resume with all sections.
        
        Args:
            resume_id: ID of the resume to duplicate
        
        Returns:
            Resume: The newly created duplicate resume
        """
        with transaction.atomic():
            # Get the original resume
            original = get_object_or_404(
                Resume.objects.prefetch_related(
                    'personal_info',
                    'experiences',
                    'education',
                    'skills',
                    'projects'
                ),
                id=resume_id
            )
            
            # Create new resume with same data
            duplicate = Resume.objects.create(
                user=original.user,
                title=f"{original.title} (Copy)",
                template=original.template
            )
            
            # Duplicate personal info if exists
            if hasattr(original, 'personal_info'):
                personal_info = original.personal_info
                PersonalInfo.objects.create(
                    resume=duplicate,
                    full_name=personal_info.full_name,
                    phone=personal_info.phone,
                    email=personal_info.email,
                    linkedin=personal_info.linkedin,
                    github=personal_info.github,
                    location=personal_info.location
                )
            
            # Duplicate experiences
            for exp in original.experiences.all():
                Experience.objects.create(
                    resume=duplicate,
                    company=exp.company,
                    role=exp.role,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    description=exp.description,
                    order=exp.order
                )
            
            # Duplicate education
            for edu in original.education.all():
                Education.objects.create(
                    resume=duplicate,
                    institution=edu.institution,
                    degree=edu.degree,
                    field=edu.field,
                    start_year=edu.start_year,
                    end_year=edu.end_year,
                    order=edu.order
                )
            
            # Duplicate skills
            for skill in original.skills.all():
                Skill.objects.create(
                    resume=duplicate,
                    name=skill.name,
                    category=skill.category
                )
            
            # Duplicate projects
            for proj in original.projects.all():
                Project.objects.create(
                    resume=duplicate,
                    name=proj.name,
                    description=proj.description,
                    technologies=proj.technologies,
                    url=proj.url,
                    order=proj.order
                )
            
            return duplicate

