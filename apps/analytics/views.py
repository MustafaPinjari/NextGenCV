from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from apps.resumes.models import Resume, ResumeAnalysis, OptimizationHistory
from apps.resumes.utils.query_optimization import (
    get_user_analyses_optimized,
    get_user_optimizations_optimized,
    bulk_prefetch_resume_relations
)
from .services.analytics_service import AnalyticsService
import logging
import json

logger = logging.getLogger(__name__)


@login_required
def analytics_dashboard(request):
    """
    Display comprehensive analytics dashboard for user's resumes.
    
    Shows:
    - Resume health meter (0-100 score)
    - Total number of resume versions
    - ATS score trend over time
    - Top missing keywords across all analyses
    - Section completeness percentages
    - Average score improvement from optimization sessions
    
    Prepares chart data in JSON format for Chart.js visualization.
    
    Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
    """
    user = request.user
    
    # Get all user's resumes with optimized query
    resumes = bulk_prefetch_resume_relations(
        Resume.objects.filter(user=user)
    )
    
    # Check if user has any resumes
    if not resumes.exists():
        context = {
            'has_resumes': False,
            'message': 'Create your first resume to see analytics!'
        }
        return render(request, 'analytics/dashboard.html', context)
    
    # Calculate metrics for each resume
    resume_health_scores = []
    total_versions = 0
    
    for resume in resumes:
        # Calculate health score
        health_score = AnalyticsService.calculate_resume_health(resume)
        resume_health_scores.append({
            'resume_id': resume.id,
            'resume_title': resume.title,
            'health_score': health_score
        })
        
        # Count versions
        total_versions += resume.versions.count()
    
    # Calculate average health across all resumes
    if resume_health_scores:
        average_health = sum(r['health_score'] for r in resume_health_scores) / len(resume_health_scores)
    else:
        average_health = 0.0
    
    # Get score trends
    score_trends = AnalyticsService.get_score_trends(user)
    
    # Get top missing keywords
    top_missing_keywords = AnalyticsService.get_top_missing_keywords(user, limit=10)
    
    # Calculate section completeness across all resumes
    section_completeness = {
        'personal_info': 0,
        'experiences': 0,
        'education': 0,
        'skills': 0,
        'projects': 0
    }
    
    for resume in resumes:
        if hasattr(resume, 'personal_info'):
            section_completeness['personal_info'] += 1
        if resume.experiences.exists():
            section_completeness['experiences'] += 1
        if resume.education.exists():
            section_completeness['education'] += 1
        if resume.skills.exists():
            section_completeness['skills'] += 1
        if resume.projects.exists():
            section_completeness['projects'] += 1
    
    # Convert to percentages
    total_resumes = resumes.count()
    section_completeness_percent = {
        section: round((count / total_resumes) * 100, 1)
        for section, count in section_completeness.items()
    }
    
    # Get optimization statistics
    all_optimizations = OptimizationHistory.objects.filter(resume__user=user)
    total_optimizations = all_optimizations.count()
    
    # Calculate average improvement from optimizations
    improvements = [
        opt.improvement_delta
        for opt in all_optimizations
        if opt.improvement_delta is not None
    ]
    average_improvement = sum(improvements) / len(improvements) if improvements else 0.0
    
    # Prepare chart data for Chart.js
    chart_data = {
        'score_trend': {
            'labels': score_trends.get('timestamps', []),
            'scores': score_trends.get('scores', []),
            'moving_average': score_trends.get('moving_average', [])
        },
        'health_by_resume': {
            'labels': [r['resume_title'] for r in resume_health_scores],
            'data': [r['health_score'] for r in resume_health_scores]
        },
        'section_completeness': {
            'labels': ['Personal Info', 'Experience', 'Education', 'Skills', 'Projects'],
            'data': [
                section_completeness_percent['personal_info'],
                section_completeness_percent['experiences'],
                section_completeness_percent['education'],
                section_completeness_percent['skills'],
                section_completeness_percent['projects']
            ]
        }
    }
    
    # Determine health status and color
    if average_health >= 80:
        health_status = 'excellent'
        health_color = 'success'
    elif average_health >= 60:
        health_status = 'good'
        health_color = 'info'
    elif average_health >= 40:
        health_status = 'fair'
        health_color = 'warning'
    else:
        health_status = 'needs improvement'
        health_color = 'danger'
    
    logger.info(
        f'Analytics dashboard loaded for user {user.username}: '
        f'Average health: {average_health:.2f}, '
        f'Total resumes: {total_resumes}, '
        f'Total optimizations: {total_optimizations}'
    )
    
    context = {
        'has_resumes': True,
        'total_resumes': total_resumes,
        'average_health': round(average_health, 2),
        'health_status': health_status,
        'health_color': health_color,
        'resume_health_scores': resume_health_scores,
        'total_versions': total_versions,
        'score_trends': score_trends,
        'top_missing_keywords': top_missing_keywords,
        'section_completeness': section_completeness_percent,
        'total_optimizations': total_optimizations,
        'average_improvement': round(average_improvement, 2),
        'chart_data_json': json.dumps(chart_data),
        'trend_direction': score_trends.get('trend', 'no_data'),
        'improvement_rate': score_trends.get('improvement_rate', 0.0),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def analytics_trends(request):
    """
    Display detailed trend analysis for user's resume scores.
    
    Shows:
    - All analyses for user with timestamps
    - Detailed trend calculations
    - Moving average visualization
    - Improvement rate over time
    - Trend direction indicators
    
    Generates interactive trend charts with Chart.js.
    
    Requirements: 11.3, 11.6
    """
    user = request.user
    
    # Get all analyses for user's resumes with optimized query
    analyses = get_user_analyses_optimized(user)
    
    # Check if user has any analyses
    if not analyses.exists():
        context = {
            'has_analyses': False,
            'message': 'No analyses found. Analyze your resume with a job description to see trends!'
        }
        return render(request, 'analytics/trends.html', context)
    
    # Get score trends with detailed breakdown
    score_trends = AnalyticsService.get_score_trends(user, window_size=5)
    
    # Prepare detailed analysis data
    analysis_data = []
    for analysis in analyses:
        analysis_data.append({
            'id': analysis.id,
            'resume_title': analysis.resume.title,
            'timestamp': analysis.analysis_timestamp.isoformat(),
            'timestamp_display': analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M'),
            'final_score': analysis.final_score,
            'keyword_match_score': analysis.keyword_match_score,
            'skill_relevance_score': analysis.skill_relevance_score,
            'section_completeness_score': analysis.section_completeness_score,
            'experience_impact_score': analysis.experience_impact_score,
            'quantification_score': analysis.quantification_score,
            'action_verb_score': analysis.action_verb_score,
        })
    
    # Calculate component score trends
    component_trends = {
        'keyword_match': [a['keyword_match_score'] for a in analysis_data],
        'skill_relevance': [a['skill_relevance_score'] for a in analysis_data],
        'section_completeness': [a['section_completeness_score'] for a in analysis_data],
        'experience_impact': [a['experience_impact_score'] for a in analysis_data],
        'quantification': [a['quantification_score'] for a in analysis_data],
        'action_verb': [a['action_verb_score'] for a in analysis_data],
    }
    
    # Prepare chart data for Chart.js
    chart_data = {
        'overall_trend': {
            'labels': score_trends.get('timestamps', []),
            'scores': score_trends.get('scores', []),
            'moving_average': score_trends.get('moving_average', [])
        },
        'component_trends': {
            'labels': [a['timestamp_display'] for a in analysis_data],
            'datasets': [
                {
                    'label': 'Keyword Match',
                    'data': component_trends['keyword_match'],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.1)'
                },
                {
                    'label': 'Skill Relevance',
                    'data': component_trends['skill_relevance'],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.1)'
                },
                {
                    'label': 'Section Completeness',
                    'data': component_trends['section_completeness'],
                    'borderColor': 'rgb(255, 206, 86)',
                    'backgroundColor': 'rgba(255, 206, 86, 0.1)'
                },
                {
                    'label': 'Experience Impact',
                    'data': component_trends['experience_impact'],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.1)'
                },
                {
                    'label': 'Quantification',
                    'data': component_trends['quantification'],
                    'borderColor': 'rgb(153, 102, 255)',
                    'backgroundColor': 'rgba(153, 102, 255, 0.1)'
                },
                {
                    'label': 'Action Verbs',
                    'data': component_trends['action_verb'],
                    'borderColor': 'rgb(255, 159, 64)',
                    'backgroundColor': 'rgba(255, 159, 64, 0.1)'
                }
            ]
        }
    }
    
    # Calculate statistics
    total_analyses = analyses.count()
    first_score = score_trends['scores'][0] if score_trends['scores'] else 0
    latest_score = score_trends['scores'][-1] if score_trends['scores'] else 0
    total_improvement = latest_score - first_score
    
    logger.info(
        f'Trend analysis loaded for user {user.username}: '
        f'{total_analyses} analyses, '
        f'Improvement: {total_improvement:.2f} points'
    )
    
    context = {
        'has_analyses': True,
        'total_analyses': total_analyses,
        'first_score': round(first_score, 2),
        'latest_score': round(latest_score, 2),
        'total_improvement': round(total_improvement, 2),
        'improvement_rate': score_trends.get('improvement_rate', 0.0),
        'trend_direction': score_trends.get('trend', 'stable'),
        'analysis_data': analysis_data,
        'chart_data_json': json.dumps(chart_data),
    }
    
    return render(request, 'analytics/trends.html', context)


