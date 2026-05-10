from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils import timezone
from datetime import timedelta


class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('resume_created', 'Resume Created'),
        ('resume_updated', 'Resume Updated'),
        ('resume_deleted', 'Resume Deleted'),
        ('resume_exported', 'Resume Exported'),
        ('resume_duplicated', 'Resume Duplicated'),
        ('resume_analyzed', 'Resume Analyzed'),
        ('resume_optimized', 'Resume Optimized'),
        ('pdf_uploaded', 'PDF Uploaded'),
        ('pdf_imported', 'PDF Imported'),
        ('version_restored', 'Version Restored'),
        ('cover_letter_generated', 'Cover Letter Generated'),
        ('application_created', 'Application Created'),
        ('application_updated', 'Application Updated'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.CharField(max_length=300)
    resume_id = models.IntegerField(null=True, blank=True)
    resume_title = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} — {self.action} — {self.created_at:%Y-%m-%d %H:%M}"

    @classmethod
    def log(cls, user, action, description, resume=None, metadata=None):
        cls.objects.create(
            user=user,
            action=action,
            description=description,
            resume_id=resume.id if resume else None,
            resume_title=resume.title if resume else '',
            metadata=metadata or {},
        )
        # Keep only the 200 most recent entries per user.
        # Subquery approach works on both SQLite and PostgreSQL.
        keep_ids = (
            cls.objects
            .filter(user=user)
            .order_by('-created_at')
            .values_list('id', flat=True)[:200]
        )
        # Wrap in list() to force evaluation before the DELETE
        cls.objects.filter(user=user).exclude(id__in=list(keep_ids)).delete()


class SavedJobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_job_descriptions')
    title = models.CharField(max_length=200, help_text='e.g. "Senior Python Dev @ Google"')
    company = models.CharField(max_length=200, blank=True)
    job_url = models.URLField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_used_at', '-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class EmailVerificationToken(models.Model):
    """
    One-time token for email address verification.
    Created on registration; expires after 48 hours.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Email Verification Token'

    def __str__(self):
        return f"Verification for {self.user.username} — {'verified' if self.verified_at else 'pending'}"

    @classmethod
    def create_for_user(cls, user) -> 'EmailVerificationToken':
        """Generate a fresh token for a user, replacing any existing one."""
        token = secrets.token_urlsafe(48)
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={'token': token, 'verified_at': None},
        )
        return obj

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(hours=48)

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None
