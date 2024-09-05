# resume/views.py
from django.shortcuts import render, redirect
from .forms import ResumeForm
from django.contrib.auth.decorators import login_required
from .models import Resume

@login_required
def create_resume_view(request):
    # Check if the user already has a resume
    existing_resume = Resume.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=existing_resume)  # Load existing data if present
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user  # Link the resume to the logged-in user
            resume.save()
            return redirect('NextGenCV/dashboard.html')  # Redirect to the dashboard or another page after saving
    else:
        form = ResumeForm(instance=existing_resume)  # Load existing data if present

    return render(request, 'resume/create_resume.html', {'form': form})
