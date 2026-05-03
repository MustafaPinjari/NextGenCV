from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0017_add_enhanced_resume_fields'),
        ('tracker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewPrepSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=200)),
                ('company', models.CharField(blank=True, max_length=200)),
                ('job_description', models.TextField(blank=True)),
                ('questions', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='interview_preps', to='tracker.jobapplication')),
                ('resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interview_preps', to='resumes.resume')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_preps', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SkillGapAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_role', models.CharField(max_length=200)),
                ('job_descriptions', models.JSONField(default=list)),
                ('missing_skills', models.JSONField(default=list)),
                ('present_skills', models.JSONField(default=list)),
                ('recommendations', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skill_gap_analyses', to='resumes.resume')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_gap_analyses', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
