"""
Views for Resume A/B Testing feature.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from apps.resumes.models import Resume
from apps.resumes.ab_testing import ResumeABTest


@login_required
def ab_test_list(request):
    """List all A/B tests for the current user."""
    tests = ResumeABTest.objects.filter(user=request.user).select_related('resume_a', 'resume_b')
    tests_with_stats = [(t, t.get_stats()) for t in tests]
    return render(request, 'resumes/ab_test_list.html', {
        'tests_with_stats': tests_with_stats,
    })


@login_required
def ab_test_create(request):
    """Create a new A/B test."""
    resumes = Resume.objects.filter(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        target_role = request.POST.get('target_role', '').strip()
        target_company = request.POST.get('target_company', '').strip()
        job_description = request.POST.get('job_description', '').strip()
        resume_a_id = request.POST.get('resume_a')
        resume_b_id = request.POST.get('resume_b')
        hypothesis = request.POST.get('hypothesis', '').strip()

        if not all([name, target_role, resume_a_id, resume_b_id]):
            messages.error(request, 'Name, target role, and both resume variants are required.')
            return render(request, 'resumes/ab_test_create.html', {'resumes': resumes})

        if resume_a_id == resume_b_id:
            messages.error(request, 'Please select two different resumes.')
            return render(request, 'resumes/ab_test_create.html', {'resumes': resumes})

        resume_a = get_object_or_404(Resume, id=resume_a_id, user=request.user)
        resume_b = get_object_or_404(Resume, id=resume_b_id, user=request.user)

        test = ResumeABTest.objects.create(
            user=request.user,
            name=name,
            target_role=target_role,
            target_company=target_company,
            job_description=job_description,
            resume_a=resume_a,
            resume_b=resume_b,
            hypothesis=hypothesis,
        )
        messages.success(request, f'A/B test "{name}" created. Apply with both resumes and track results!')
        return redirect('ab_test_detail', pk=test.pk)

    return render(request, 'resumes/ab_test_create.html', {'resumes': resumes})


@login_required
def ab_test_detail(request, pk):
    """View A/B test details and live stats."""
    test = get_object_or_404(ResumeABTest, pk=pk, user=request.user)
    stats = test.get_stats()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(stats)

    return render(request, 'resumes/ab_test_detail.html', {
        'test': test,
        'stats': stats,
    })


@login_required
def ab_test_conclude(request, pk):
    """Conclude an A/B test and declare a winner."""
    test = get_object_or_404(ResumeABTest, pk=pk, user=request.user)

    if request.method == 'POST':
        winner = request.POST.get('winner', '').upper()
        notes = request.POST.get('conclusion_notes', '').strip()

        if winner not in ('A', 'B'):
            messages.error(request, 'Please select a winner (A or B).')
            return redirect('ab_test_detail', pk=pk)

        test.status = 'concluded'
        test.winner = winner
        test.conclusion_notes = notes
        test.concluded_at = timezone.now()
        test.save()

        messages.success(request, f'A/B test concluded. Resume {winner} declared the winner!')
        return redirect('ab_test_detail', pk=pk)

    return redirect('ab_test_detail', pk=pk)


@login_required
def ab_test_delete(request, pk):
    """Delete an A/B test."""
    test = get_object_or_404(ResumeABTest, pk=pk, user=request.user)
    if request.method == 'POST':
        test.delete()
        messages.success(request, 'A/B test deleted.')
        return redirect('ab_test_list')
    return render(request, 'resumes/ab_test_confirm_delete.html', {'test': test})
