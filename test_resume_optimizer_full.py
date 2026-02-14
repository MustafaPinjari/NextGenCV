#!/usr/bin/env python
"""
Full integration test for ResumeOptimizerService with mock resume
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.resumes.services import ResumeOptimizerService
from apps.resumes.models import Resume, Experience, Education, Skill, Project, PersonalInfo
from django.contrib.auth.models import User

class MockResume:
    """Mock resume object for testing"""
    def __init__(self):
        self.id = 1
        self.title = "Software Engineer Resume"
        
        # Mock personal info
        self.personal_info = type('obj', (object,), {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'location': 'San Francisco, CA'
        })()
        
        # Mock experiences
        exp1 = type('obj', (object,), {
            'id': 1,
            'company': 'Tech Corp',
            'role': 'Software Engineer',
            'start_date': '2020-01-01',
            'end_date': '2022-12-31',
            'location': 'San Francisco',
            'description': """Worked on developing web applications
Led team meetings
Improved system performance
Responsible for code reviews"""
        })()
        
        exp2 = type('obj', (object,), {
            'id': 2,
            'company': 'StartupXYZ',
            'role': 'Junior Developer',
            'start_date': '2018-06-01',
            'end_date': '2019-12-31',
            'location': 'Remote',
            'description': """Helped with frontend development
