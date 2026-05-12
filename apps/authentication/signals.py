"""
SSO signal handlers for django-allauth.

Fired when a user signs up or connects a social account (Google / LinkedIn).
Populates first_name / last_name from the OAuth profile, logs the event,
and sends a welcome email to new SSO users.
"""
import logging
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_signed_up

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    """
    Fired for every new registration — SSO or standard form.
    - Logs to ActivityLog
    - Sends welcome email for SSO users (email-registered users get it after verification)
    """
    from apps.authentication.models import ActivityLog
    try:
        ActivityLog.log(
            user=user,
            action='resume_created',
            description=f'Account created for {user.username}',
        )
        logger.info(f'New user signed up: {user.username} ({user.email})')
    except Exception as e:
        logger.warning(f'Could not log signup for {user.username}: {e}')

    # For SSO signups the email is already verified — send welcome immediately
    sociallogin = kwargs.get('sociallogin')
    if sociallogin is not None:
        try:
            from apps.resumes.tasks import send_welcome_email_task
            base_url = request.build_absolute_uri('/').rstrip('/')
            send_welcome_email_task.delay(user.id, base_url)
        except Exception as e:
            logger.warning(f'Could not queue welcome email for SSO user {user.username}: {e}')


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    """
    Fired when a Google or LinkedIn account is connected to a Django user.
    Copies first_name / last_name from the OAuth profile if not already set.
    """
    user     = sociallogin.user
    try:
        extra    = sociallogin.account.extra_data
        provider = sociallogin.account.provider

        if provider == 'google':
            if not user.first_name:
                user.first_name = extra.get('given_name', '')
            if not user.last_name:
                user.last_name = extra.get('family_name', '')

        elif provider == 'linkedin_oauth2':
            if not user.first_name:
                user.first_name = extra.get('localizedFirstName', extra.get('given_name', ''))
            if not user.last_name:
                user.last_name = extra.get('localizedLastName', extra.get('family_name', ''))

        if user.first_name or user.last_name:
            user.save(update_fields=['first_name', 'last_name'])

        logger.info(f'Social account ({provider}) linked to user {user.username}')

    except Exception as e:
        logger.warning(f'Could not populate profile from social account: {e}')
