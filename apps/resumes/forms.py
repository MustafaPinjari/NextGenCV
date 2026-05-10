"""
Forms for resume management.

Validates: Requirements 14.1, 14.2, 14.3, 14.4
"""
from django import forms
from django.core.exceptions import ValidationError
import bleach
from .models import Resume, PersonalInfo, Experience, Education, Skill, Project


class ResumeForm(forms.ModelForm):
    """Form for resume title and template selection."""
    
    TEMPLATE_CHOICES = [
        ('professional', 'Professional'),
        ('modern', 'Modern'),
        ('classic', 'Classic')
    ]
    
    template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        error_messages={
            'required': 'Please select a template.',
            'invalid_choice': 'Please select a valid template.',
        }
    )
    
    class Meta:
        model = Resume
        fields = ['title', 'template']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Engineer Resume'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['title'].error_messages = {'required': 'Resume title is required.', 'max_length': 'Resume title cannot exceed 200 characters.'}
        self.fields['template'].error_messages.update({'required': 'Please select a template.'})
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Resume title is required.')
        title = bleach.clean(title.strip())
        if len(title) > 200:
            raise ValidationError('Resume title cannot exceed 200 characters.')
        if len(title) < 1:
            raise ValidationError('Resume title cannot be empty.')
        return title
    
    def clean_template(self):
        template = self.cleaned_data.get('template')
        if template not in ['professional', 'modern', 'classic']:
            raise ValidationError('Please select a valid template.')
        return template


class PersonalInfoForm(forms.ModelForm):
    """Form for personal information."""
    
    class Meta:
        model = PersonalInfo
        fields = ['full_name', 'phone', 'email', 'linkedin', 'github', 'location']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.doe@example.com'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/johndoe'}),
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/johndoe'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = False
        self.fields['linkedin'].required = False
        self.fields['github'].required = False
        self.fields['location'].required = False
        self.fields['full_name'].error_messages = {'required': 'Full name is required.', 'max_length': 'Full name cannot exceed 200 characters.'}
        self.fields['email'].error_messages = {'required': 'Email is required.', 'invalid': 'Please enter a valid email address.'}
        self.fields['phone'].error_messages = {'max_length': 'Phone number cannot exceed 20 characters.'}
        self.fields['linkedin'].error_messages = {'invalid': 'Please enter a valid LinkedIn URL.'}
        self.fields['github'].error_messages = {'invalid': 'Please enter a valid GitHub URL.'}
        self.fields['location'].error_messages = {'max_length': 'Location cannot exceed 200 characters.'}
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name:
            raise ValidationError('Full name is required.')
        full_name = bleach.clean(full_name.strip())
        if len(full_name) > 200:
            raise ValidationError('Full name cannot exceed 200 characters.')
        if len(full_name) < 1:
            raise ValidationError('Full name cannot be empty.')
        return full_name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = bleach.clean(phone.strip())
            if len(phone) > 20:
                raise ValidationError('Phone number cannot exceed 20 characters.')
        return phone if phone else ''
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        email = bleach.clean(email.strip())
        return email.lower()
    
    def clean_linkedin(self):
        linkedin = self.cleaned_data.get('linkedin')
        if linkedin:
            linkedin = bleach.clean(linkedin.strip())
            return linkedin
        return ''
    
    def clean_github(self):
        github = self.cleaned_data.get('github')
        if github:
            github = bleach.clean(github.strip())
            return github
        return ''
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            location = bleach.clean(location.strip())
            if len(location) > 200:
                raise ValidationError('Location cannot exceed 200 characters.')
        return location if location else ''


