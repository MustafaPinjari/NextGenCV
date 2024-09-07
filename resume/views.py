# resume/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ResumeForm
from .models import Resume

@login_required
def create_resume_view(request):
    # Check if the user already has a resume
    existing_resume = Resume.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # Load existing data if present, or create a new form if not
        form = ResumeForm(request.POST, request.FILES,instance=existing_resume)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user  # Ensure the resume is linked to the logged-in user
            resume.save()
            return redirect('dashboard')  # Redirect to the dashboard after saving
    else:
        # Create a form with existing data if available, otherwise an empty form
        form = ResumeForm(instance=existing_resume)

    return render(request, 'resume/create_resume.html', {'form': form})

def resume_templates(request):
    # View to display available resume templates
    return render(request, 'NextGenCV/ResumeTemplates.html')
