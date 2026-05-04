from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0018_resume_score_sharing'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('issuer', models.CharField(max_length=200, blank=True, default='')),
                ('issue_date', models.DateField(null=True, blank=True)),
                ('expiry_date', models.DateField(null=True, blank=True)),
                ('credential_id', models.CharField(max_length=200, blank=True, default='')),
                ('credential_url', models.URLField(blank=True, default='')),
                ('order', models.IntegerField(default=0)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certifications', to='resumes.resume')),
            ],
            options={'ordering': ['order', '-issue_date']},
        ),
    ]
