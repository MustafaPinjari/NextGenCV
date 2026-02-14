# Resume Optimization Services - Quick Start Guide

## Overview

The Resume Optimization Services provide AI-powered resume improvement capabilities for NextGenCV v2.0. This guide shows you how to use these services in your views and applications.

## Installation

All services are already installed in `apps/resumes/services/`. No additional dependencies required beyond the existing project requirements.

## Quick Start

### 1. Basic Bullet Point Rewriting

```python
from apps.resumes.services import BulletPointRewriterService

# Rewrite a single bullet point
bullet = "Worked on developing features"
result = BulletPointRewriterService.rewrite_bullet_point(bullet)

if result['changed']:
    print(f"Improved: {result['rewritten']}")
    print(f"Reason: {result['reason']}")
```

### 2. Keyword Injection

```python
from apps.resumes.services import KeywordInjectorService
from apps.analyzer.services import KeywordExtractorService

# Extract keywords from resume and job description
resume_text = "Python developer with web experience"
job_description = "Looking for Python Django developer with React skills"

resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
jd_keywords = KeywordExtractorService.extract_keywords(job_description)
missing_keywords = jd_keywords - resume_keywords

# Inject missing keywords
changes = KeywordInjectorService.inject_keywords(
    resume,
    missing_keywords,
    job_description,
    max_keywords=5
)

print(f"Injected {len(changes)} keywords")
```

### 3. Quantification Suggestions

```python
from apps.resumes.services import QuantificationSuggesterService

# Get suggestions for a bullet point
bullet = "Improved system performance"
result = QuantificationSuggesterService.suggest_quantification(bullet)

print(f"Type: {result['achievement_type']}")
print(f"Suggestions: {result['suggestions']}")
print(f"Example: {result['example']}")
```

### 4. Formatting Standardization

```python
from apps.resumes.services import FormattingStandardizerService

# Standardize all formatting
text = "Work History:\n01/2020 - 12/2022"
result = FormattingStandardizerService.standardize_all(text)

print(f"Standardized: {result['standardized']}")
print(f"Changes made: {len(result['all_changes'])}")
```

### 5. Full Resume Optimization (Recommended)

```python
from apps.resumes.services import ResumeOptimizerService

# Optimize entire resume
result = ResumeOptimizerService.optimize_resume(
    resume,
    job_description,
    options={
        'rewrite_bullets': True,
        'inject_keywords': True,
        'suggest_quantifications': True,
        'standardize_formatting': True,
        'max_keywords': 10
    }
)

# Access results
print(f"Score improved from {result['original_score']} to {result['optimized_score']}")
print(f"Total changes: {result['changes_summary']['total_changes']}")

# Get optimized data
optimized_data = result['optimized_data']
```

## Common Use Cases

### Use Case 1: "Fix My Resume" Feature

```python
def fix_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        job_description = request.POST.get('job_description')
        
        # Run optimization
        result = ResumeOptimizerService.optimize_resume(
            resume,
            job_description
        )
        
        # Store in session for preview
        request.session['optimization_result'] = {
            'original_score': result['original_score'],
            'optimized_score': result['optimized_score'],
            'changes': result['detailed_changes'],
            'optimized_data': result['optimized_data']
        }
        
        return redirect('optimization_preview', resume_id=resume_id)
    
    return render(request, 'fix_resume.html', {'resume': resume})
```

### Use Case 2: Real-time Bullet Point Suggestions

```python
from django.http import JsonResponse

def suggest_bullet_improvement(request):
    bullet = request.GET.get('bullet', '')
    context = request.GET.get('context', '')
    
    result = BulletPointRewriterService.rewrite_bullet_point(bullet, context)
    
    return JsonResponse({
        'original': result['original'],
        'improved': result['rewritten'],
        'changed': result['changed'],
        'reason': result['reason']
    })
```

### Use Case 3: Keyword Gap Analysis

