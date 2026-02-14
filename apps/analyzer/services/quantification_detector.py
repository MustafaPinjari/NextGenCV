# Quantification detection service
import re
from typing import List, Dict


class QuantificationDetectorService:
    """
    Service for detecting quantified achievements in resume text.
    Identifies numbers, percentages, dollar amounts, and other metrics.
    """
    
    # Regex patterns for different types of quantifications
    PATTERNS = {
        'percentage': r'\b\d+(?:\.\d+)?%',  # 25%, 3.5%
        'dollar': r'\$\d+(?:,\d{3})*(?:\.\d{2})?[KMB]?',  # $50K, $1.5M, $100,000
        'number': r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|thousand|hundred|K|M|B))?\b',  # 100, 1.5M, 50K
        'range': r'\b\d+\s*-\s*\d+',  # 10-20
        'multiplier': r'\b\d+x\b',  # 2x, 10x
        'time': r'\b\d+\s*(?:year|month|week|day|hour)s?\b',  # 3 years, 6 months
    }
    
    @staticmethod
    def detect_quantifications(text: str) -> List[Dict]:
        """
        Detect all quantifications in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries containing:
                - type: Type of quantification (percentage, dollar, number, etc.)
                - value: The quantification string
                - position: Position in text
        """
        if not text or not text.strip():
            return []
        
        quantifications = []
        
        for quant_type, pattern in QuantificationDetectorService.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                quantifications.append({
                    'type': quant_type,
                    'value': match.group(),
                    'position': match.start()
                })
        
        # Sort by position
        quantifications.sort(key=lambda x: x['position'])
        
        return quantifications
    
    @staticmethod
    def has_quantification(text: str) -> bool:
        """
        Check if text contains any quantification.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains at least one quantification
        """
        if not text or not text.strip():
            return False
        
        for pattern in QuantificationDetectorService.PATTERNS.values():
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def calculate_quantification_score(text: str) -> float:
        """
        Calculate quantification score based on presence of metrics.
        
        Args:
            text: Text to analyze (typically all experience bullet points)
            
        Returns:
            Score from 0-100 based on ratio of quantified statements
        """
        if not text or not text.strip():
            return 0.0
        
        # Split into sentences/bullet points
        lines = re.split(r'[•\-\*\n]|\d+\.', text)
        lines = [line.strip() for line in lines if line.strip() and len(line) > 10]
        
        if not lines:
            return 0.0
        
        # Count lines with quantifications
        quantified_count = 0
        for line in lines:
            if QuantificationDetectorService.has_quantification(line):
                quantified_count += 1
        
        # Calculate percentage
        quantified_ratio = quantified_count / len(lines)
        
        # Convert to 0-100 scale
        score = quantified_ratio * 100
        
        return round(score, 2)
    
    @staticmethod
    def get_quantification_summary(text: str) -> Dict:
        """
        Get summary of quantifications in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing:
                - total_quantifications: Total count
                - by_type: Count by type
                - quantifications: List of all quantifications
        """
        if not text or not text.strip():
            return {
                'total_quantifications': 0,
                'by_type': {},
                'quantifications': []
            }
        
        quantifications = QuantificationDetectorService.detect_quantifications(text)
        
        # Count by type
        by_type = {}
        for quant in quantifications:
            quant_type = quant['type']
            by_type[quant_type] = by_type.get(quant_type, 0) + 1
        
        return {
            'total_quantifications': len(quantifications),
            'by_type': by_type,
            'quantifications': quantifications
        }
