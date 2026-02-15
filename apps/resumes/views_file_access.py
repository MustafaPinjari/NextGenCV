"""
Secure file access views with authorization checks.

This module provides secure file serving with proper access control.
Files are only served to authorized users who own the files.
"""

import os
import logging
import mimetypes
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import UploadedResume

logger = logging.getLogger(__name__)


@login_required
def serve_uploaded_resume(request, upload_id):
    """
    Serve uploaded resume file with access control.
    
    Only the user who uploaded the file can access it.
    This prevents unauthorized access to uploaded PDFs.
    
    Args:
        request: HTTP request
        upload_id: ID of the UploadedResume
        
    Returns:
        FileResponse with PDF content or 403 Forbidden
        
    Requirements: 15.6, 16.1, 16.2
    """
    # Get the uploaded resume
    uploaded_resume = get_object_or_404(UploadedResume, id=upload_id)
    
    # Authorization check - verify ownership
    if uploaded_resume.user != request.user:
        logger.warning(
            f'Unauthorized file access attempt: User {request.user.username} '
            f'tried to access upload {upload_id} owned by {uploaded_resume.user.username}'
        )
        return HttpResponseForbidden(
            "You do not have permission to access this file."
        )
    
    # Get file path
    file_path = uploaded_resume.file_path.path
    
    # Verify file exists
    if not os.path.exists(file_path):
        logger.error(f'File not found: {file_path} for upload ID {upload_id}')
        raise Http404("File not found")
    
    # Verify file is within allowed directory (prevent path traversal)
    media_root = str(settings.MEDIA_ROOT)
    real_file_path = os.path.realpath(file_path)
    real_media_root = os.path.realpath(media_root)
    
    if not real_file_path.startswith(real_media_root):
        logger.error(
            f'Path traversal attempt detected: {file_path} '
            f'is outside MEDIA_ROOT for upload ID {upload_id}'
        )
        return HttpResponseForbidden("Invalid file path")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/pdf'
    
    # Log access
    logger.info(
        f'File access: User {request.user.username} '
        f'accessed upload {upload_id} ({uploaded_resume.original_filename})'
    )
    
    # Serve file
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )
        response['Content-Disposition'] = f'inline; filename="{uploaded_resume.original_filename}"'
        return response
    except Exception as e:
        logger.error(f'Error serving file {file_path}: {e}', exc_info=True)
        raise Http404("Error serving file")


@login_required
def download_uploaded_resume(request, upload_id):
    """
    Download uploaded resume file with access control.
    
    Similar to serve_uploaded_resume but forces download instead of inline display.
    
    Args:
        request: HTTP request
        upload_id: ID of the UploadedResume
        
    Returns:
        FileResponse with PDF content as attachment or 403 Forbidden
        
    Requirements: 15.6, 16.1, 16.2
    """
    # Get the uploaded resume
    uploaded_resume = get_object_or_404(UploadedResume, id=upload_id)
    
    # Authorization check - verify ownership
    if uploaded_resume.user != request.user:
        logger.warning(
            f'Unauthorized download attempt: User {request.user.username} '
            f'tried to download upload {upload_id} owned by {uploaded_resume.user.username}'
        )
        return HttpResponseForbidden(
            "You do not have permission to download this file."
        )
    
    # Get file path
    file_path = uploaded_resume.file_path.path
    
    # Verify file exists
    if not os.path.exists(file_path):
        logger.error(f'File not found: {file_path} for upload ID {upload_id}')
        raise Http404("File not found")
    
    # Verify file is within allowed directory
    media_root = str(settings.MEDIA_ROOT)
    real_file_path = os.path.realpath(file_path)
    real_media_root = os.path.realpath(media_root)
    
    if not real_file_path.startswith(real_media_root):
        logger.error(
            f'Path traversal attempt detected: {file_path} '
            f'is outside MEDIA_ROOT for upload ID {upload_id}'
        )
        return HttpResponseForbidden("Invalid file path")
    
    # Log download
    logger.info(
        f'File download: User {request.user.username} '
        f'downloaded upload {upload_id} ({uploaded_resume.original_filename})'
    )
    
    # Serve file as download
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{uploaded_resume.original_filename}"'
        return response
    except Exception as e:
        logger.error(f'Error downloading file {file_path}: {e}', exc_info=True)
        raise Http404("Error downloading file")
