from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0017_add_enhanced_resume_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='latest_ats_score',
            field=models.FloatField(blank=True, null=True, help_text='Most recent ATS score'),
        ),
        migrations.AddField(
            model_name='resume',
            name='completeness_score',
            field=models.IntegerField(default=0, help_text='Resume completeness 0-100'),
        ),
        migrations.AddField(
            model_name='resume',
            name='share_token',
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
    ]
