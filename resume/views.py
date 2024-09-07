# resume/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ResumeForm
from .models import Resume


def editor_template(request, template_name):
    # Assuming you might have some logic to handle different templates
    context = {'template_name': template_name}
    return render(request, 'resume/editor_template.html', context)

def resume_templates(request):
    return render(request, 'NextGenCV/ResumeTemplates.html')

@login_required
def create_resume_view(request):
    # Check if the user already has a resume
    existing_resume = Resume.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # Load existing data if present, or create a new form if not
        form = ResumeForm(request.POST, instance=existing_resume)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user  # Ensure the resume is linked to the logged-in user
            resume.save()
            return redirect('dashboard')  # Redirect to the named URL pattern for the dashboard
        else:
            # Handle form errors if needed
            return render(request, 'resume/create_resume.html', {'form': form})
    else:
        # Create a form with existing data if available, otherwise an empty form
        form = ResumeForm(instance=existing_resume)

    return render(request, 'resume/create_resume.html', {'form': form})
