from django.contrib import admin
from .models import Resume, PersonalInfo, Experience, Education, Skill, Project, Certification, ResumeAnalysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'latest_ats_score', 'completeness_score', 'updated_at']
    list_filter = ['template']
    search_fields = ['title', 'user__username']

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuer', 'resume', 'issue_date']
    search_fields = ['name', 'issuer']

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['resume', 'final_score', 'analysis_timestamp']
    list_filter = ['analysis_timestamp']
