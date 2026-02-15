"""
Query optimization utilities for efficient database access.

This module provides helper functions to optimize Django ORM queries
using select_related and prefetch_related to reduce database hits.

Requirements: 18.2
"""
from django.db.models import Prefetch
from apps.resumes.models import (
    Resume, Experience, Education, Skill, Project,
    ResumeVersion, UploadedResume, ResumeAnalysis, OptimizationHistory
)


def get_resume_with_relations(resume_id):
    """
    Get a resume with all related data using optimized queries.
    
    Uses select_related for one-to-one relationships (personal_info)
    and prefetch_related for one-to-many relationships (experiences, education, etc.)
    
    Args:
        resume_id: ID of the resume to fetch
        
    Returns:
        Resume object with all relations prefetched
        
    Requirements: 18.2
    """
    return Resume.objects.select_related(
        'personal_info'
    ).prefetch_related(
        'experiences',
        'education',
        'skills',
        'projects'
    ).get(id=resume_id)


def get_user_resumes_optimized(user):
    """
    Get all resumes for a user with optimized queries.
    
    Prefetches personal_info for each resume to avoid N+1 queries
    when displaying resume lists.
    
    Args:
        user: User object
        
    Returns:
        QuerySet of Resume objects with personal_info prefetched
        
    Requirements: 18.2
    """
    return Resume.objects.filter(
        user=user
    ).select_related(
        'personal_info'
    ).order_by('-updated_at')


def get_resume_with_versions(resume_id):
    """
    Get a resume with all versions using optimized queries.
    
    Args:
        resume_id: ID of the resume to fetch
        
    Returns:
        Resume object with versions prefetched
        
    Requirements: 18.2
    """
    return Resume.objects.prefetch_related(
        Prefetch(
            'versions',
            queryset=ResumeVersion.objects.order_by('-version_number')
        )
    ).get(id=resume_id)


def get_resume_with_analyses(resume_id):
    """
    Get a resume with all analyses using optimized queries.
    
    Args:
        resume_id: ID of the resume to fetch
        
    Returns:
        Resume object with analyses prefetched
        
    Requirements: 18.2
    """
    return Resume.objects.prefetch_related(
        Prefetch(
            'analyses',
            queryset=ResumeAnalysis.objects.order_by('-analysis_timestamp')
        )
    ).get(id=resume_id)


def get_resume_with_optimizations(resume_id):
    """
    Get a resume with optimization history using optimized queries.
    
    Args:
        resume_id: ID of the resume to fetch
        
    Returns:
        Resume object with optimizations prefetched
        
    Requirements: 18.2
    """
    return Resume.objects.prefetch_related(
        Prefetch(
            'optimizations',
            queryset=OptimizationHistory.objects.select_related(
                'original_version',
                'optimized_version'
            ).order_by('-optimization_timestamp')
        )
    ).get(id=resume_id)


def get_user_uploaded_resumes_optimized(user):
    """
    Get all uploaded resumes for a user with optimized queries.
    
    Args:
        user: User object
        
    Returns:
        QuerySet of UploadedResume objects
        
    Requirements: 18.2
    """
    return UploadedResume.objects.filter(
        user=user
    ).order_by('-uploaded_at')


def get_user_analyses_optimized(user):
    """
    Get all resume analyses for a user with optimized queries.
    
    Includes resume data to avoid additional queries when displaying analysis lists.
    
    Args:
        user: User object
        
    Returns:
        QuerySet of ResumeAnalysis objects with resume prefetched
        
    Requirements: 18.2
    """
    return ResumeAnalysis.objects.filter(
        resume__user=user
    ).select_related(
        'resume'
    ).order_by('-analysis_timestamp')


def get_user_optimizations_optimized(user):
    """
    Get all optimization history for a user with optimized queries.
    
    Includes resume and version data to avoid additional queries.
    
    Args:
        user: User object
        
    Returns:
        QuerySet of OptimizationHistory objects with related data prefetched
        
    Requirements: 18.2
    """
    return OptimizationHistory.objects.filter(
        resume__user=user
    ).select_related(
        'resume',
        'original_version',
        'optimized_version'
    ).order_by('-optimization_timestamp')


def bulk_prefetch_resume_relations(resume_queryset):
    """
    Add prefetch_related to a queryset of resumes for bulk operations.
    
    Useful for batch operations where multiple resumes need their relations loaded.
    
    Args:
        resume_queryset: QuerySet of Resume objects
        
    Returns:
        QuerySet with prefetch_related applied
        
    Requirements: 18.2
    """
    return resume_queryset.select_related(
        'personal_info'
    ).prefetch_related(
        'experiences',
        'education',
        'skills',
        'projects'
    )
