from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, EmailValidator


class Resume(models.Model):
    """
    Main resume model containing metadata and template selection.
    Each user can have multiple resumes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    template = models.CharField(max_length=50, default='professional')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Version tracking
    current_version_number = models.IntegerField(default=1)
    
    # Analysis tracking
    last_analyzed_at = models.DateTimeField(null=True, blank=True)
    last_optimized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class PersonalInfo(models.Model):
    """
    Personal information section of a resume.
    One-to-one relationship with Resume.
    """
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(validators=[EmailValidator()])
    linkedin = models.URLField(blank=True, validators=[URLValidator()])
    github = models.URLField(blank=True, validators=[URLValidator()])
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"Personal Info - {self.full_name}"


class Experience(models.Model):
    """
    Work experience entry for a resume.
    Multiple experiences can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']
        indexes = [
            models.Index(fields=['resume', 'order']),
            models.Index(fields=['resume', '-start_date']),
        ]

    def __str__(self):
        return f"{self.role} at {self.company}"

    def clean(self):
        """Validate that start_date is before end_date if end_date is provided."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date.')


class Education(models.Model):
    """
    Education entry for a resume.
    Multiple education entries can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-end_year']
        indexes = [
            models.Index(fields=['resume', 'order']),
            models.Index(fields=['resume', '-end_year']),
        ]

    def __str__(self):
        return f"{self.degree} in {self.field} from {self.institution}"

    def clean(self):
        """Validate that start_year is before end_year if end_year is provided."""
        from django.core.exceptions import ValidationError
        if self.end_year and self.start_year > self.end_year:
            raise ValidationError('Start year must be before end year.')


class Skill(models.Model):
    """
    Skill entry for a resume.
    Multiple skills can be associated with one resume.
    Unique constraint on (resume, name) to prevent duplicates.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    class Meta:
        unique_together = [['resume', 'name']]
        indexes = [
            models.Index(fields=['resume', 'category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Project(models.Model):
    """
    Project entry for a resume.
    Multiple projects can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=500)
    url = models.URLField(blank=True, validators=[URLValidator()])
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['resume', 'order']),
        ]

    def __str__(self):
        return self.name


class ResumeVersion(models.Model):
    """
    Version history for resumes.
    Stores complete snapshots of resume state at different points in time.
    """
    MODIFICATION_TYPES = [
        ('manual', 'Manual Edit'),
        ('optimized', 'AI Optimized'),
        ('restored', 'Restored from History'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modification_type = models.CharField(max_length=20, choices=MODIFICATION_TYPES, default='manual')
    ats_score = models.FloatField(null=True, blank=True)
    snapshot_data = models.JSONField()  # Complete resume state
    user_notes = models.TextField(blank=True)

    class Meta:
        unique_together = [['resume', 'version_number']]
        indexes = [
            models.Index(fields=['resume', '-created_at']),
        ]
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.resume.title} - Version {self.version_number}"


class UploadedResume(models.Model):
    """
    Stores uploaded PDF resumes and their parsing status.
    Tracks the complete upload and parsing workflow.
    """
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('parsing', 'Parsing'),
        ('parsed', 'Parsed'),
        ('imported', 'Imported'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resumes')
    original_filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()
    extracted_text = models.TextField(blank=True)
    parsing_confidence = models.FloatField(null=True, blank=True)
    parsed_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
        ]
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"


class ResumeAnalysis(models.Model):
    """
    Stores comprehensive ATS analysis results for resumes.
    Tracks all component scores and detailed analysis data.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_description = models.TextField()
    analysis_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Component Scores
    keyword_match_score = models.FloatField()
    skill_relevance_score = models.FloatField()
    section_completeness_score = models.FloatField()
    experience_impact_score = models.FloatField()
    quantification_score = models.FloatField()
    action_verb_score = models.FloatField()
    
    # Composite Score
    final_score = models.FloatField()
    
    # Detailed Analysis (JSON)
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    weak_action_verbs = models.JSONField(default=list)
    missing_quantifications = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)

    class Meta:
        indexes = [
            models.Index(fields=['resume', '-analysis_timestamp']),
        ]
        ordering = ['-analysis_timestamp']
        verbose_name_plural = 'Resume analyses'

    def __str__(self):
        return f"Analysis for {self.resume.title} - Score: {self.final_score}"


class OptimizationHistory(models.Model):
    """
    Tracks resume optimization sessions and their results.
    Links original and optimized versions with detailed change tracking.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='optimizations')
    original_version = models.ForeignKey(
        ResumeVersion, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='optimizations_as_original'
    )
    optimized_version = models.ForeignKey(
        ResumeVersion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='optimizations_as_optimized'
    )
    job_description = models.TextField()
    optimization_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Scores
    original_score = models.FloatField()
    optimized_score = models.FloatField(null=True, blank=True)
    improvement_delta = models.FloatField(null=True, blank=True)
    
    # Changes (JSON)
    changes_summary = models.JSONField(default=dict)  # {type: count}
    detailed_changes = models.JSONField(default=list)  # [{section, field, old, new, reason}]
    accepted_changes = models.JSONField(default=list)
    rejected_changes = models.JSONField(default=list)
    user_notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['resume', '-optimization_timestamp']),
        ]
        ordering = ['-optimization_timestamp']
        verbose_name_plural = 'Optimization histories'

    def __str__(self):
        return f"Optimization for {self.resume.title} - Delta: {self.improvement_delta}"
