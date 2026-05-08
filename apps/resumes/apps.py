from django.apps import AppConfig


class ResumesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.resumes'

    def ready(self):
        import apps.resumes.signals  # noqa: F401
