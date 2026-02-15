"""
Authorization utilities for data isolation and access control.

This module provides:
- Ownership verification helpers
- Authorization decorators
- Query filtering utilities

All views should use these utilities to ensure proper data isolation.
"""

import logging
from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from ..models import Resume, UploadedResume, ResumeVersion, OptimizationHistory, ResumeAnalysis

logger = logging.getLogger(__name__)


def check_resume_ownership(user, resume_id):
    """
    Verify that a resume belongs to the specified user.
    
    Args:
        user: Django User object
        resume_id: Resume ID to check
        
    Returns:
        Resume: The resume object if authorized
        
    Raises:
        Http404: If resume doesn't exist
        PermissionDenied: If user doesn't own the resume
        
    Requirements: 16.1, 16.2
    """
    resume = get_object_or_404(Resume, id=resume_id)
    
    if resume.user != user:
        logger.warning(
            f'Authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access resume {resume_id} owned by {resume.user.username} (ID: {resume.user.id})'
        )
        raise PermissionDenied("You do not have permission to access this resume.")
    
    return resume


def check_uploaded_resume_ownership(user, upload_id):
    """
    Verify that an uploaded resume belongs to the specified user.
    
    Args:
        user: Django User object
        upload_id: UploadedResume ID to check
        
    Returns:
        UploadedResume: The uploaded resume object if authorized
        
    Raises:
        Http404: If uploaded resume doesn't exist
        PermissionDenied: If user doesn't own the uploaded resume
        
    Requirements: 16.1, 16.2
    """
    uploaded_resume = get_object_or_404(UploadedResume, id=upload_id)
    
    if uploaded_resume.user != user:
        logger.warning(
            f'Authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access upload {upload_id} owned by {uploaded_resume.user.username} (ID: {uploaded_resume.user.id})'
        )
        raise PermissionDenied("You do not have permission to access this uploaded file.")
    
    return uploaded_resume


def check_version_ownership(user, version_id):
    """
    Verify that a resume version belongs to the specified user.
    
    Args:
        user: Django User object
        version_id: ResumeVersion ID to check
        
    Returns:
        ResumeVersion: The version object if authorized
        
    Raises:
        Http404: If version doesn't exist
        PermissionDenied: If user doesn't own the version
        
    Requirements: 16.1, 16.4
    """
    version = get_object_or_404(ResumeVersion, id=version_id)
    
    if version.resume.user != user:
        logger.warning(
            f'Authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access version {version_id} owned by {version.resume.user.username} (ID: {version.resume.user.id})'
        )
        raise PermissionDenied("You do not have permission to access this version.")
    
    return version


def check_analysis_ownership(user, analysis_id):
    """
    Verify that a resume analysis belongs to the specified user.
    
    Args:
        user: Django User object
        analysis_id: ResumeAnalysis ID to check
        
    Returns:
        ResumeAnalysis: The analysis object if authorized
        
    Raises:
        Http404: If analysis doesn't exist
        PermissionDenied: If user doesn't own the analysis
        
    Requirements: 16.1, 16.3
    """
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id)
    
    if analysis.resume.user != user:
        logger.warning(
            f'Authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access analysis {analysis_id} owned by {analysis.resume.user.username} (ID: {analysis.resume.user.id})'
        )
        raise PermissionDenied("You do not have permission to access this analysis.")
    
    return analysis


def check_optimization_ownership(user, optimization_id):
    """
    Verify that an optimization history belongs to the specified user.
    
    Args:
        user: Django User object
        optimization_id: OptimizationHistory ID to check
        
    Returns:
        OptimizationHistory: The optimization object if authorized
        
    Raises:
        Http404: If optimization doesn't exist
        PermissionDenied: If user doesn't own the optimization
        
    Requirements: 16.1, 16.5
    """
    optimization = get_object_or_404(OptimizationHistory, id=optimization_id)
    
    if optimization.resume.user != user:
        logger.warning(
            f'Authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access optimization {optimization_id} owned by {optimization.resume.user.username} (ID: {optimization.resume.user.id})'
        )
        raise PermissionDenied("You do not have permission to access this optimization.")
    
    return optimization


def require_resume_ownership(view_func):
    """
    Decorator to verify resume ownership before executing view.
    
    The view must accept 'pk' parameter for resume ID.
    The decorated view will receive the resume object as 'resume' parameter.
    
    Usage:
        @login_required
        @require_resume_ownership
        def my_view(request, pk, resume):
            # resume is guaranteed to belong to request.user
            ...
    
    Requirements: 16.1, 16.2
    """
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        resume = check_resume_ownership(request.user, pk)
        return view_func(request, pk, resume=resume, *args, **kwargs)
    return wrapper