```python
def analyze_keyword_gaps(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    job_description = request.POST.get('job_description')
    
    # Get resume text
    resume_text = get_resume_text(resume)
    
    # Extract keywords
    resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
    jd_keywords = KeywordExtractorService.extract_keywords(job_description)
    
    # Find gaps
    missing_keywords = jd_keywords - resume_keywords
    matched_keywords = resume_keywords & jd_keywords
    
    # Prioritize missing keywords
    priorities = KeywordInjectorService.calculate_keyword_priority(
        missing_keywords,
        job_description
    )
    
    return render(request, 'keyword_analysis.html', {
        'matched': matched_keywords,
        'missing': priorities[:10],  # Top 10
        'match_percentage': len(matched_keywords) / len(jd_keywords) * 100
    })
```

### Use Case 4: Quantification Coverage Report

```python
def quantification_report(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    reports = []
    for experience in resume.experiences.all():
        analysis = QuantificationSuggesterService.analyze_experience_quantification(
            experience.description
        )
        
        reports.append({
            'company': experience.company,
            'role': experience.role,
            'coverage': analysis['coverage_percentage'],
            'suggestions': analysis['suggestions']
        })
    
    return render(request, 'quantification_report.html', {
        'reports': reports
    })
```

## Integration with Views

### Example: Optimization Preview View

```python
def optimization_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get optimization result from session
    result = request.session.get('optimization_result')
    
    if not result:
        return redirect('fix_resume', resume_id=resume_id)
    
    # Organize changes by type
    changes_by_type = {
        'bullet_rewrites': [],
        'keyword_injections': [],
        'quantifications': [],
        'formatting': []
    }
    
    for change in result['changes']:
        if change['type'] == 'bullet_rewrite':
            changes_by_type['bullet_rewrites'].append(change)
        elif change['type'] == 'keyword_injection':
            changes_by_type['keyword_injections'].append(change)
        elif change['type'] == 'quantification_suggestion':
            changes_by_type['quantifications'].append(change)
        elif change['type'] == 'formatting_standardization':
            changes_by_type['formatting'].append(change)
    
    context = {
        'resume': resume,
        'original_score': result['original_score'],
        'optimized_score': result['optimized_score'],
        'improvement': result['optimized_score'] - result['original_score'],
        'changes': changes_by_type,
        'optimized_data': result['optimized_data']
    }
    
    return render(request, 'optimization_preview.html', context)
```

### Example: Accept Optimization

```python
from apps.resumes.services import VersionService

def accept_optimization(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Get optimization result from session
    result = request.session.get('optimization_result')
    
    if not result:
        return redirect('resume_detail', resume_id=resume_id)
    
    # Create new version with optimized data
    version = VersionService.create_version(resume, 'optimized')
    
    # Apply optimized data to resume
    optimized_data = result['optimized_data']
    
    # Update experiences
    for exp_data in optimized_data['experiences']:
        experience = resume.experiences.get(company=exp_data['company'])
        experience.description = exp_data['description']
        experience.save()
    
    # Add new skills from keyword injections
    for skill_data in optimized_data['skills']:
        if not resume.skills.filter(name=skill_data['name']).exists():
            resume.skills.create(
                name=skill_data['name'],
                proficiency=skill_data['proficiency']
            )
    
    # Create optimization history record
    OptimizationHistory.objects.create(
        resume=resume,
        original_version=version,
        original_score=result['original_score'],
        optimized_score=result['optimized_score'],
        improvement_delta=result['optimized_score'] - result['original_score'],
        changes_summary=result['changes_summary'],
        detailed_changes=result['changes']
    )
    
    # Clear session
    del request.session['optimization_result']
    
    messages.success(request, f"Resume optimized! Score improved by {result['improvement']:.1f} points.")
    return redirect('resume_detail', resume_id=resume_id)
```

## API Endpoints (REST API)

