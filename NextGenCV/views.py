# NextGenCV/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from resume.models import Resume  # Ensure this import is correct

User = get_user_model()

def index(request):
    return render(request, 'NextGenCV/index.html')

def auth_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            # Login logic
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'NextGenCV/auth.html', {'error': 'Invalid credentials', 'mode': 'login'})
        
        elif 'signup' in request.POST:
            # Sign-up logic
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    login(request, user)
                    return redirect('dashboard')
                except:
                    return render(request, 'NextGenCV/auth.html', {'error': 'Username or email already exists', 'mode': 'signup'})
            else:
                return render(request, 'NextGenCV/auth.html', {'error': 'Passwords do not match', 'mode': 'signup'})

    mode = request.GET.get('mode', 'login')
    return render(request, 'NextGenCV/auth.html', {'mode': mode})

def logout_view(request):
    logout(request)
    return redirect('index')

class DashboardView(TemplateView):
    template_name = 'NextGenCV/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Fetch the logged-in user's resume
            resume = Resume.objects.filter(user=self.request.user).first()
            context['resume'] = resume
        return context
