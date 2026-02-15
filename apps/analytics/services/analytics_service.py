# Analytics service
from typing import Dict, List, Tuple, Optional
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from apps.resumes.models import Resume, ResumeAnalysis, OptimizationHistory
from apps.analyzer.services.action_verb_analyzer import ActionVerbAnalyzerService
from apps.analyzer.services.quantification_detector import QuantificationDetectorService
from .cache_utils import (
    get_cached_resume_health,
    cache_resume_health,
    get_cached_score_trends,
    cache_score_trends,
    get_cached_analytics_data,
    cache_analytics_data
)


class AnalyticsService:
    """
    Service for calculating resume analytics and health metrics.
    Provides comprehensive insights into resume quality and improvement trends.
    
    Uses caching to improve performance for expensive calculations.
    Requirements: 18.3
    """
    
    @staticmethod
    def calculate_resume_health(resume: Resume) -> float:
        """
        Calculate overall resume health score (0-100).
        
        Uses caching to avoid recalculating for the same resume.
        Cache is valid for 5 minutes.
        
        Components:
        - Section completeness (40 points)
        - Contact info completeness (15 points)
        - Quantified achievements (20 points)
        - Action verb usage (15 points)
        - ATS-friendly formatting (10 points)
        
        Args:
            resume: Resume instance to analyze
            
        Returns:
            float: Health score between 0 and 100
            
        Requirements: 18.3
        """
        # Try to get from cache first
        cached_score = get_cached_resume_health(resume.id)
        if cached_score is not None:
            return cached_score
        
        # Calculate health score
        health_score = 0.0
        
        # 1. Section completeness (40 points)
        sections = {
            'personal_info': hasattr(resume, 'personal_info'),
            'experiences': resume.experiences.exists(),
            'education': resume.education.exists(),
            'skills': resume.skills.exists(),
        }
        completed_sections = sum(1 for has_content in sections.values() if has_content)
        health_score += (completed_sections / len(sections)) * 40
        
        # 2. Contact info completeness (15 points)
        if hasattr(resume, 'personal_info'):
            pi = resume.personal_info
            contact_fields = [
                bool(pi.email),
                bool(pi.phone),
                bool(pi.location),
            ]
            completed_contact = sum(contact_fields)
            health_score += (completed_contact / len(contact_fields)) * 15
        
        # 3. Quantified achievements (20 points)
        total_bullets = 0
        quantified_bullets = 0
        
        for experience in resume.experiences.all():
            if experience.description:
                bullets = [line.strip() for line in experience.description.split('\n') if line.strip()]
                total_bullets += len(bullets)
                for bullet in bullets:
                    if QuantificationDetectorService.has_quantification(bullet):
                        quantified_bullets += 1
        
        if total_bullets > 0:
            health_score += (quantified_bullets / total_bullets) * 20
        
        # 4. Action verb usage (15 points)
        strong_verb_count = 0
        
        for experience in resume.experiences.all():
            if experience.description:
                bullets = [line.strip() for line in experience.description.split('\n') if line.strip()]
                for bullet in bullets:
                    # Check if bullet starts with a strong action verb
                    words = bullet.split()
                    if words:
                        first_word = words[0].lower().rstrip('.,;:')
                        if first_word in ActionVerbAnalyzerService.STRONG_ACTION_VERBS:
                            strong_verb_count += 1
        
        if total_bullets > 0:
            health_score += (strong_verb_count / total_bullets) * 15
        
        # 5. ATS-friendly formatting (10 points)
        # Check for basic ATS-friendly characteristics
        is_ats_friendly = True
        
        # Check if template is ATS-friendly (professional, modern, classic are good)
        ats_friendly_templates = ['professional', 'modern', 'classic']
        if resume.template in ats_friendly_templates:
            health_score += 10
        
        # Round and cache the result
        health_score = round(health_score, 2)
        cache_resume_health(resume.id, health_score)
        
        return health_score
    
    @staticmethod
    def get_score_trends(user: User, window_size: int = 5) -> Dict:
        """
        Calculate score trends over time with moving average.
        
        Uses caching to avoid recalculating for the same user.
        Cache is valid for 10 minutes.
        
        Args:
            user: User instance
            window_size: Window size for moving average calculation
            
        Returns:
            Dict: Trend data including scores, moving average, and improvement rate
            
        Requirements: 18.3
        """
        # Try to get from cache first
        cached_trends = get_cached_score_trends(user.id)
        if cached_trends is not None:
            return cached_trends
        
        # Get all analyses for user's resumes
        analyses = ResumeAnalysis.objects.filter(
            resume__user=user
        ).order_by('analysis_timestamp').values_list('final_score', 'analysis_timestamp')
        
        if not analyses:
            return {
                'scores': [],
                'timestamps': [],
                'moving_average': [],
                'improvement_rate': 0.0,
                'trend': 'no_data'
            }
        
        scores = [score for score, _ in analyses]
        timestamps = [ts.isoformat() for _, ts in analyses]
        
        # Calculate moving average
        moving_avg = AnalyticsService._calculate_moving_average(scores, window_size)
        
        # Calculate improvement rate
        if len(scores) >= 2:
            improvement_rate = (scores[-1] - scores[0]) / len(scores)
        else:
            improvement_rate = 0.0
        
        # Determine trend direction
        if improvement_rate > 0.5:
            trend = 'improving'
        elif improvement_rate < -0.5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        result = {
            'scores': scores,
            'timestamps': timestamps,
            'moving_average': moving_avg,
            'improvement_rate': round(improvement_rate, 2),
            'trend': trend
        }
        
        # Cache the result
        cache_score_trends(user.id, result)
        
        return result
    
    @staticmethod
    def _calculate_moving_average(scores: List[float], window_size: int) -> List[float]:
        """
        Calculate moving average for a list of scores.
        
        Args:
            scores: List of scores
            window_size: Window size for averaging
            
        Returns:
            List[float]: Moving average values
        """
        if not scores:
            return []
        
        moving_avg = []
        for i in range(len(scores)):
            start_idx = max(0, i - window_size + 1)
            window = scores[start_idx:i + 1]
            avg = sum(window) / len(window)
            moving_avg.append(round(avg, 2))
        
        return moving_avg
    
    @staticmethod
    def get_top_missing_keywords(user: User, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently missing keywords across all analyses.
        
        Args:
            user: User instance
            limit: Maximum number of keywords to return
            
        Returns:
            List[Tuple[str, int]]: List of (keyword, frequency) tuples
        """
        # Get all analyses for user's resumes
        analyses = ResumeAnalysis.objects.filter(resume__user=user)
        
        # Aggregate missing keywords
        keyword_counts = {}
        for analysis in analyses:
            for keyword in analysis.missing_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top N
        top_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return top_keywords
    
    @staticmethod
    def generate_improvement_report(user: User) -> Dict:
        """
        Generate comprehensive improvement report for user.
        
        Args:
            user: User instance
            
        Returns:
            Dict: Comprehensive report with metrics and recommendations
        """
        # Get all user's resumes
        resumes = Resume.objects.filter(user=user).prefetch_related(
            'analyses', 'optimizations', 'versions'
        )
        
        if not resumes.exists():
            return {
                'total_resumes': 0,
                'average_health': 0.0,
                'total_optimizations': 0,
                'average_improvement': 0.0,
                'top_missing_keywords': [],
                'recommendations': ['Create your first resume to get started!']
            }
        
        # Calculate metrics
        total_resumes = resumes.count()
        
        # Calculate average health across all resumes
        health_scores = [
            AnalyticsService.calculate_resume_health(resume)
            for resume in resumes
        ]
        average_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        
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
        
        # Get top missing keywords
        top_missing_keywords = AnalyticsService.get_top_missing_keywords(user, limit=10)
        
        # Generate recommendations
        recommendations = AnalyticsService._generate_recommendations(
            average_health=average_health,
            total_optimizations=total_optimizations,
            top_missing_keywords=top_missing_keywords,
            resumes=resumes
        )
        
        return {
            'total_resumes': total_resumes,
            'average_health': round(average_health, 2),
            'total_optimizations': total_optimizations,
            'average_improvement': round(average_improvement, 2),
            'top_missing_keywords': top_missing_keywords,
            'recommendations': recommendations,
            'health_scores': health_scores,
        }
    
    @staticmethod
    def _generate_recommendations(average_health: float, total_optimizations: int,
                                 top_missing_keywords: List[Tuple[str, int]],
                                 resumes) -> List[str]:
        """
        Generate personalized recommendations based on analytics.
        
        Args:
            average_health: Average health score
            total_optimizations: Total number of optimizations
            top_missing_keywords: Top missing keywords
            resumes: QuerySet of user's resumes
            
        Returns:
            List[str]: List of recommendation strings
        """
        recommendations = []
        
        # Health-based recommendations
        if average_health < 50:
            recommendations.append(
                "Your resume health is below 50%. Focus on completing all sections "
                "and adding quantified achievements."
            )
        elif average_health < 70:
            recommendations.append(
                "Your resume health is moderate. Consider adding more quantified "
                "achievements and using stronger action verbs."
            )
        else:
            recommendations.append(
                "Your resume health is good! Keep maintaining high-quality content."
            )
        
        # Optimization recommendations
        if total_optimizations == 0:
            recommendations.append(
                "Try the 'Fix My Resume' feature to automatically optimize your resume "
                "for ATS systems."
            )
        
        # Keyword recommendations
        if top_missing_keywords:
            top_3_keywords = [kw for kw, _ in top_missing_keywords[:3]]
            recommendations.append(
                f"Consider adding these frequently missing keywords: {', '.join(top_3_keywords)}"
            )
        
        # Section-specific recommendations
        for resume in resumes:
            if not resume.experiences.exists():
                recommendations.append(
                    f"Add work experience to '{resume.title}' to improve its completeness."
                )
                break
            
            if not resume.skills.exists():
                recommendations.append(
                    f"Add skills to '{resume.title}' to improve keyword matching."
                )
                break
        
        return recommendations