### Example API View

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def api_optimize_resume(request, resume_id):
    """
    API endpoint for resume optimization
    
    POST /api/resumes/{id}/optimize/
    Body: {
        "job_description": "...",
        "options": {
            "rewrite_bullets": true,
            "inject_keywords": true,
            "max_keywords": 10
        }
    }
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    job_description = request.data.get('job_description')
    options = request.data.get('options', {})
    
    if not job_description:
        return Response(
            {'error': 'job_description is required'},
            status=400
        )
    
    # Run optimization
    result = ResumeOptimizerService.optimize_resume(
        resume,
        job_description,
        options
    )
    
    return Response({
        'success': True,
        'original_score': result['original_score'],
        'optimized_score': result['optimized_score'],
        'improvement_delta': result['improvement_delta'],
        'changes_summary': result['changes_summary'],
        'detailed_changes': result['detailed_changes'][:20],  # Limit for API
        'optimized_data': result['optimized_data']
    })
```

## Testing Your Integration

### Unit Test Example

```python
from django.test import TestCase
from apps.resumes.services import BulletPointRewriterService

class BulletRewriterTest(TestCase):
    def test_weak_verb_replacement(self):
        bullet = "Worked on developing features"
        result = BulletPointRewriterService.rewrite_bullet_point(bullet)
        
        self.assertTrue(result['changed'])
        self.assertNotIn('worked on', result['rewritten'].lower())
        self.assertTrue(
            BulletPointRewriterService.starts_with_action_verb(
                result['rewritten']
            )
        )
```

### Integration Test Example

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.resumes.models import Resume, Experience

class OptimizationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.client.login(username='test', password='pass')
        
        self.resume = Resume.objects.create(
            user=self.user,
            title='Test Resume'
        )
        
        Experience.objects.create(
            resume=self.resume,
            company='Test Corp',
            role='Developer',
            description='Worked on projects'
        )
    
    def test_full_optimization_flow(self):
        # Submit job description
        response = self.client.post(
            f'/resumes/{self.resume.id}/fix/',
            {'job_description': 'Python Django developer needed'}
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check session has optimization result
        session = self.client.session
        self.assertIn('optimization_result', session)
        
        # Preview optimization
        response = self.client.get(
            f'/resumes/{self.resume.id}/fix/preview/'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('optimized_score', response.context)
```

## Performance Tips

1. **Batch Operations**: Use batch methods when processing multiple items
   ```python
   # Good
   results = BulletPointRewriterService.rewrite_multiple_bullets(bullets)
   
   # Avoid
   results = [BulletPointRewriterService.rewrite_bullet_point(b) for b in bullets]
   ```

2. **Caching**: Cache job description keyword extraction
   ```python
   from django.core.cache import cache
   
   cache_key = f'jd_keywords_{hash(job_description)}'
   jd_keywords = cache.get(cache_key)
   
   if not jd_keywords:
       jd_keywords = KeywordExtractorService.extract_keywords(job_description)
       cache.set(cache_key, jd_keywords, 300)  # 5 minutes
   ```

3. **Async Processing**: For large resumes, consider async processing
   ```python
   from celery import shared_task
   
   @shared_task
   def optimize_resume_async(resume_id, job_description):
       resume = Resume.objects.get(id=resume_id)
       result = ResumeOptimizerService.optimize_resume(resume, job_description)
       # Store result in database or cache
       return result
   ```

## Troubleshooting

### Common Issues

1. **Empty Results**: Ensure resume has content
   ```python
   if not resume.experiences.exists():
       messages.warning(request, "Add experience entries before optimizing")
   ```

2. **Low Improvement**: Check if resume already has strong content
   ```python
   if result['improvement_delta'] < 5:
       messages.info(request, "Your resume is already well-optimized!")
   ```

3. **Too Many Changes**: Limit changes for better user experience
   ```python
   options = {
       'max_keywords': 5,  # Limit keyword injections
       'rewrite_bullets': True,
       'suggest_quantifications': False  # Disable if too many
   }
   ```

## Support

For questions or issues:
1. Check the main README in `apps/resumes/services/README.md`
2. Review test files: `test_optimization_services.py` and `test_resume_optimizer_full.py`
3. Consult the design document: `.kiro/specs/nextgencv-v2-advanced/design.md`

## Next Steps

1. Implement views for optimization flow (Task 8 in tasks.md)
2. Create templates for optimization preview (Task 12 in tasks.md)
3. Add optimization history tracking (Task 6 in tasks.md)
4. Integrate with analytics dashboard (Task 10 in tasks.md)
