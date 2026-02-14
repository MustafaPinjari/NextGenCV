#!/usr/bin/env python
"""
Demonstration script for VersionService, AnalyticsService, and TrendAnalysisService

This script demonstrates the complete workflow of:
1. Creating resume versions
2. Calculating health scores
3. Analyzing trends
4. Comparing versions
5. Generating improvement reports

Run with: python demo_version_analytics.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.resumes.models import Resume, PersonalInfo, Experience, Education, Skill, ResumeAnalysis
from apps.resumes.services import VersionService
from apps.analytics.services import AnalyticsService, TrendAnalysisService
from datetime import date
from django.utils import timezone


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def main():
    print_section("NextGenCV v2.0 - Version & Analytics Services Demo")
    
    # Get or create demo user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print(f"\n✓ Created demo user: {user.username}")
    else:
        print(f"\n✓ Using existing demo user: {user.username}")
    
    # Create or get demo resume
    resume, created = Resume.objects.get_or_create(
        user=user,
        title='Software Engineer Resume',
        defaults={'template': 'professional'}
    )
    
    if created:
        print(f"✓ Created new resume: {resume.title}")
        
        # Add personal info
        PersonalInfo.objects.create(
            resume=resume,
            full_name='John Doe',
            phone='555-1234',
            email='john.doe@example.com',
            location='San Francisco, CA',
            linkedin='linkedin.com/in/johndoe',
            github='github.com/johndoe'
        )
        
        # Add experience
        Experience.objects.create(
            resume=resume,
            company='Tech Corp',
            role='Senior Software Engineer',
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
            description='Developed web applications\nLed team of 5 developers\nIncreased performance by 40%',
            order=0
        )
        
        # Add education
        Education.objects.create(
            resume=resume,
            institution='Stanford University',
            degree='BS',
            field='Computer Science',
            start_year=2016,
            end_year=2020,
            order=0
        )
        
        # Add skills
        for skill_name, category in [
            ('Python', 'Programming'),
            ('Django', 'Framework'),
            ('JavaScript', 'Programming'),
            ('React', 'Frontend')
        ]:
            Skill.objects.create(resume=resume, name=skill_name, category=category)
    else:
        print(f"✓ Using existing resume: {resume.title}")
    
    # Demo 1: Calculate Initial Health
    print_section("1. Calculate Resume Health")
    initial_health = AnalyticsService.calculate_resume_health(resume)
    print(f"\nInitial Resume Health Score: {initial_health}/100")
    
    if initial_health >= 80:
        print("Status: Excellent ✓")
    elif initial_health >= 60:
        print("Status: Good")
    else:
        print("Status: Needs Improvement")
    
    # Demo 2: Create Initial Version
    print_section("2. Create Initial Version")
    version1 = VersionService.create_version(
        resume=resume,
        modification_type='manual',
        user_notes='Initial version',
        ats_score=initial_health
    )
    print(f"\n✓ Created Version {version1.version_number}")
    print(f"  - Modification Type: {version1.modification_type}")
    print(f"  - ATS Score: {version1.ats_score}")
    print(f"  - Created: {version1.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Demo 3: Simulate Improvements
    print_section("3. Simulate Resume Improvements")
    
    # Add more skills
    print("\nAdding more skills...")
    new_skills = [
        ('PostgreSQL', 'Database'),
        ('Docker', 'DevOps'),
        ('AWS', 'Cloud')
    ]
    for skill_name, category in new_skills:
        Skill.objects.get_or_create(resume=resume, name=skill_name, defaults={'category': category})
    
    # Calculate new health
    improved_health = AnalyticsService.calculate_resume_health(resume)
    print(f"New Health Score: {improved_health}/100")
    print(f"Improvement: +{improved_health - initial_health:.2f} points")
    
    # Create new version
    version2 = VersionService.create_version(
        resume=resume,
        modification_type='manual',
        user_notes='Added technical skills',
        ats_score=improved_health
    )
    print(f"\n✓ Created Version {version2.version_number}")
    
    # Demo 4: Compare Versions
    print_section("4. Compare Versions")
    diff = VersionService.compare_versions(version1, version2)
    
    print(f"\nComparing Version {diff['version1_number']} → Version {diff['version2_number']}")
    print(f"Total Changes: {len(diff['changes'])}")
    
    if diff['changes']:
        print("\nChanges detected:")
        for i, change in enumerate(diff['changes'][:5], 1):  # Show first 5 changes
            if change['type'] == 'added':
                print(f"  {i}. Added {change['section']}: {change.get('item', change.get('field'))}")
            elif change['type'] == 'deleted':
                print(f"  {i}. Deleted {change['section']}: {change.get('item', change.get('field'))}")
            elif change['type'] == 'modified':
                print(f"  {i}. Modified {change['section']}: {change.get('item', change.get('field'))}")
        
        if len(diff['changes']) > 5:
            print(f"  ... and {len(diff['changes']) - 5} more changes")
    else:
        print("\nNo changes detected")
    
    # Demo 5: Create Analyses for Trend Analysis
    print_section("5. Create Sample Analyses for Trend Analysis")
    
    scores = [65.0, 70.0, 75.0, 80.0, 85.0]
    print(f"\nCreating {len(scores)} sample analyses with improving scores...")
    
    for i, score in enumerate(scores):
        ResumeAnalysis.objects.get_or_create(
            resume=resume,
            job_description=f'Sample job description {i+1}',
            defaults={
                'keyword_match_score': score,
                'skill_relevance_score': score,
                'section_completeness_score': score,
                'experience_impact_score': score,
                'quantification_score': score,
                'action_verb_score': score,
                'final_score': score,
                'matched_keywords': ['python', 'django', 'react'],
                'missing_keywords': ['kubernetes', 'microservices'],
            }
        )
        print(f"  ✓ Analysis {i+1}: Score = {score}")
    
    # Demo 6: Analyze Trends
    print_section("6. Analyze Score Trends")
    
    trends = AnalyticsService.get_score_trends(user)
    
    print(f"\nTrend Analysis:")
    print(f"  - Direction: {trends['trend'].upper()}")
    print(f"  - Improvement Rate: {trends['improvement_rate']:.2f} points per analysis")
    print(f"  - Total Analyses: {len(trends['scores'])}")
    
    if trends['scores']:
        print(f"  - Score Range: {min(trends['scores']):.1f} - {max(trends['scores']):.1f}")
        print(f"  - Latest Score: {trends['scores'][-1]:.1f}")
    
    # Demo 7: Detailed Trend Analysis
    print_section("7. Detailed Trend Analysis")
    
    if trends['scores']:
        summary = TrendAnalysisService.get_trend_summary(trends['scores'])
        
        print(f"\nStatistical Analysis:")
        print(f"  - Trend Direction: {summary['direction']}")
        print(f"  - Improvement Rate: {summary['improvement_rate']:.4f}")
        print(f"  - Volatility (Std Dev): {summary['volatility']:.2f}")
        print(f"  - Trend Strength (R²): {summary['trend_strength']:.4f}")
        
        if summary['anomalies']:
            print(f"\n  Anomalies Detected: {len(summary['anomalies'])}")
            for idx, score in summary['anomalies']:
                print(f"    - Position {idx}: Score = {score}")
        else:
            print(f"\n  No anomalies detected")
        
        print(f"\nSummary: {summary['summary']}")
    
    # Demo 8: Top Missing Keywords
    print_section("8. Top Missing Keywords")
    
    top_keywords = AnalyticsService.get_top_missing_keywords(user, limit=5)
    
    if top_keywords:
        print("\nMost frequently missing keywords:")
        for i, (keyword, count) in enumerate(top_keywords, 1):
            print(f"  {i}. {keyword} (missing in {count} analyses)")
    else:
        print("\nNo missing keywords data available")
    
    # Demo 9: Improvement Report
    print_section("9. Generate Improvement Report")
    
    report = AnalyticsService.generate_improvement_report(user)
    
    print(f"\nImprovement Report for {user.username}:")
    print(f"  - Total Resumes: {report['total_resumes']}")
    print(f"  - Average Health: {report['average_health']:.2f}/100")
    print(f"  - Total Optimizations: {report['total_optimizations']}")
    print(f"  - Average Improvement: {report['average_improvement']:.2f} points")
    
    if report['recommendations']:
        print(f"\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Demo 10: Version History
    print_section("10. Version History")
    
    history = VersionService.get_version_history(resume)
    
    print(f"\nTotal Versions: {len(history)}")
    print("\nVersion History:")
    for version in history[:5]:  # Show last 5 versions
        print(f"  Version {version.version_number}:")
        print(f"    - Type: {version.modification_type}")
        print(f"    - Score: {version.ats_score or 'N/A'}")
        print(f"    - Date: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if version.user_notes:
            print(f"    - Notes: {version.user_notes}")
    
    if len(history) > 5:
        print(f"  ... and {len(history) - 5} more versions")
    
    print_section("Demo Complete!")
    print("\nAll services are working correctly!")
    print("\nYou can now:")
    print("  1. View the resume in the admin panel")
    print("  2. Check version history")
    print("  3. Review analytics data")
    print("  4. Explore trend analysis")
    print("\nThank you for using NextGenCV v2.0!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
