from django.contrib import admin
from .models import JobApplication, CoverLetter

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['company', 'role', 'status', 'user', 'applied_date', 'ats_score_at_apply']
    list_filter = ['status']
    search_fields = ['company', 'role', 'user__username']

@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ['company', 'role', 'user', 'created_at']
    search_fields = ['company', 'role', 'user__username']
