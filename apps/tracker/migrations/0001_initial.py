from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('resumes', '0017_add_enhanced_resume_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
                ('job_url', models.URLField(blank=True)),
                ('job_description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('saved', 'Saved'), ('applied', 'Applied'), ('interview', 'Interview'), ('offer', 'Offer'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')], default='saved', max_length=20)),
                ('ats_score_at_apply', models.FloatField(blank=True, null=True)),
                ('applied_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='resumes.resume')),
                ('resume_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='resumes.resumeversion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['user', '-updated_at'], name='tracker_job_user_id_updated_idx'),
                    models.Index(fields=['user', 'status'], name='tracker_job_user_id_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='CoverLetter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200)),
                ('role', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('application', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cover_letter', to='tracker.jobapplication')),
                ('resume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cover_letters', to='resumes.resume')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cover_letters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