Made improvements to the codebase
Worked on bug fixes"""
        })()
        
        self._experiences = [exp1, exp2]
        
        # Mock education
        edu1 = type('obj', (object,), {
            'institution': 'University of California',
            'degree': 'Bachelor of Science',
            'field': 'Computer Science',
            'start_date': '2014-09-01',
            'end_date': '2018-05-31',
            'gpa': '3.8'
        })()
        
        self._education = [edu1]
        
        # Mock skills
        skill1 = type('obj', (object,), {'name': 'JavaScript', 'proficiency': 'Advanced'})()
        skill2 = type('obj', (object,), {'name': 'HTML', 'proficiency': 'Advanced'})()
        skill3 = type('obj', (object,), {'name': 'CSS', 'proficiency': 'Intermediate'})()
        
        self._skills = [skill1, skill2, skill3]
        
        # Mock projects
        proj1 = type('obj', (object,), {
            'name': 'E-commerce Platform',
            'description': 'Built an online shopping platform',
            'technologies': 'React, Node.js, MongoDB',
            'url': 'https://example.com'
        })()
        
        self._projects = [proj1]
    
    class MockQuerySet:
        def __init__(self, items):
            self.items = items
        
        def all(self):
            return self.items
        
        def exists(self):
            return len(self.items) > 0
        
        def count(self):
            return len(self.items)
    
    @property
    def experiences(self):
        return self.MockQuerySet(self._experiences)
    
    @property
    def education(self):
        return self.MockQuerySet(self._education)
    
    @property
    def skills(self):
        return self.MockQuerySet(self._skills)
    
    @property
    def projects(self):
        return self.MockQuerySet(self._projects)

def test_full_optimization():
    print("\n" + "="*60)
    print("FULL RESUME OPTIMIZATION TEST")
    print("="*60)
    
    # Create mock resume
    resume = MockResume()
    
    # Job description
    job_description = """
    We are looking for a Senior Software Engineer with strong Python and Django experience.
    The ideal candidate should have:
    - 5+ years of experience with Python and Django
    - Experience with React and modern JavaScript frameworks
    - Strong understanding of RESTful APIs and microservices
    - Experience with PostgreSQL and database optimization
    - Knowledge of Docker and Kubernetes
    - Agile/Scrum methodology experience
    - Strong problem-solving skills
    
    Responsibilities:
    - Design and develop scalable web applications
    - Lead technical discussions and code reviews
    - Mentor junior developers
    - Optimize application performance
    - Collaborate with cross-functional teams
    """
    
    print("\n📋 Original Resume Summary:")
    print(f"   - Experiences: {resume.experiences.count()}")
    print(f"   - Skills: {resume.skills.count()}")
    print(f"   - Education: {resume.education.count()}")
    print(f"   - Projects: {resume.projects.count()}")
    
    print("\n🎯 Job Description Keywords:")
    from apps.analyzer.services import KeywordExtractorService
    jd_keywords = KeywordExtractorService.extract_keywords(job_description)
    print(f"   Found {len(jd_keywords)} keywords")
    print(f"   Top keywords: {list(jd_keywords)[:10]}")
    
    print("\n🔄 Running Optimization...")
    
    # Run optimization
    result = ResumeOptimizerService.optimize_resume(
        resume,
        job_description,
        options={
            'rewrite_bullets': True,
            'inject_keywords': True,
            'suggest_quantifications': True,
            'standardize_formatting': True,
            'max_keywords': 8
        }
    )
    
    print("\n📊 OPTIMIZATION RESULTS:")
    print("="*60)
    
    print(f"\n📈 Score Improvement:")
    print(f"   Original Score:  {result['original_score']:.2f}")
    print(f"   Optimized Score: {result['optimized_score']:.2f}")
    print(f"   Improvement:     +{result['improvement_delta']:.2f} points")
    
    print(f"\n📝 Changes Summary:")
    summary = result['changes_summary']
    print(f"   Bullet Rewrites:           {summary['bullet_rewrites']}")
    print(f"   Keyword Injections:        {summary['keyword_injections']}")
    print(f"   Quantification Suggestions: {summary['quantification_suggestions']}")
    print(f"   Formatting Fixes:          {summary['formatting_fixes']}")
    print(f"   TOTAL CHANGES:             {summary['total_changes']}")
    
    print(f"\n🔍 Detailed Changes:")
    print("-"*60)
    
    # Show bullet rewrites
    bullet_changes = [c for c in result['detailed_changes'] if c['type'] == 'bullet_rewrite']
    if bullet_changes:
        print(f"\n✏️  Bullet Point Rewrites ({len(bullet_changes)}):")
        for i, change in enumerate(bullet_changes[:5], 1):  # Show first 5
            print(f"\n   {i}. {change['company']} - {change['role']}")
            print(f"      OLD: {change['old_text']}")
            print(f"      NEW: {change['new_text']}")
            print(f"      Reason: {change['reason']}")
    
    # Show keyword injections
    keyword_changes = [c for c in result['detailed_changes'] if c['type'] == 'keyword_injection']
    if keyword_changes:
        print(f"\n🔑 Keyword Injections ({len(keyword_changes)}):")
        for i, change in enumerate(keyword_changes[:5], 1):  # Show first 5
            print(f"\n   {i}. Keyword: '{change['keyword']}'")
            print(f"      Location: {change['location']}")
            print(f"      Frequency in JD: {change['frequency']}")
            print(f"      Injection: {change['new_text'][:100]}...")
    
    # Show quantification suggestions
    quant_changes = [c for c in result['detailed_changes'] if c['type'] == 'quantification_suggestion']
    if quant_changes:
        print(f"\n📊 Quantification Suggestions ({len(quant_changes)}):")
        for i, change in enumerate(quant_changes[:5], 1):  # Show first 5
            print(f"\n   {i}. {change['company']} - {change['role']}")
            print(f"      Original: {change['old_text']}")
            print(f"      Suggested: {change['suggested_text']}")
            print(f"      Type: {change['achievement_type']}")
    
    # Show formatting fixes
    format_changes = [c for c in result['detailed_changes'] if c['type'] == 'formatting_standardization']
    if format_changes:
        print(f"\n🎨 Formatting Standardizations ({len(format_changes)}):")
        for i, change in enumerate(format_changes[:3], 1):  # Show first 3
            print(f"\n   {i}. {change['section']}")
            print(f"      Changes: {len(change['specific_changes'])} formatting fixes")
    
    print("\n" + "="*60)
    print("✅ OPTIMIZATION COMPLETE!")
    print("="*60)
    
    # Verify optimized data structure
    print("\n🔍 Verifying Optimized Data Structure...")
    optimized = result['optimized_data']
    
    assert 'personal_info' in optimized
    assert 'experiences' in optimized
    assert 'education' in optimized
    assert 'skills' in optimized
    assert 'projects' in optimized
    
    print(f"   ✓ Personal Info: {optimized['personal_info']['full_name']}")
    print(f"   ✓ Experiences: {len(optimized['experiences'])} entries")
    print(f"   ✓ Education: {len(optimized['education'])} entries")
    print(f"   ✓ Skills: {len(optimized['skills'])} entries")
    print(f"   ✓ Projects: {len(optimized['projects'])} entries")
    
    print("\n✅ All verifications passed!")
    
    return result

if __name__ == '__main__':
    try:
        result = test_full_optimization()
        print("\n" + "🎉"*20)
        print("SUCCESS! ResumeOptimizerService is fully functional!")
        print("🎉"*20)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
