# resume/forms.py
from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'full_name', 'email', 'phone', 'address',
            'education', 'experience', 'skills', 'summary'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Address', 'rows': 3}),
            'education': forms.Textarea(attrs={'placeholder': 'Education', 'rows': 4}),
            'experience': forms.Textarea(attrs={'placeholder': 'Experience', 'rows': 4}),
            'skills': forms.Textarea(attrs={'placeholder': 'Skills', 'rows': 3}),
            'summary': forms.Textarea(attrs={'placeholder': 'Summary', 'rows': 3}),
        }
