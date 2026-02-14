from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, EmailValidator


class Resume(models.Model):
    """
    Main resume model containing metadata and template selection.
    Each user can have multiple resumes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    template = models.CharField(max_length=50, default='professional')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class PersonalInfo(models.Model):
    """
    Personal information section of a resume.
    One-to-one relationship with Resume.
    """
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(validators=[EmailValidator()])
    linkedin = models.URLField(blank=True, validators=[URLValidator()])
    github = models.URLField(blank=True, validators=[URLValidator()])
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"Personal Info - {self.full_name}"


class Experience(models.Model):
    """
    Work experience entry for a resume.
    Multiple experiences can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']
        indexes = [
            models.Index(fields=['resume', 'order']),
            models.Index(fields=['resume', '-start_date']),
        ]

    def __str__(self):
        return f"{self.role} at {self.company}"

    def clean(self):
        """Validate that start_date is before end_date if end_date is provided."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date.')


class Education(models.Model):
    """
    Education entry for a resume.
    Multiple education entries can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-end_year']
        indexes = [
            models.Index(fields=['resume', 'order']),
            models.Index(fields=['resume', '-end_year']),
        ]

    def __str__(self):
        return f"{self.degree} in {self.field} from {self.institution}"

    def clean(self):
        """Validate that start_year is before end_year if end_year is provided."""
        from django.core.exceptions import ValidationError
        if self.end_year and self.start_year > self.end_year:
            raise ValidationError('Start year must be before end year.')


class Skill(models.Model):
    """
    Skill entry for a resume.
    Multiple skills can be associated with one resume.
    Unique constraint on (resume, name) to prevent duplicates.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    class Meta:
        unique_together = [['resume', 'name']]
        indexes = [
            models.Index(fields=['resume', 'category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Project(models.Model):
    """
    Project entry for a resume.
    Multiple projects can be associated with one resume.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=500)
    url = models.URLField(blank=True, validators=[URLValidator()])
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['resume', 'order']),
        ]

    def __str__(self):
        return self.name
