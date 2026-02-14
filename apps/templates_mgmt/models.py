from django.db import models
from apps.resumes.models import Resume


class ResumeTemplate(models.Model):
    """
    Stores resume template metadata and configuration.
    Manages multiple template styles with customization options.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    template_file = models.CharField(max_length=200)  # Path to HTML template
    thumbnail = models.ImageField(upload_to='template_thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)
    
    # Customization Options
    supports_color_customization = models.BooleanField(default=True)
    supports_font_customization = models.BooleanField(default=True)
    available_colors = models.JSONField(default=list)
    available_fonts = models.JSONField(default=list)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name


class TemplateCustomization(models.Model):
    """
    Stores user-specific template customizations.
    One-to-one relationship with Resume.
    """
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='template_customization')
    template = models.ForeignKey(ResumeTemplate, on_delete=models.PROTECT)
    color_scheme = models.CharField(max_length=50, blank=True)
    font_family = models.CharField(max_length=100, blank=True)
    custom_css = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Template customizations'

    def __str__(self):
        return f"Customization for {self.resume.title}"
