from django.db import models
from django.contrib.auth.models import User
from apps.resumes.models import Resume, ResumeVersion


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    job_url = models.URLField(blank=True)
    job_description = models.TextField(blank=True)
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    resume_version = models.ForeignKey(ResumeVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='saved')
    ats_score_at_apply = models.FloatField(null=True, blank=True)
    applied_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.role} at {self.company} ({self.status})"


class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letters')
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, null=True, blank=True, related_name='cover_letter')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='cover_letters')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cover Letter - {self.role} at {self.company}"


class InterviewPrepSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_preps')
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True, related_name='interview_preps')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='interview_preps')
    role = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    job_description = models.TextField(blank=True)
    questions = models.JSONField(default=list)  # [{question, category, talking_points, resume_evidence}]
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Interview Prep - {self.role} ({self.user.username})"


class SkillGapAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_gap_analyses')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_gap_analyses')
    target_role = models.CharField(max_length=200)
    job_descriptions = models.JSONField(default=list)  # list of JD texts analysed
    missing_skills = models.JSONField(default=list)    # [{skill, frequency, importance}]
    present_skills = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Skill Gap - {self.target_role} ({self.user.username})"