class ExperienceForm(forms.ModelForm):
    """Form for work experience entry with enhanced fields for achievements."""
    
    class Meta:
        model = Experience
        fields = ['company', 'role', 'location', 'start_date', 'end_date', 'description', 'achievements']
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Company Name'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Job Title (e.g., Senior Software Engineer)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'City, State/Country (e.g., San Francisco, CA)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'Select start date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'Select end date',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Brief overview of your role and responsibilities...'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6, 
                'placeholder': '• Developed and deployed 5+ full-stack applications serving 10,000+ users\n• Improved application performance by 40% through database optimization\n• Led code reviews and mentored 3 junior developers\n• Implemented RESTful APIs handling 1M+ requests daily'
            })
        }
        help_texts = {
            'achievements': 'List your key achievements with quantifiable metrics (one per line, start with action verbs like Developed, Implemented, Led, Optimized)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['location'].required = False
        self.fields['achievements'].required = False
        self.fields['company'].required = True
        self.fields['company'].error_messages = {'required': 'Company name is required.', 'max_length': 'Company name cannot exceed 200 characters.'}
        self.fields['role'].required = True
        self.fields['role'].error_messages = {'required': 'Job role is required.', 'max_length': 'Job role cannot exceed 200 characters.'}
        self.fields['start_date'].required = True
        self.fields['start_date'].error_messages = {'required': 'Start date is required.', 'invalid': 'Please enter a valid date.'}
        self.fields['end_date'].error_messages = {'invalid': 'Please enter a valid date.'}
        self.fields['description'].required = False
        self.fields['achievements'].help_text = 'List your key achievements with quantifiable metrics (one per line, start with action verbs)'
    
    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            raise ValidationError('Company name is required.')
        company = bleach.clean(company.strip())
        if len(company) > 200:
            raise ValidationError('Company name cannot exceed 200 characters.')
        if len(company) < 1:
            raise ValidationError('Company name cannot be empty.')
        return company
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise ValidationError('Job role is required.')
        role = bleach.clean(role.strip())
        if len(role) > 200:
            raise ValidationError('Job role cannot exceed 200 characters.')
        if len(role) < 1:
            raise ValidationError('Job role cannot be empty.')
        return role
    
    def clean_location(self):
        location = self.cleaned_data.get('location', '')
        if location:
            location = bleach.clean(location.strip())
        return location
    
    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if description:
            allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
            description = bleach.clean(description.strip(), tags=allowed_tags, strip=True)
        return description
    
    def clean_achievements(self):
        achievements = self.cleaned_data.get('achievements', '')
        if achievements:
            achievements = bleach.clean(achievements.strip())
        return achievements
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Start date must be before end date.')
        return cleaned_data


class EducationForm(forms.ModelForm):
    """Form for education entry with enhanced fields."""
    
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field', 'start_year', 'end_year', 'gpa', 'honors', 'relevant_coursework']
        widgets = {
            'institution': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'University Name'
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Bachelor of Science'
            }),
            'field': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Computer Science'
            }),
            'start_year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '2018'
            }),
            'end_year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '2022'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '3.8',
                'step': '0.01',
                'min': '0',
                'max': '4.0'
            }),
            'honors': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Summa Cum Laude, Dean\'s List'
            }),
            'relevant_coursework': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Data Structures, Algorithms, Machine Learning, Database Systems'
            })
        }
        help_texts = {
            'gpa': 'GPA out of 4.0 (optional, only include if 3.5 or higher)',
            'honors': 'Academic honors, awards, or distinctions',
            'relevant_coursework': 'Comma-separated list of relevant courses'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['institution'].required = True
        self.fields['degree'].required = True
        self.fields['field'].required = True
        self.fields['start_year'].required = True
        self.fields['end_year'].required = False
        self.fields['gpa'].required = False
        self.fields['honors'].required = False
        self.fields['relevant_coursework'].required = False
        self.fields['institution'].error_messages = {'required': 'Institution name is required.', 'max_length': 'Institution name cannot exceed 200 characters.'}
        self.fields['degree'].error_messages = {'required': 'Degree is required.', 'max_length': 'Degree cannot exceed 200 characters.'}
        self.fields['field'].error_messages = {'required': 'Field of study is required.', 'max_length': 'Field of study cannot exceed 200 characters.'}
        self.fields['start_year'].error_messages = {'required': 'Start year is required.', 'invalid': 'Please enter a valid year.'}
        self.fields['end_year'].error_messages = {'invalid': 'Please enter a valid year.'}
    
    def clean_institution(self):
        institution = self.cleaned_data.get('institution')
        if not institution:
            raise ValidationError('Institution name is required.')
        institution = bleach.clean(institution.strip())
        if len(institution) > 200:
            raise ValidationError('Institution name cannot exceed 200 characters.')
        if len(institution) < 1:
            raise ValidationError('Institution name cannot be empty.')
        return institution
    
    def clean_degree(self):
        degree = self.cleaned_data.get('degree')
        if not degree:
            raise ValidationError('Degree is required.')
        degree = bleach.clean(degree.strip())
        if len(degree) > 200:
            raise ValidationError('Degree cannot exceed 200 characters.')
        if len(degree) < 1:
            raise ValidationError('Degree cannot be empty.')
        return degree
    
    def clean_field(self):
        field = self.cleaned_data.get('field')
        if not field:
            raise ValidationError('Field of study is required.')
        field = bleach.clean(field.strip())
        if len(field) > 200:
            raise ValidationError('Field of study cannot exceed 200 characters.')
        if len(field) < 1:
            raise ValidationError('Field of study cannot be empty.')
        return field
    
    def clean_start_year(self):
        start_year = self.cleaned_data.get('start_year')
        if start_year:
            if start_year < 1900 or start_year > 2100:
                raise ValidationError('Please enter a valid year between 1900 and 2100.')
        return start_year
    
    def clean_end_year(self):
        end_year = self.cleaned_data.get('end_year')
        if end_year:
            if end_year < 1900 or end_year > 2100:
                raise ValidationError('Please enter a valid year between 1900 and 2100.')
        return end_year
    
    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        if gpa is not None:
            if gpa < 0 or gpa > 4.0:
                raise ValidationError('GPA must be between 0.0 and 4.0')
        return gpa
    
    def clean_honors(self):
        honors = self.cleaned_data.get('honors', '')
        if honors:
            honors = bleach.clean(honors.strip())
        return honors
    
    def clean_relevant_coursework(self):
        coursework = self.cleaned_data.get('relevant_coursework', '')
        if coursework:
            coursework = bleach.clean(coursework.strip())
        return coursework
    
    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        if start_year and end_year and start_year > end_year:
            raise ValidationError('Start year must be before end year.')
        return cleaned_data


class SkillForm(forms.ModelForm):
    """Form for skill entry with proficiency level."""
    
    CATEGORY_CHOICES = [
        ('Languages', 'Programming Languages'),
        ('Frameworks', 'Frameworks & Libraries'),
        ('Tools', 'Tools & Technologies'),
        ('Databases', 'Databases'),
        ('Cloud', 'Cloud Platforms'),
        ('Soft Skills', 'Soft Skills'),
        ('Other', 'Other')
    ]
    
    category = forms.ChoiceField(
        choices=[('', '— Select category —')] + CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        error_messages={
            'required': 'Please select a category.',
            'invalid_choice': 'Please select a valid category.',
        }
    )
    
    proficiency_level = forms.ChoiceField(
        choices=[('', '— Select level —')] + list(Skill.PROFICIENCY_LEVELS),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        initial='intermediate',
        error_messages={'invalid_choice': 'Please select a valid proficiency level.'}
    )
    
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency_level', 'years_of_experience']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Python, React, AWS, Leadership'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '3',
                'min': '0',
                'max': '50'
            })
        }
        help_texts = {
            'proficiency_level': 'Your skill level (optional)',
            'years_of_experience': 'Years of experience (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        self.resume = kwargs.pop('resume', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['proficiency_level'].required = False
        self.fields['years_of_experience'].required = False
        self.fields['name'].error_messages = {'required': 'Skill name is required.', 'max_length': 'Skill name cannot exceed 100 characters.'}
        self.fields['category'].error_messages.update({'required': 'Please select a category.'})
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Skill name is required.')
        name = bleach.clean(name.strip())
        if len(name) > 100:
            raise ValidationError('Skill name cannot exceed 100 characters.')
        if len(name) < 1:
            raise ValidationError('Skill name cannot be empty.')
        if self.resume:
            existing_skills = Skill.objects.filter(resume=self.resume, name__iexact=name)
            if self.instance.pk:
                existing_skills = existing_skills.exclude(pk=self.instance.pk)
            if existing_skills.exists():
                raise ValidationError(f'A skill with the name "{name}" already exists on this resume.')
        return name
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        valid_categories = [choice[0] for choice in self.CATEGORY_CHOICES]
        if category not in valid_categories:
            raise ValidationError('Please select a valid category.')
        return category
    
    def clean_years_of_experience(self):
        years = self.cleaned_data.get('years_of_experience')
        if years is not None:
            if years < 0 or years > 50:
                raise ValidationError('Years of experience must be between 0 and 50')
        return years


class ProjectForm(forms.ModelForm):
    """Form for project entry with enhanced fields."""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'technologies', 'impact', 'url', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Project Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Describe the project, your role, and what problem it solves...'
            }),
            'technologies': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Python, Django, PostgreSQL, React, AWS'
            }),
            'impact': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Achieved 95% ATS compatibility score, Serving 10,000+ users, Reduced processing time by 40%'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://github.com/username/project or https://project-demo.com'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'Select start date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'type': 'date',
                'placeholder': 'Select end date',
            })
        }
        help_texts = {
            'impact': 'Quantifiable results or achievements (optional)',
            'url': 'GitHub repository, live demo, or portfolio link (optional)',
            'start_date': 'Project start date (optional)',
            'end_date': 'Project end date (optional, leave blank if ongoing)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['technologies'].required = True
        self.fields['impact'].required = False
        self.fields['url'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['name'].error_messages = {'required': 'Project name is required.', 'max_length': 'Project name cannot exceed 200 characters.'}
        self.fields['description'].error_messages = {'required': 'Project description is required.'}
        self.fields['technologies'].error_messages = {'required': 'Technologies are required.', 'max_length': 'Technologies cannot exceed 500 characters.'}
        self.fields['url'].error_messages = {'invalid': 'Please enter a valid URL.'}
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Project name is required.')
        name = bleach.clean(name.strip())
        if len(name) > 200:
            raise ValidationError('Project name cannot exceed 200 characters.')
        if len(name) < 1:
            raise ValidationError('Project name cannot be empty.')
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise ValidationError('Project description is required.')
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        description = bleach.clean(description.strip(), tags=allowed_tags, strip=True)
        if len(description) < 1:
            raise ValidationError('Project description cannot be empty.')
        return description
    
    def clean_technologies(self):
        technologies = self.cleaned_data.get('technologies')
        if not technologies:
            raise ValidationError('Technologies are required.')
        technologies = bleach.clean(technologies.strip())
        if len(technologies) > 500:
            raise ValidationError('Technologies cannot exceed 500 characters.')
        if len(technologies) < 1:
            raise ValidationError('Technologies cannot be empty.')
        return technologies
    
    def clean_impact(self):
        impact = self.cleaned_data.get('impact', '')
        if impact:
            impact = bleach.clean(impact.strip())
        return impact
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url:
            url = bleach.clean(url.strip())
            return url
        return ''
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Start date must be before end date.')
        return cleaned_data



class SummaryForm(forms.Form):
    """Form for professional summary."""
    
    summary = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write a brief professional summary highlighting your key qualifications and career goals...',
            'maxlength': '500'
        }),
        help_text='2-4 sentences that capture your professional identity and value proposition'
    )
    
    def clean_summary(self):
        summary = self.cleaned_data.get('summary', '')
        if summary:
            summary = bleach.clean(summary.strip())
            if len(summary) > 500:
                raise ValidationError('Summary cannot exceed 500 characters.')
        return summary
