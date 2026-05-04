from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50, choices=[
                    ('resume_created', 'Resume Created'), ('resume_updated', 'Resume Updated'),
                    ('resume_deleted', 'Resume Deleted'), ('resume_exported', 'Resume Exported'),
                    ('resume_duplicated', 'Resume Duplicated'), ('resume_analyzed', 'Resume Analyzed'),
                    ('resume_optimized', 'Resume Optimized'), ('pdf_uploaded', 'PDF Uploaded'),
                    ('pdf_imported', 'PDF Imported'), ('version_restored', 'Version Restored'),
                    ('cover_letter_generated', 'Cover Letter Generated'),
                    ('application_created', 'Application Created'),
                    ('application_updated', 'Application Updated'),
                ])),
                ('description', models.CharField(max_length=300)),
                ('resume_id', models.IntegerField(blank=True, null=True)),
                ('resume_title', models.CharField(blank=True, max_length=200)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'indexes': [models.Index(fields=['user', '-created_at'], name='auth_actlog_user_idx')]},
        ),
        migrations.CreateModel(
            name='SavedJobDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('company', models.CharField(blank=True, max_length=200)),
                ('job_url', models.URLField(blank=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_job_descriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-last_used_at', '-created_at'], 'indexes': [models.Index(fields=['user', '-created_at'], name='auth_savedjd_user_idx')]},
        ),
    ]
