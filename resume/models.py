# resume/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    summary = models.TextField()

    def __str__(self):
        
        return self.full_name
