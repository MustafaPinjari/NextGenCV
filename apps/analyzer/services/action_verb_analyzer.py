# Action verb analysis service
from typing import List, Dict
import re


class ActionVerbAnalyzerService:
    """
    Service for analyzing action verbs in resume bullet points.
    Evaluates strength of action verbs and identifies weak verbs.
    """
    
    # Strong action verbs that demonstrate impact
    STRONG_ACTION_VERBS = {
        'achieved', 'accelerated', 'accomplished', 'delivered', 'developed',
        'engineered', 'established', 'executed', 'generated', 'implemented',
        'improved', 'increased', 'launched', 'led', 'optimized', 'reduced',
        'spearheaded', 'streamlined', 'transformed', 'built', 'created',
        'designed', 'directed', 'drove', 'enhanced', 'expanded', 'facilitated',
        'founded', 'grew', 'headed', 'initiated', 'innovated', 'instituted',
        'introduced', 'managed', 'orchestrated', 'overhauled', 'pioneered',
        'produced', 'programmed', 'redesigned', 'restructured', 'revamped',
        'revolutionized', 'shaped', 'strengthened', 'succeeded', 'supervised',
        'surpassed', 'upgraded', 'automated', 'collaborated', 'coordinated',
        'demonstrated', 'exceeded', 'formulated', 'guided', 'influenced',
        'mentored', 'negotiated', 'organized', 'planned', 'presented',
        'resolved', 'trained', 'unified', 'validated', 'architected',
        'championed', 'consolidated', 'cultivated', 'customized', 'deployed',
        'devised', 'elevated', 'empowered', 'enabled', 'enforced',
        'expedited', 'fostered', 'integrated', 'leveraged', 'maximized',
        'modernized', 'mobilized', 'operationalized', 'outperformed',
        'positioned', 'prioritized', 'propelled', 'realized', 'reengineered',
        'refined', 'revitalized', 'scaled', 'secured', 'standardized',
        'strategized', 'synthesized', 'systematized', 'utilized'
    }
    
    # Weak verbs that should be replaced
    WEAK_VERBS = {
        'did', 'made', 'worked', 'helped', 'tried', 'used', 'was', 'were',
        'had', 'got', 'went', 'came', 'saw', 'took', 'gave', 'found',
        'told', 'asked', 'seemed', 'felt', 'became', 'left', 'put',
        'responsible for', 'in charge of', 'tasked with', 'duties included',
        'worked on', 'helped with', 'assisted with', 'involved in',
        'participated in', 'contributed to', 'supported', 'handled'
    }
    
    @staticmethod
    def analyze_action_verbs(text: str) -> Dict:
        """
        Analyze action verbs in text (typically bullet points).
        
        Args:
            text: Text to analyze (can be multiple bullet points)
            
        Returns:
            Dictionary containing:
                - strong_verbs: List of strong action verbs found
                - weak_verbs: List of weak verbs found
                - total_verbs: Total number of action verbs
                - strong_count: Count of strong verbs
                - weak_count: Count of weak verbs
        """
        if not text or not text.strip():
            return {
                'strong_verbs': [],
                'weak_verbs': [],
                'total_verbs': 0,
                'strong_count': 0,
                'weak_count': 0
            }
        
        text_lower = text.lower()
        
        # Split into sentences/bullet points
        # Handle various bullet point formats
        lines = re.split(r'[•\-\*\n]|\d+\.', text)
        lines = [line.strip() for line in lines if line.strip()]
        
        strong_verbs_found = []
        weak_verbs_found = []
        
        for line in lines:
            # Get first few words (where action verb typically appears)
            words = line.lower().split()[:5]  # Check first 5 words
            
            # Check for strong verbs
            for verb in ActionVerbAnalyzerService.STRONG_ACTION_VERBS:
                if verb in words:
                    strong_verbs_found.append(verb)
                    break  # Only count one verb per line
            
            # Check for weak verbs
            for verb in ActionVerbAnalyzerService.WEAK_VERBS:
                # Handle multi-word weak phrases
                if ' ' in verb:
                    if verb in line.lower():
                        weak_verbs_found.append(verb)
                        break
                else:
                    if verb in words:
                        weak_verbs_found.append(verb)
                        break
        
        total_verbs = len(strong_verbs_found) + len(weak_verbs_found)
        
        return {
            'strong_verbs': strong_verbs_found,
            'weak_verbs': weak_verbs_found,
            'total_verbs': total_verbs,
            'strong_count': len(strong_verbs_found),
            'weak_count': len(weak_verbs_found)
        }
    
    @staticmethod
    def calculate_action_verb_score(text: str) -> float:
        """
        Calculate action verb strength score (0-100).
        
        Args:
            text: Text to analyze
            
        Returns:
            Score from 0-100 based on ratio of strong to total verbs
        """
        if not text or not text.strip():
            return 0.0
        
        analysis = ActionVerbAnalyzerService.analyze_action_verbs(text)
        
        total_verbs = analysis['total_verbs']
        if total_verbs == 0:
            # No verbs found - return low score
            return 20.0
        
        strong_count = analysis['strong_count']
        
        # Calculate percentage of strong verbs
        strong_ratio = strong_count / total_verbs
        
        # Convert to 0-100 scale
        # 100% strong verbs = 100 score
        # 0% strong verbs = 0 score
        score = strong_ratio * 100
        
        return round(score, 2)