def require_upload_ownership(view_func):
    """
    Decorator to verify uploaded resume ownership before executing view.
    
    The view must accept 'upload_id' parameter.
    The decorated view will receive the uploaded resume object as 'uploaded_resume' parameter.
    
    Usage:
        @login_required
        @require_upload_ownership
        def my_view(request, upload_id, uploaded_resume):
            # uploaded_resume is guaranteed to belong to request.user
            ...
    
    Requirements: 16.1, 16.2
    """
    @wraps(view_func)
    def wrapper(request, upload_id, *args, **kwargs):
        uploaded_resume = check_uploaded_resume_ownership(request.user, upload_id)
        return view_func(request, upload_id, uploaded_resume=uploaded_resume, *args, **kwargs)
    return wrapper


# Query filtering utilities

def get_user_resumes(user):
    """
    Get all resumes for a user with proper filtering.
    
    Args:
        user: Django User object
        
    Returns:
        QuerySet: Filtered resumes
        
    Requirements: 16.2
    """
    return Resume.objects.filter(user=user)


def get_user_uploaded_resumes(user):
    """
    Get all uploaded resumes for a user with proper filtering.
    
    Args:
        user: Django User object
        
    Returns:
        QuerySet: Filtered uploaded resumes
        
    Requirements: 16.2
    """
    return UploadedResume.objects.filter(user=user)


def get_user_analyses(user):
    """
    Get all resume analyses for a user with proper filtering.
    
    Args:
        user: Django User object
        
    Returns:
        QuerySet: Filtered analyses
        
    Requirements: 16.3
    """
    return ResumeAnalysis.objects.filter(resume__user=user)


def get_user_versions(user):
    """
    Get all resume versions for a user with proper filtering.
    
    Args:
        user: Django User object
        
    Returns:
        QuerySet: Filtered versions
        
    Requirements: 16.4
    """
    return ResumeVersion.objects.filter(resume__user=user)


def get_user_optimizations(user):
    """
    Get all optimization histories for a user with proper filtering.
    
    Args:
        user: Django User object
        
    Returns:
        QuerySet: Filtered optimizations
        
    Requirements: 16.5
    """
    return OptimizationHistory.objects.filter(resume__user=user)


# Batch operation utilities

def verify_resume_ids_ownership(user, resume_ids):
    """
    Verify that all resume IDs belong to the user.
    
    Used for batch operations to ensure user can only
    operate on their own resumes.
    
    Args:
        user: Django User object
        resume_ids: List of resume IDs
        
    Returns:
        QuerySet: Filtered resumes that belong to user
        
    Raises:
        PermissionDenied: If any resume doesn't belong to user
        
    Requirements: 16.2
    """
    # Get resumes that belong to user
    user_resumes = Resume.objects.filter(id__in=resume_ids, user=user)
    
    # Check if all requested IDs are owned by user
    if user_resumes.count() != len(resume_ids):
        # Some resumes don't belong to user
        owned_ids = set(user_resumes.values_list('id', flat=True))
        requested_ids = set(resume_ids)
        unauthorized_ids = requested_ids - owned_ids
        
        logger.warning(
            f'Batch operation authorization failed: User {user.username} (ID: {user.id}) '
            f'attempted to access resumes {unauthorized_ids} they do not own'
        )
        raise PermissionDenied(
            "You do not have permission to access one or more of the selected resumes."
        )
    
    return user_resumes


# Logging utilities

def log_access(user, resource_type, resource_id, action='view'):
    """
    Log resource access for audit trail.
    
    Args:
        user: Django User object
        resource_type: Type of resource (e.g., 'resume', 'upload', 'version')
        resource_id: ID of the resource
        action: Action performed (e.g., 'view', 'edit', 'delete')
    """
    logger.info(
        f'Access: User {user.username} (ID: {user.id}) '
        f'{action} {resource_type} {resource_id}'
    )


def log_authorization_failure(user, resource_type, resource_id, owner_username=None):
    """
    Log authorization failure for security monitoring.
    
    Args:
        user: Django User object attempting access
        resource_type: Type of resource
        resource_id: ID of the resource
        owner_username: Username of actual owner (if known)
    """
    owner_info = f' owned by {owner_username}' if owner_username else ''
    logger.warning(
        f'Authorization failure: User {user.username} (ID: {user.id}) '
        f'attempted to access {resource_type} {resource_id}{owner_info}'
    )
