from django import forms
from .models import JobApplication, CoverLetter


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'role', 'job_url', 'job_description', 'resume',
                  'status', 'applied_date', 'notes']
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date'}),
            'job_description': forms.Textarea(attrs={'rows': 6}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].queryset = user.resumes.all()
        self.fields['resume'].required = False
        self.fields['job_description'].required = False
        self.fields['job_url'].required = False
        self.fields['applied_date'].required = False
        self.fields['notes'].required = False


class CoverLetterForm(forms.ModelForm):
    class Meta:
        model = CoverLetter
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'cover-letter-editor'}),
        }


class ScrapeJobForm(forms.Form):
    job_url = forms.URLField(label='Job Posting URL', widget=forms.URLInput(
        attrs={'placeholder': 'https://www.linkedin.com/jobs/view/...'}
    ))