@login_required
def improvement_report(request):
    """
    Generate comprehensive improvement report for user.
    
    Shows:
    - Overall resume quality metrics
    - Optimization history with details
    - Personalized recommendations
    - Progress tracking
    - Action items for improvement
    
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7
    """
    user = request.user
    
    # Generate comprehensive report using AnalyticsService
    report = AnalyticsService.generate_improvement_report(user)
    
    # Check if user has any resumes
    if report['total_resumes'] == 0:
        context = {
            'has_resumes': False,
            'message': 'Create your first resume to see your improvement report!'
        }
        return render(request, 'analytics/improvement_report.html', context)
    
    # Get detailed optimization history with optimized query
    optimizations = get_user_optimizations_optimized(user)
    
    # Prepare optimization history data
    optimization_history = []
    for opt in optimizations:
        optimization_history.append({
            'id': opt.id,
            'resume_title': opt.resume.title,
            'timestamp': opt.optimization_timestamp.strftime('%Y-%m-%d %H:%M'),
            'original_score': opt.original_score,
            'optimized_score': opt.optimized_score or opt.original_score,
            'improvement_delta': opt.improvement_delta or 0.0,
            'changes_count': sum(opt.changes_summary.values()) if opt.changes_summary else 0,
            'changes_summary': opt.changes_summary,
        })
    
    # Get all user's resumes with health scores using optimized query
    resumes = bulk_prefetch_resume_relations(
        Resume.objects.filter(user=user)
    )
    
    resume_details = []
    for resume in resumes:
        health_score = AnalyticsService.calculate_resume_health(resume)
        
        # Determine what's missing
        missing_sections = []
        if not hasattr(resume, 'personal_info'):
            missing_sections.append('Personal Information')
        if not resume.experiences.exists():
            missing_sections.append('Work Experience')
        if not resume.education.exists():
            missing_sections.append('Education')
        if not resume.skills.exists():
            missing_sections.append('Skills')
        
        resume_details.append({
            'id': resume.id,
            'title': resume.title,
            'health_score': health_score,
            'missing_sections': missing_sections,
            'last_updated': resume.updated_at.strftime('%Y-%m-%d'),
            'version_count': resume.versions.count(),
            'analysis_count': resume.analyses.count(),
        })
    
    # Sort resumes by health score (lowest first - needs most attention)
    resume_details.sort(key=lambda x: x['health_score'])
    
    # Categorize recommendations by priority
    high_priority_recommendations = []
    medium_priority_recommendations = []
    low_priority_recommendations = []
    
    for rec in report['recommendations']:
        if 'below 50%' in rec or 'missing' in rec.lower():
            high_priority_recommendations.append(rec)
        elif 'moderate' in rec or 'consider' in rec.lower():
            medium_priority_recommendations.append(rec)
        else:
            low_priority_recommendations.append(rec)
    
    # Calculate progress metrics
    if report['total_optimizations'] > 0:
        optimization_rate = 'Active'
        optimization_message = f"You've optimized your resume {report['total_optimizations']} time(s)."
    else:
        optimization_rate = 'Not Started'
        optimization_message = "Try the 'Fix My Resume' feature to improve your ATS score."
    
    # Determine overall status
    if report['average_health'] >= 80:
        overall_status = 'Excellent'
        status_color = 'success'
        status_message = 'Your resumes are in great shape! Keep up the good work.'
    elif report['average_health'] >= 60:
        overall_status = 'Good'
        status_color = 'info'
        status_message = 'Your resumes are doing well. A few improvements could make them even better.'
    elif report['average_health'] >= 40:
        overall_status = 'Fair'
        status_color = 'warning'
        status_message = 'Your resumes need some attention. Focus on the high-priority recommendations.'
    else:
        overall_status = 'Needs Improvement'
        status_color = 'danger'
        status_message = 'Your resumes need significant work. Start with completing all sections.'
    
    logger.info(
        f'Improvement report generated for user {user.username}: '
        f'Status: {overall_status}, '
        f'Average health: {report["average_health"]:.2f}'
    )
    
    context = {
        'has_resumes': True,
        'total_resumes': report['total_resumes'],
        'average_health': report['average_health'],
        'overall_status': overall_status,
        'status_color': status_color,
        'status_message': status_message,
        'total_optimizations': report['total_optimizations'],
        'average_improvement': report['average_improvement'],
        'optimization_rate': optimization_rate,
        'optimization_message': optimization_message,
        'top_missing_keywords': report['top_missing_keywords'],
        'high_priority_recommendations': high_priority_recommendations,
        'medium_priority_recommendations': medium_priority_recommendations,
        'low_priority_recommendations': low_priority_recommendations,
        'optimization_history': optimization_history,
        'resume_details': resume_details,
    }
    
    return render(request, 'analytics/improvement_report.html', context)
