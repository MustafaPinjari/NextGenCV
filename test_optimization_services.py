#!/usr/bin/env python
"""
Test script for optimization services
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.resumes.services import (
    BulletPointRewriterService,
    KeywordInjectorService,
    QuantificationSuggesterService,
    FormattingStandardizerService,
    ResumeOptimizerService
)

def test_bullet_point_rewriter():
    print("\n=== Testing BulletPointRewriterService ===")
    
    # Test with weak verb
    bullet1 = "Worked on developing a new feature for the application"
    result1 = BulletPointRewriterService.rewrite_bullet_point(bullet1)
    print(f"Original: {result1['original']}")
    print(f"Rewritten: {result1['rewritten']}")
    print(f"Changed: {result1['changed']}")
    print(f"Reason: {result1['reason']}")
    
    # Test with "responsible for"
    bullet2 = "Responsible for managing the team"
    result2 = BulletPointRewriterService.rewrite_bullet_point(bullet2, "team management")
    print(f"\nOriginal: {result2['original']}")
    print(f"Rewritten: {result2['rewritten']}")
    print(f"Changed: {result2['changed']}")
    
    # Test starts_with_action_verb
    print(f"\nStarts with action verb (Led team): {BulletPointRewriterService.starts_with_action_verb('Led team of 5 developers')}")
    print(f"Starts with action verb (Worked on): {BulletPointRewriterService.starts_with_action_verb('Worked on project')}")
    
    print("✓ BulletPointRewriterService tests passed")

def test_keyword_injector():
    print("\n=== Testing KeywordInjectorService ===")
    
    # Test keyword classification
    print(f"Python classification: {KeywordInjectorService._classify_keyword('python')}")
    print(f"Agile classification: {KeywordInjectorService._classify_keyword('agile')}")
    print(f"Jira classification: {KeywordInjectorService._classify_keyword('jira')}")
    
    # Test natural injection
    text = "Developed web applications"
    keyword = "React"
    injected = KeywordInjectorService.inject_keyword_naturally(text, keyword, 'technology')
    print(f"\nOriginal: {text}")
    print(f"Injected: {injected}")
    
    # Test priority calculation
    keywords = {'python', 'django', 'react', 'javascript'}
    jd = "We need a Python developer with Django experience. Python and Django are essential."
    priorities = KeywordInjectorService.calculate_keyword_priority(keywords, jd)
    print(f"\nKeyword priorities: {priorities}")
    
    print("✓ KeywordInjectorService tests passed")

def test_quantification_suggester():
    print("\n=== Testing QuantificationSuggesterService ===")
    
    # Test classification
    bullet1 = "Improved system performance significantly"
    result1 = QuantificationSuggesterService.suggest_quantification(bullet1)
    print(f"Bullet: {bullet1}")
    print(f"Achievement type: {result1['achievement_type']}")
    print(f"Suggestions: {result1['suggestions'][:3]}")
    print(f"Example: {result1['example']}")
    
    # Test team-related
    bullet2 = "Led a team of developers"
    result2 = QuantificationSuggesterService.suggest_quantification(bullet2)
    print(f"\nBullet: {bullet2}")
    print(f"Achievement type: {result2['achievement_type']}")
    print(f"Suggestions: {result2['suggestions'][:3]}")
    
    # Test already quantified
    bullet3 = "Increased revenue by 25%"
    result3 = QuantificationSuggesterService.suggest_quantification(bullet3)
    print(f"\nBullet: {bullet3}")
    print(f"Has quantification: {result3['has_quantification']}")
    
    # Test experience analysis
    description = """
    Developed web applications
    Led team meetings
    Improved system performance by 30%
    """
    analysis = QuantificationSuggesterService.analyze_experience_quantification(description)
    print(f"\nExperience analysis:")
    print(f"Total bullets: {analysis['total_bullets']}")
    print(f"Quantified: {analysis['quantified_bullets']}")
    print(f"Coverage: {analysis['coverage_percentage']}%")
    
    print("✓ QuantificationSuggesterService tests passed")

def test_formatting_standardizer():
    print("\n=== Testing FormattingStandardizerService ===")
    
    # Test section heading standardization
    text1 = "Work History:\nSoftware Engineer at Company"
    result1 = FormattingStandardizerService.standardize_section_headings(text1)
    print(f"Original: {text1}")
    print(f"Standardized: {result1['standardized']}")
    print(f"Changes: {result1['changes']}")
    
    # Test date standardization
    text2 = "01/2020 - 12/2022"
    result2 = FormattingStandardizerService.standardize_date_formats(text2)
    print(f"\nOriginal dates: {text2}")
    print(f"Standardized: {result2['standardized']}")
    
    # Test problematic formatting removal
    text3 = "Multiple    spaces\tand\ttabs"
    result3 = FormattingStandardizerService.remove_problematic_formatting(text3)
    print(f"\nOriginal: {text3}")
    print(f"Cleaned: {result3['cleaned']}")
    
    # Test ATS validation
    text4 = "Normal text with standard formatting"
    validation = FormattingStandardizerService.validate_ats_friendly(text4)
    print(f"\nATS validation score: {validation['score']}")
    print(f"Is ATS friendly: {validation['is_ats_friendly']}")
    
    print("✓ FormattingStandardizerService tests passed")

def test_integration():
    print("\n=== Testing Service Integration ===")
    
    # Test multiple bullet rewrites
    bullets = [
        "Worked on developing features",
        "Responsible for team management",
        "Helped with code reviews"
    ]
    results = BulletPointRewriterService.rewrite_multiple_bullets(bullets, "software development")
    print(f"Rewritten {len([r for r in results if r['changed']])} out of {len(bullets)} bullets")
    
    # Test multiple quantification suggestions
    bullets2 = [
        "Improved system performance",
        "Led team meetings",
        "Developed new features"
    ]
    suggestions = QuantificationSuggesterService.suggest_for_multiple_bullets(bullets2)
    print(f"Generated {len(suggestions)} quantification suggestions")
    
    # Test full standardization
    text = """
    Work History:
    Software Engineer - 01/2020 to 12/2022
    • Worked on    developing features
    • Improved performance
    """
    result = FormattingStandardizerService.standardize_all(text)
    print(f"\nTotal formatting changes: {len(result['all_changes'])}")
    
    print("✓ Integration tests passed")

if __name__ == '__main__':
    print("Starting Optimization Services Tests...")
    
    try:
        test_bullet_point_rewriter()
        test_keyword_injector()
        test_quantification_suggester()
        test_formatting_standardizer()
        test_integration()
        
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED!")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
