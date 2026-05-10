"""
Business logic services for resume management.
"""
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, Project
from apps.resumes.utils.query_optimization import (
    get_resume_with_relations,
    get_user_resumes_optimized,
    bulk_prefetch_resume_relations
)


class ResumeService:
    """
    Service class containing business logic for resume operations.
    Handles CRUD operations and ensures data integrity.
    
    Uses query optimization utilities to reduce database hits.
    Requirements: 18.2
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
                template=data.get('template', 'professional'),
                summary=data.get('summary', ''),
                is_draft=data.get('is_draft', True)
            )
            
            # Create personal info if provided
            if 'personal_info' in data:
                pi = data['personal_info']
                PersonalInfo.objects.create(
                    resume=resume,
                    full_name=pi.get('full_name') or '',
                    phone=pi.get('phone') or '',
                    email=pi.get('email') or '',
                    linkedin=pi.get('linkedin') or None,
                    github=pi.get('github') or None,
                    location=pi.get('location') or '',
                )
            
            # Create experiences if provided
            if 'experiences' in data:
                for idx, exp_data in enumerate(data['experiences']):
                    Experience.objects.create(
                        resume=resume,
                        order=idx,
                        company=exp_data.get('company', 'Unknown Company'),
                        role=exp_data.get('role', 'Unknown Role'),
                        start_date=exp_data.get('start_date'),
                        end_date=exp_data.get('end_date'),
                        description=exp_data.get('description', ''),
                        achievements=exp_data.get('achievements', ''),
                        location=exp_data.get('location', ''),
                    )
            
            # Create education entries if provided
            if 'education' in data:
                for idx, edu_data in enumerate(data['education']):
                    Education.objects.create(
                        resume=resume,
                        order=idx,
                        institution=edu_data.get('institution', ''),
                        degree=edu_data.get('degree', ''),
                        field=edu_data.get('field', '') or '',
                        start_year=edu_data.get('start_year') or 2000,
                        end_year=edu_data.get('end_year'),
                    )

            # Create skills if provided
            if 'skills' in data:
                for skill_data in data['skills']:
                    name = skill_data.get('name', '').strip()
                    if not name:
                        continue
                    Skill.objects.create(
                        resume=resume,
                        name=name,
                        category=skill_data.get('category') or 'General',
                    )

            # Create projects if provided
            if 'projects' in data:
                for idx, proj_data in enumerate(data['projects']):
                    Project.objects.create(
                        resume=resume,
                        order=idx,
                        name=proj_data.get('name', ''),
                        description=proj_data.get('description', ''),
                        technologies=proj_data.get('technologies', ''),
                        url=proj_data.get('url', ''),
                    )
            
            return resume

    @staticmethod
    def get_user_resumes(user):
        """
        Retrieve all resumes for a user, ordered by updated_at descending.
        
        Uses optimized query with select_related to reduce database hits.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: Resumes belonging to the user with personal_info prefetched
            
        Requirements: 18.2
        """
        return get_user_resumes_optimized(user)

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
                resume.experiences.all().delete()
                for idx, exp_data in enumerate(data['experiences']):
                    Experience.objects.create(
                        resume=resume,
                        order=idx,
                        company=exp_data.get('company', 'Unknown Company'),
                        role=exp_data.get('role', 'Unknown Role'),
                        start_date=exp_data.get('start_date'),
                        end_date=exp_data.get('end_date'),
                        description=exp_data.get('description', ''),
                        achievements=exp_data.get('achievements', ''),
                        location=exp_data.get('location', ''),
                    )

            # Update education if provided
            if 'education' in data:
                resume.education.all().delete()
                for idx, edu_data in enumerate(data['education']):
                    Education.objects.create(
                        resume=resume,
                        order=idx,
                        institution=edu_data.get('institution', ''),
                        degree=edu_data.get('degree', ''),
                        field=edu_data.get('field', '') or '',
                        start_year=edu_data.get('start_year') or 2000,
                        end_year=edu_data.get('end_year'),
                    )

            # Update skills if provided
            if 'skills' in data:
                resume.skills.all().delete()
                for skill_data in data['skills']:
                    name = skill_data.get('name', '').strip()
                    if not name:
                        continue
                    Skill.objects.create(
                        resume=resume,
                        name=name,
                        category=skill_data.get('category') or 'General',
                    )

            # Update projects if provided
            if 'projects' in data:
                resume.projects.all().delete()
                for idx, proj_data in enumerate(data['projects']):
                    Project.objects.create(
                        resume=resume,
                        order=idx,
                        name=proj_data.get('name', ''),
                        description=proj_data.get('description', ''),
                        technologies=proj_data.get('technologies', ''),
                        url=proj_data.get('url', ''),
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
        
        Uses optimized query with prefetch_related to load all relations in one query.
        
        Args:
            resume_id: ID of the resume to duplicate
        
        Returns:
            Resume: The newly created duplicate resume
            
        Requirements: 18.2
        """
        with transaction.atomic():
            # Get the original resume with all relations prefetched
            original = get_resume_with_relations(resume_id)
            
            # Create new resume with same data (Requirements: 25.1, 25.2, 25.3)
            duplicate = Resume.objects.create(
                user=original.user,
                title=f"{original.title} (Copy)",
                template=original.template,
                color_scheme=original.color_scheme,  # Copy customization
                font_family=original.font_family      # Copy customization
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

