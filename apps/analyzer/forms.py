"""
Forms for the ATS Analyzer application.

Validates: Requirements 9.1, 14.1, 14.2, 14.3, 14.4
"""

from django import forms
from django.core.exceptions import ValidationError
import bleach


class JobDescriptionForm(forms.Form):
    """
    Form for job description input for ATS analysis.
    
    Validates: Requirements 9.1, 14.1, 14.2, 14.3, 14.4
    """
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste the job description here...',
            'required': True
        }),
        label='Job Description',
        help_text='Enter the complete job description to analyze your resume against.',
        required=True,
        max_length=10000,
        error_messages={
            'required': 'Please enter a job description to analyze.',
            'max_length': 'Job description cannot exceed 10,000 characters.'
        }
    )
    
    def clean_job_description(self):
        """
        Validate that job description is not empty or just whitespace.
        Sanitizes input to prevent XSS and validates length.
        """
        job_description = self.cleaned_data.get('job_description', '')
        
        # Strip whitespace and check if empty
        if not job_description.strip():
            raise ValidationError('Job description cannot be empty.')
        
        # Sanitize to prevent XSS (allow basic formatting tags)
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3']
        job_description = bleach.clean(job_description.strip(), tags=allowed_tags, strip=True)
        
        # Validate length
        if len(job_description) > 10000:
            raise ValidationError('Job description cannot exceed 10,000 characters.')
        
        if len(job_description) < 10:
            raise ValidationError('Job description must be at least 10 characters long.')
        
        return job_description
