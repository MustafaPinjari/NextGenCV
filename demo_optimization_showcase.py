#!/usr/bin/env python
"""
Showcase demonstration of all optimization services
Demonstrates the full capabilities of the Resume Optimization system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.resumes.services import (
    BulletPointRewriterService,
    KeywordInjectorService,
    QuantificationSuggesterService,
    FormattingStandardizerService,
    ResumeOptimizerService
)

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def demo_bullet_rewriter():
    print_section("1. BULLET POINT REWRITER DEMO")
    
    examples = [
        ("Worked on developing web applications", "web development"),
        ("Responsible for managing a team of developers", "team management"),
        ("Helped with code reviews and testing", "code quality"),
        ("Made improvements to system performance", "performance optimization"),
        ("Did data analysis for business insights", "data analytics")
    ]
    
    print("\n📝 Rewriting weak bullet points with strong action verbs:\n")
    
    for i, (bullet, context) in enumerate(examples, 1):
        result = BulletPointRewriterService.rewrite_bullet_point(bullet, context)
        
        print(f"{i}. Context: {context}")
        print(f"   ❌ Before: {result['original']}")
        print(f"   ✅ After:  {result['rewritten']}")
        print(f"   💡 Reason: {result['reason']}\n")

def demo_keyword_injector():
    print_section("2. KEYWORD INJECTOR DEMO")
    
    print("\n🔑 Injecting missing keywords naturally:\n")
    
    # Demonstrate keyword classification
    keywords = ['Python', 'Agile', 'Docker', 'Jira', 'Machine Learning']
    print("Keyword Classification:")
    for keyword in keywords:
        classification = KeywordInjectorService._classify_keyword(keyword)
        print(f"   • {keyword:20} → {classification}")
    
    # Demonstrate natural injection
    print("\n📝 Natural Injection Examples:")
    
    examples = [
        ("Developed backend services", "Django", "technology"),
        ("Managed project workflows", "Scrum", "methodology"),
        ("Collaborated with team", "Slack", "tool"),
        ("Built data pipelines", "Apache Spark", "technology")
    ]
    
    for i, (text, keyword, injection_type) in enumerate(examples, 1):
        injected = KeywordInjectorService.inject_keyword_naturally(
            text, keyword, injection_type
        )
        print(f"\n   {i}. Keyword: '{keyword}' (Type: {injection_type})")
        print(f"      Original: {text}")
        print(f"      Injected: {injected}")

def demo_quantification_suggester():
    print_section("3. QUANTIFICATION SUGGESTER DEMO")
    
    print("\n📊 Suggesting metrics for unquantified achievements:\n")
    
    examples = [
        "Improved system performance",
        "Led a team of developers",
        "Reduced operational costs",
        "Increased customer satisfaction",
        "Automated manual processes",
        "Developed new features",
        "Managed multiple projects"
    ]
    
    for i, bullet in enumerate(examples, 1):
        result = QuantificationSuggesterService.suggest_quantification(bullet)
        
        print(f"{i}. Achievement Type: {result['achievement_type']}")
        print(f"   Original: {result['original']}")
        print(f"   Suggestions: {', '.join(result['suggestions'][:3])}")
        print(f"   Example: {result['example']}\n")

def demo_formatting_standardizer():
    print_section("4. FORMATTING STANDARDIZER DEMO")
    
    print("\n🎨 Standardizing resume formatting for ATS compatibility:\n")
    
    # Section headings
    print("1. Section Heading Standardization:")
    headings = [
        "Work History:",
        "Employment:",
        "Technical Skills:",
        "Schooling:",
        "Professional Experience:"
    ]
    
    for heading in headings:
        result = FormattingStandardizerService.standardize_section_headings(heading)
        if result['changes']:
            change = result['changes'][0]
            print(f"   {change['old']:25} → {change['new']}")
    
    # Date formats
    print("\n2. Date Format Standardization:")
    dates = [
        "01/2020 - 12/2022",
        "2019-06 to 2020-12",
        "03-2018 - 05-2021"
    ]
    
    for date in dates:
        result = FormattingStandardizerService.standardize_date_formats(date)
        print(f"   {date:25} → {result['standardized']}")
    
    # Problematic formatting
    print("\n3. Problematic Formatting Removal:")
    problems = [
        ("Multiple    spaces", "Excessive whitespace"),
        ("Text\twith\ttabs", "Tab characters"),
        ("Smart "quotes" here", "Smart quotes"),
        ("Em—dash—usage", "Em dashes")
    ]
    
    for text, issue in problems:
        result = FormattingStandardizerService.remove_problematic_formatting(text)
        print(f"   Issue: {issue}")
        print(f"   Before: {text}")
        print(f"   After:  {result['cleaned']}\n")

def demo_full_optimization():
    print_section("5. FULL OPTIMIZATION ORCHESTRATION DEMO")
    
    print("\n🚀 Complete resume optimization pipeline:\n")
    
    # Create a simple mock resume
    class SimpleResume:
        def __init__(self):
            self.personal_info = type('obj', (object,), {
                'full_name': 'Jane Developer',
                'email': 'jane@example.com',
                'phone': '555-0123',
                'location': 'Seattle, WA'
            })()
            
            exp = type('obj', (object,), {
                'company': 'Tech Startup',
                'role': 'Software Developer',
                'description': 'Worked on web applications\nHelped with code reviews\nImproved performance'
            })()
            
            self._experiences = [exp]
            self._skills = [
                type('obj', (object,), {'name': 'JavaScript', 'proficiency': 'Advanced'})()
            ]
            self._education = []
            self._projects = []
        
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
        def skills(self):
            return self.MockQuerySet(self._skills)
        @property
        def education(self):
            return self.MockQuerySet(self._education)
        @property
        def projects(self):
            return self.MockQuerySet(self._projects)
    
    resume = SimpleResume()
    job_description = """
    Senior Python Developer needed with Django and React experience.
    Must have strong problem-solving skills and experience with PostgreSQL.
    """
    
    print("📋 Original Resume:")
    print(f"   Company: {resume.experiences.all()[0].company}")
    print(f"   Role: {resume.experiences.all()[0].role}")
    print(f"   Description: {resume.experiences.all()[0].description}")
    print(f"   Skills: {resume.skills.count()}")
    
    print("\n🔄 Running optimization...")
    
    result = ResumeOptimizerService.optimize_resume(
        resume,
        job_description,
        options={'max_keywords': 5}
    )
    
    print("\n📊 RESULTS:")
    print(f"   Original Score:  {result['original_score']:.1f}")
    print(f"   Optimized Score: {result['optimized_score']:.1f}")
    print(f"   Improvement:     +{result['improvement_delta']:.1f} points")
    
    print("\n📝 Changes Made:")
    summary = result['changes_summary']
    print(f"   • Bullet Rewrites:      {summary['bullet_rewrites']}")
    print(f"   • Keyword Injections:   {summary['keyword_injections']}")
    print(f"   • Quantifications:      {summary['quantification_suggestions']}")
    print(f"   • Formatting Fixes:     {summary['formatting_fixes']}")
    print(f"   • TOTAL:                {summary['total_changes']}")
    
    if result['detailed_changes']:
        print("\n🔍 Sample Changes:")
        for i, change in enumerate(result['detailed_changes'][:3], 1):
            print(f"\n   {i}. Type: {change['type']}")
            if 'old_text' in change:
                print(f"      Before: {change['old_text'][:60]}...")
                if 'new_text' in change:
                    print(f"      After:  {change['new_text'][:60]}...")

def main():
    print("\n" + "🎯"*35)
    print("  RESUME OPTIMIZATION SERVICES - COMPLETE SHOWCASE")
    print("🎯"*35)
    
    print("\nThis demonstration showcases all 5 optimization services:")
    print("  1. BulletPointRewriterService")
    print("  2. KeywordInjectorService")
    print("  3. QuantificationSuggesterService")
    print("  4. FormattingStandardizerService")
    print("  5. ResumeOptimizerService (Orchestrator)")
    
    try:
        demo_bullet_rewriter()
        input("\nPress Enter to continue to Keyword Injector demo...")
        
        demo_keyword_injector()
        input("\nPress Enter to continue to Quantification Suggester demo...")
        
        demo_quantification_suggester()
        input("\nPress Enter to continue to Formatting Standardizer demo...")
        
        demo_formatting_standardizer()
        input("\nPress Enter to continue to Full Optimization demo...")
        
        demo_full_optimization()
        
        print("\n" + "="*70)
        print("  ✅ DEMONSTRATION COMPLETE!")
        print("="*70)
        print("\n🎉 All optimization services are fully functional and ready to use!")
        print("\n📚 For more information:")
        print("   • Service Documentation: apps/resumes/services/README.md")
        print("   • Quick Start Guide: OPTIMIZATION_SERVICES_GUIDE.md")
        print("   • Implementation Summary: TASK_5_IMPLEMENTATION_SUMMARY.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
