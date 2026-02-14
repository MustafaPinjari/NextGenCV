# Quantification suggestion service
from typing import Dict, List
import re
from apps.analyzer.services.quantification_detector import QuantificationDetectorService


class QuantificationSuggesterService:
    """
    Service for suggesting quantifications for achievements lacking metrics.
    Provides context-appropriate metric suggestions based on achievement type.
    """
    
    # Achievement type classification patterns
    ACHIEVEMENT_PATTERNS = {
        'performance': [
            r'\b(improve|enhance|optimize|accelerate|boost|increase|speed)\b',
            r'\b(performance|efficiency|productivity|throughput|response time)\b',
        ],
        'scale': [
            r'\b(scale|grow|expand|handle|process|manage|serve)\b',
            r'\b(users|customers|requests|transactions|records|data)\b',
        ],
        'team': [
            r'\b(lead|manage|supervise|mentor|coach|train|guide)\b',
            r'\b(team|developers|engineers|members|people|staff)\b',
        ],
        'financial': [
            r'\b(revenue|sales|profit|cost|budget|savings|roi)\b',
            r'\b(generate|increase|reduce|save|cut|grow)\b',
        ],
        'time': [
            r'\b(deliver|complete|finish|launch|ship|release)\b',
            r'\b(deadline|schedule|timeline|duration|time|period)\b',
        ],
        'quality': [
            r'\b(quality|reliability|accuracy|stability|uptime)\b',
            r'\b(improve|enhance|ensure|maintain|achieve)\b',
        ],
        'customer': [
            r'\b(customer|client|user|satisfaction|experience|support)\b',
            r'\b(improve|enhance|increase|resolve|handle)\b',
        ],
        'project': [
            r'\b(project|initiative|program|feature|product)\b',
            r'\b(deliver|launch|complete|implement|execute)\b',
        ],
        'automation': [
            r'\b(automate|streamline|eliminate|reduce manual)\b',
            r'\b(process|workflow|task|operation)\b',
        ],
        'code': [
            r'\b(code|codebase|application|system|software)\b',
            r'\b(write|develop|refactor|optimize|maintain)\b',
        ],
    }
    
    # Metric suggestions by achievement type
    METRIC_SUGGESTIONS = {
        'performance': [
            'X% faster',
            'X% improvement',
            'reduced by X%',
            'improved response time by Xms',
            'increased throughput by X%',
            'X% more efficient',
        ],
        'scale': [
            'X users',
            'X+ customers',
            'X million requests/day',
            'X transactions per second',
            'X GB of data',
            'scaled to X concurrent users',
        ],
        'team': [
            'team of X',
            'X developers',
            'X engineers',
            'X team members',
            'mentored X people',
            'managed X direct reports',
        ],
        'financial': [
            '$X revenue',
            '$X in savings',
            'X% ROI',
            '$X budget',
            'reduced costs by $X',
            'generated $X in sales',
        ],
        'time': [
            'X months',
            'X weeks',
            'delivered X days early',
            'reduced time by X%',
            'completed in X hours',
            'X-week sprint',
        ],
        'quality': [
            'X% uptime',
            'X% accuracy',
            'reduced errors by X%',
            'X% reliability',
            'improved quality by X%',
            'achieved X% SLA',
        ],
        'customer': [
            'X% satisfaction',
            'X customers served',
            'resolved X tickets',
            'X% faster resolution',
            'improved NPS by X points',
            'X% retention rate',
        ],
        'project': [
            'X projects',
            'X features',
            'X releases',
            'X milestones',
            'delivered X initiatives',
            'completed X sprints',
        ],
        'automation': [
            'saved X hours/week',
            'eliminated X manual steps',
            'reduced manual work by X%',
            'automated X processes',
            'X% automation coverage',
            'freed up X hours',
        ],
        'code': [
            'X lines of code',
            'X% code coverage',
            'reduced codebase by X%',
            'X commits',
            'X pull requests',
            'refactored X modules',
        ],
    }
    
    @staticmethod
    def suggest_quantification(bullet: str) -> Dict:
        """
        Suggest quantification for a bullet point lacking metrics.
        
        Args:
            bullet: Bullet point text
            
        Returns:
            Dictionary containing:
                - original: Original bullet point
                - has_quantification: Whether it already has metrics
                - achievement_type: Classified achievement type
                - suggestions: List of metric suggestions
                - example: Example with suggested metric
        """
        if not bullet or not bullet.strip():
            return {
                'original': bullet,
                'has_quantification': False,
                'achievement_type': 'unknown',
                'suggestions': [],
                'example': bullet
            }
        
        original = bullet.strip()
        
        # Check if already has quantification
        has_quant = QuantificationDetectorService.has_quantification(original)
        
        if has_quant:
            return {
                'original': original,
                'has_quantification': True,
                'achievement_type': 'already_quantified',
                'suggestions': [],
                'example': original
            }
        
        # Classify achievement type
        achievement_type = QuantificationSuggesterService.classify_achievement(original)
        
        # Get suggestions for this type
        suggestions = QuantificationSuggesterService.METRIC_SUGGESTIONS.get(
            achievement_type,
            ['[add specific metric]', '[add measurable result]']
        )
        
        # Create example with first suggestion
        example = QuantificationSuggesterService._create_example(original, suggestions[0])
        
        return {
            'original': original,
            'has_quantification': False,
            'achievement_type': achievement_type,
            'suggestions': suggestions,
            'example': example
        }
    
    @staticmethod
    def classify_achievement(bullet: str) -> str:
        """
        Classify achievement type based on content.
        
        Args:
            bullet: Bullet point text
            
        Returns:
            Achievement type classification
        """
        if not bullet:
            return 'unknown'
        
        bullet_lower = bullet.lower()
        
        # Score each achievement type
        type_scores = {}
        
        for achievement_type, patterns in QuantificationSuggesterService.ACHIEVEMENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, bullet_lower)
                score += len(matches)
            
            if score > 0:
                type_scores[achievement_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    @staticmethod
    def suggest_for_multiple_bullets(bullets: List[str]) -> List[Dict]:
        """
        Suggest quantifications for multiple bullet points.
        
        Args:
            bullets: List of bullet point texts
            
        Returns:
            List of suggestion results for each bullet
        """
        results = []
        for bullet in bullets:
            result = QuantificationSuggesterService.suggest_quantification(bullet)
            # Only include bullets that need quantification
            if not result['has_quantification']:
                results.append(result)
        return results
    
    @staticmethod
    def _create_example(bullet: str, suggestion: str) -> str:
        """
        Create an example bullet with suggested metric.
        
        Args:
            bullet: Original bullet point
            suggestion: Metric suggestion
            
        Returns:
            Example bullet with metric inserted
        """
        # Try to insert metric naturally
        # Look for common insertion points
        
        # Pattern 1: After action verb
        # "Improved system performance" -> "Improved system performance by X%"
        improvement_verbs = ['improved', 'increased', 'reduced', 'enhanced', 'optimized', 'accelerated']
        for verb in improvement_verbs:
            if verb in bullet.lower():
                # Add "by [metric]" after the object
                return f"{bullet} by {suggestion}"
        
        # Pattern 2: After "to" or "for"
        if ' to ' in bullet.lower() or ' for ' in bullet.lower():
            return f"{bullet}, achieving {suggestion}"
        
        # Pattern 3: At the end
        return f"{bullet}, resulting in {suggestion}"
    
    @staticmethod
    def get_suggestions_by_type(achievement_type: str) -> List[str]:
        """
        Get all metric suggestions for a specific achievement type.
        
        Args:
            achievement_type: Type of achievement
            
        Returns:
            List of metric suggestions
        """
        return QuantificationSuggesterService.METRIC_SUGGESTIONS.get(
            achievement_type,
            ['[add specific metric]']
        )
    
    @staticmethod
    def analyze_experience_quantification(experience_description: str) -> Dict:
        """
        Analyze quantification coverage in an experience description.
        
        Args:
            experience_description: Full experience description text
            
        Returns:
            Dictionary with analysis results
        """
        if not experience_description:
            return {
                'total_bullets': 0,
                'quantified_bullets': 0,
                'unquantified_bullets': 0,
                'coverage_percentage': 0.0,
                'suggestions': []
            }
        
        # Split into bullet points
        lines = experience_description.split('\n')
        bullets = [line.strip() for line in lines if line.strip() and len(line.strip()) > 20]
        
        quantified = []
        unquantified = []
        suggestions = []
        
        for bullet in bullets:
            if QuantificationDetectorService.has_quantification(bullet):
                quantified.append(bullet)
            else:
                unquantified.append(bullet)
                # Get suggestion for this bullet
                suggestion = QuantificationSuggesterService.suggest_quantification(bullet)
                suggestions.append(suggestion)
        
        total = len(bullets)
        coverage = (len(quantified) / total * 100) if total > 0 else 0.0
        
        return {
            'total_bullets': total,
            'quantified_bullets': len(quantified),
            'unquantified_bullets': len(unquantified),
            'coverage_percentage': round(coverage, 2),
            'suggestions': suggestions
        }
