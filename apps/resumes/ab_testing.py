"""
Resume A/B Testing — let users create two resume versions for the same job
and track which version gets more responses.

This brings conversion rate optimisation thinking to job searching.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.resumes.models import Resume, ResumeVersion


class ResumeABTest(models.Model):
    """
    An A/B test comparing two resume versions for a specific role/company.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('concluded', 'Concluded'),
        ('paused', 'Paused'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ab_tests')
    name = models.CharField(max_length=200, help_text='e.g. "Software Engineer @ Google — Q1 2025"')
    target_role = models.CharField(max_length=200)
    target_company = models.CharField(max_length=200, blank=True)
    job_description = models.TextField(blank=True)

    # The two variants
    resume_a = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name='ab_tests_as_a',
        help_text='Version A (control)'
    )
    resume_b = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name='ab_tests_as_b',
        help_text='Version B (variant)'
    )

    # Hypothesis
    hypothesis = models.TextField(
        blank=True,
        help_text='What you changed and why you think it will perform better'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    concluded_at = models.DateTimeField(null=True, blank=True)
    winner = models.CharField(max_length=1, blank=True, choices=[('A', 'A'), ('B', 'B')])
    conclusion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resume A/B Test'

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def applications_a(self):
        from apps.tracker.models import JobApplication
        return JobApplication.objects.filter(user=self.user, resume=self.resume_a)

    @property
    def applications_b(self):
        from apps.tracker.models import JobApplication
        return JobApplication.objects.filter(user=self.user, resume=self.resume_b)

    def get_stats(self) -> dict:
        """Calculate performance stats for both variants."""
        def _stats(apps_qs):
            total = apps_qs.count()
            applied = apps_qs.filter(status__in=['applied', 'interview', 'offer', 'rejected']).count()
            interviews = apps_qs.filter(status__in=['interview', 'offer']).count()
            offers = apps_qs.filter(status='offer').count()
            callback_rate = round(interviews / applied * 100, 1) if applied else 0
            return {
                'total': total,
                'applied': applied,
                'interviews': interviews,
                'offers': offers,
                'callback_rate': callback_rate,
            }

        stats_a = _stats(self.applications_a)
        stats_b = _stats(self.applications_b)

        # Determine leading variant
        leading = None
        if stats_a['callback_rate'] > stats_b['callback_rate']:
            leading = 'A'
        elif stats_b['callback_rate'] > stats_a['callback_rate']:
            leading = 'B'

        return {
            'a': stats_a,
            'b': stats_b,
            'leading': leading,
            'sufficient_data': (stats_a['applied'] + stats_b['applied']) >= 10,
        }
