# Bullet point rewriting service
from typing import Dict, List, Optional
import re
import random
from apps.analyzer.services.action_verb_analyzer import ActionVerbAnalyzerService


class BulletPointRewriterService:
    """
    Service for rewriting resume bullet points with stronger action verbs.
    Improves achievement statements by replacing weak verbs with strong ones.
    """
    
    # Context-based verb selection mapping
    CONTEXT_VERB_MAPPING = {
        'team': ['led', 'managed', 'coordinated', 'supervised', 'mentored', 'guided', 'directed'],
        'system': ['developed', 'engineered', 'built', 'architected', 'designed', 'implemented'],
        'application': ['developed', 'engineered', 'built', 'created', 'programmed', 'deployed'],
        'process': ['optimized', 'streamlined', 'improved', 'enhanced', 'refined', 'standardized'],
        'project': ['led', 'managed', 'delivered', 'executed', 'launched', 'spearheaded'],
        'revenue': ['generated', 'increased', 'grew', 'boosted', 'maximized', 'drove'],
        'cost': ['reduced', 'decreased', 'minimized', 'cut', 'saved', 'lowered'],
        'performance': ['improved', 'enhanced', 'optimized', 'accelerated', 'boosted', 'elevated'],
        'customer': ['served', 'supported', 'assisted', 'helped', 'resolved', 'satisfied'],
        'data': ['analyzed', 'processed', 'evaluated', 'interpreted', 'synthesized', 'leveraged'],
        'strategy': ['developed', 'formulated', 'devised', 'crafted', 'designed', 'strategized'],
        'product': ['launched', 'delivered', 'shipped', 'released', 'introduced', 'produced'],
        'quality': ['improved', 'enhanced', 'elevated', 'ensured', 'maintained', 'guaranteed'],
        'training': ['trained', 'educated', 'mentored', 'coached', 'developed', 'instructed'],
        'research': ['researched', 'investigated', 'analyzed', 'studied', 'explored', 'examined'],
    }
    
    @staticmethod
    def rewrite_bullet_point(bullet: str, context: Optional[str] = None) -> Dict:
        """
        Rewrite a bullet point with stronger action verbs.
        
        Args:
            bullet: Original bullet point text
            context: Optional context (e.g., job description) for better verb selection
            
        Returns:
            Dictionary containing:
                - original: Original bullet point
                - rewritten: Rewritten bullet point
                - changed: Whether any changes were made
                - reason: Explanation of changes
        """
        if not bullet or not bullet.strip():
            return {
                'original': bullet,
                'rewritten': bullet,
                'changed': False,
                'reason': 'Empty bullet point'
            }
        
        original = bullet.strip()
        rewritten = original
        changed = False
        reasons = []
        
        # Check if starts with weak verb
        weak_verb_found = None
        for weak_verb in ActionVerbAnalyzerService.WEAK_VERBS:
            # Handle multi-word phrases
            if ' ' in weak_verb:
                pattern = r'^' + re.escape(weak_verb)
                if re.search(pattern, rewritten.lower()):
                    weak_verb_found = weak_verb
                    break
            else:
                # Single word - check if it's the first word
                words = rewritten.split()
                if words and words[0].lower() == weak_verb:
                    weak_verb_found = weak_verb
                    break
        
        # Replace weak verb with strong verb
        if weak_verb_found:
            strong_verb = BulletPointRewriterService.select_strong_verb(
                rewritten, context
            )
            
            # Replace the weak verb
            if ' ' in weak_verb_found:
                # Multi-word phrase
                pattern = r'^' + re.escape(weak_verb_found)
                rewritten = re.sub(pattern, strong_verb, rewritten, flags=re.IGNORECASE)
            else:
                # Single word
                words = rewritten.split()
                words[0] = strong_verb.capitalize()
                rewritten = ' '.join(words)
            
            changed = True
            reasons.append(f"Replaced weak verb '{weak_verb_found}' with '{strong_verb}'")
        
        # Ensure starts with action verb
        if not BulletPointRewriterService.starts_with_action_verb(rewritten):
            # Add a strong action verb at the beginning
            strong_verb = BulletPointRewriterService.select_strong_verb(
                rewritten, context
            )
            rewritten = f"{strong_verb.capitalize()} {rewritten}"
            changed = True
            reasons.append(f"Added action verb '{strong_verb}' at the beginning")
        
        return {
            'original': original,
            'rewritten': rewritten,
            'changed': changed,
            'reason': '; '.join(reasons) if reasons else 'No changes needed'
        }
    
    @staticmethod
    def select_strong_verb(bullet: str, context: Optional[str] = None) -> str:
        """
        Select an appropriate strong action verb based on context.
        
        Args:
            bullet: Bullet point text
            context: Optional context for better selection
            
        Returns:
            Selected strong action verb
        """
        bullet_lower = bullet.lower()
        combined_text = bullet_lower
        
        if context:
            combined_text += ' ' + context.lower()
        
        # Check for context keywords and select appropriate verb
        for keyword, verbs in BulletPointRewriterService.CONTEXT_VERB_MAPPING.items():
            if keyword in combined_text:
                return random.choice(verbs)
        
        # If no specific context match, return a general strong verb
        general_verbs = [
            'achieved', 'accomplished', 'delivered', 'executed', 'implemented',
            'developed', 'created', 'established', 'improved', 'enhanced'
        ]
        return random.choice(general_verbs)
    
    @staticmethod
    def starts_with_action_verb(bullet: str) -> bool:
        """
        Check if bullet point starts with an action verb.
        
        Args:
            bullet: Bullet point text
            
        Returns:
            True if starts with action verb, False otherwise
        """
        if not bullet or not bullet.strip():
            return False
        
        # Get first word
        words = bullet.strip().split()
        if not words:
            return False
        
        first_word = words[0].lower().rstrip('.,;:')
        
        # Check if it's a strong action verb
        if first_word in ActionVerbAnalyzerService.STRONG_ACTION_VERBS:
            return True
        
        # Check if it's NOT a weak verb (could be a decent verb not in our lists)
        if first_word not in ActionVerbAnalyzerService.WEAK_VERBS:
            # Check if it looks like a verb (ends with common verb patterns)
            verb_patterns = ['ed', 'ing', 'ized', 'ated', 'ified']
            if any(first_word.endswith(pattern) for pattern in verb_patterns):
                return True
        
        return False
    
    @staticmethod
    def rewrite_multiple_bullets(bullets: List[str], context: Optional[str] = None) -> List[Dict]:
        """
        Rewrite multiple bullet points.
        
        Args:
            bullets: List of bullet point texts
            context: Optional context for better verb selection
            
        Returns:
            List of rewrite results for each bullet
        """
        results = []
        for bullet in bullets:
            result = BulletPointRewriterService.rewrite_bullet_point(bullet, context)
            results.append(result)
        return results
