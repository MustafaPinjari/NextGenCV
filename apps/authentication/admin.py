from django.contrib import admin
from .models import ActivityLog, SavedJobDescription

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'created_at']
    list_filter = ['action']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']

@admin.register(SavedJobDescription)
class SavedJobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'company', 'created_at', 'last_used_at']
    search_fields = ['title', 'user__username', 'company']
