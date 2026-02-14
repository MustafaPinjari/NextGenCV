#!/usr/bin/env python
"""
Demo script showing NLP and Scoring services in action
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analyzer.services import (
    KeywordExtractorService,
    ActionVerbAnalyzerService,
    QuantificationDetectorService,
    ScoringEngineService
)

def demo():
    print("\n" + "="*70)
    print("NextGenCV v2.0 - NLP and Scoring Services Demo")
    print("="*70 + "\n")
    
    # Sample resume text
    resume_text = """
    Senior Software Engineer with 5+ years of experience in Python and Django.
    
    Experience:
    • Led team of 8 developers to build scalable web application
    • Implemented CI/CD pipeline reducing deployment time by 50%
    • Increased code coverage from 60% to 90%
    • Developed RESTful APIs serving 1M+ requests per day
    • Reduced server costs by $50K annually through optimization
    
    Skills: Python, Django, PostgreSQL, AWS, Docker, React
    """
    
    job_description = """
    We're looking for a Senior Python Developer with strong Django experience.
    Requirements:
    - 5+ years of software development
    - Expert in Python, Django, PostgreSQL
    - Experience with cloud platforms (AWS preferred)
    - Strong leadership and team collaboration skills
    - Track record of delivering scalable solutions
    """
    
    print("📄 Sample Resume Text:")
    print("-" * 70)
    print(resume_text.strip())
    print()
    
    print("📋 Job Description:")
    print("-" * 70)
    print(job_description.strip())
    print("\n" + "="*70 + "\n")
    
    # 1. Keyword Extraction
    print("🔍 KEYWORD EXTRACTION")
    print("-" * 70)
    resume_keywords = KeywordExtractorService.extract_keywords(resume_text)
    jd_keywords = KeywordExtractorService.extract_keywords(job_description)
    
    print(f"Resume Keywords ({len(resume_keywords)}):")
    print(f"  {', '.join(list(resume_keywords)[:10])}")
    print(f"\nJob Description Keywords ({len(jd_keywords)}):")
    print(f"  {', '.join(list(jd_keywords)[:10])}")
    
    matched = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords
    print(f"\n✓ Matched Keywords ({len(matched)}): {', '.join(list(matched)[:5])}")
    print(f"✗ Missing Keywords ({len(missing)}): {', '.join(list(missing)[:5])}")
    
    # 2. Action Verb Analysis
    print("\n" + "="*70 + "\n")
    print("💪 ACTION VERB ANALYSIS")
    print("-" * 70)
    verb_analysis = ActionVerbAnalyzerService.analyze_action_verbs(resume_text)
    print(f"Strong Action Verbs: {', '.join(verb_analysis['strong_verbs'])}")
    print(f"Weak Verbs: {', '.join(verb_analysis['weak_verbs']) if verb_analysis['weak_verbs'] else 'None'}")
    print(f"Action Verb Score: {ActionVerbAnalyzerService.calculate_action_verb_score(resume_text)}/100")
    
    # 3. Quantification Detection
    print("\n" + "="*70 + "\n")
    print("📊 QUANTIFICATION DETECTION")
    print("-" * 70)
    quants = QuantificationDetectorService.detect_quantifications(resume_text)
    summary = QuantificationDetectorService.get_quantification_summary(resume_text)
    print(f"Total Quantifications: {summary['total_quantifications']}")
    print(f"By Type: {summary['by_type']}")
    print(f"Quantification Score: {QuantificationDetectorService.calculate_quantification_score(resume_text)}/100")
    print(f"\nDetected Quantifications:")
    for q in quants[:5]:
        print(f"  • {q['type']}: {q['value']}")
    
    # 4. Comprehensive Scoring (with mock resume)
    print("\n" + "="*70 + "\n")
    print("🎯 COMPREHENSIVE ATS SCORING")
    print("-" * 70)
    
    # Create mock resume
    class MockPersonalInfo:
        full_name = "John Doe"
        email = "john@example.com"
        phone = "555-1234"
        location = "San Francisco, CA"
    
    class MockExperience:
        company = "Tech Corp"
        role = "Senior Software Engineer"
        description = resume_text
    
    class MockSkill:
        name = "Python"
    
    class MockQuerySet:
        def __init__(self, items):
            self._items = items
        def all(self):
            return self._items
        def exists(self):
            return len(self._items) > 0
        def count(self):
            return len(self._items)
    
    class MockResume:
        personal_info = MockPersonalInfo()
        experiences = MockQuerySet([MockExperience()])
        education = MockQuerySet([])
        skills = MockQuerySet([MockSkill()])
        projects = MockQuerySet([])
    
    result = ScoringEngineService.calculate_ats_score(MockResume(), job_description)
    
    print(f"🏆 FINAL ATS SCORE: {result['final_score']}/100")
    print(f"\n📈 Component Scores:")
    print(f"  • Keyword Match:        {result['keyword_match_score']}/100 (30% weight)")
    print(f"  • Skill Relevance:      {result['skill_relevance_score']}/100 (20% weight)")
    print(f"  • Section Completeness: {result['section_completeness_score']}/100 (15% weight)")
    print(f"  • Experience Impact:    {result['experience_impact_score']}/100 (15% weight)")
    print(f"  • Quantification:       {result['quantification_score']}/100 (10% weight)")
    print(f"  • Action Verb Strength: {result['action_verb_score']}/100 (10% weight)")
    
    print(f"\n✓ Matched Keywords: {', '.join(result['matched_keywords'][:5])}")
    print(f"✗ Missing Keywords: {', '.join(result['missing_keywords'][:5])}")
    
    print("\n" + "="*70)
    print("✅ Demo Complete! All services working correctly.")
    print("="*70 + "\n")

if __name__ == '__main__':
    demo()
