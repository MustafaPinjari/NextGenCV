# resume/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    First_Name = models.CharField(max_length=50)
    Last_Name = models.CharField(max_length=50, default='Unknown')  # Added default value
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    summary = models.TextField()
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name}"
