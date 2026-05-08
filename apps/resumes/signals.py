"""
Post-save signals to keep Resume.completeness_score up to date
without recalculating on every page load.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _refresh_completeness(resume_id: int):
    """Recalculate and persist completeness score for a single resume."""
    try:
        from apps.resumes.models import Resume
        from apps.analyzer.views import _compute_completeness
        resume = Resume.objects.get(id=resume_id)
        new_score = _compute_completeness(resume)
        if resume.completeness_score != new_score:
            Resume.objects.filter(id=resume_id).update(completeness_score=new_score)
    except Exception as e:
        logger.warning(f"Could not refresh completeness for resume {resume_id}: {e}")


@receiver(post_save, sender='resumes.Experience')
@receiver(post_delete, sender='resumes.Experience')
def on_experience_change(sender, instance, **kwargs):
    _refresh_completeness(instance.resume_id)


@receiver(post_save, sender='resumes.Education')
@receiver(post_delete, sender='resumes.Education')
def on_education_change(sender, instance, **kwargs):
    _refresh_completeness(instance.resume_id)


@receiver(post_save, sender='resumes.Skill')
@receiver(post_delete, sender='resumes.Skill')
def on_skill_change(sender, instance, **kwargs):
    _refresh_completeness(instance.resume_id)


@receiver(post_save, sender='resumes.Project')
@receiver(post_delete, sender='resumes.Project')
def on_project_change(sender, instance, **kwargs):
    _refresh_completeness(instance.resume_id)


@receiver(post_save, sender='resumes.PersonalInfo')
def on_personal_info_change(sender, instance, **kwargs):
    _refresh_completeness(instance.resume_id)
