# Keyword extraction service
import spacy
from typing import Set, Dict
import re


class KeywordExtractorService:
    """
    Service for extracting and analyzing keywords from text using NLP.
    Uses spaCy for natural language processing.
    """
    
    # Load spaCy model (singleton pattern)
    _nlp = None
    
    # Common stop words to exclude
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them',
        'their', 'my', 'your', 'his', 'her', 'its', 'our'
    }
    
    @classmethod
    def _get_nlp(cls):
        """Lazy load spaCy model."""
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load('en_core_web_sm')
            except OSError:
                # If model not found, download it
                import subprocess
                subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
                cls._nlp = spacy.load('en_core_web_sm')
        return cls._nlp
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> Set[str]:
        """
        Extract keywords from text using spaCy NLP.
        
        Args:
            text: Input text to extract keywords from
            min_length: Minimum length of keywords to include
            
        Returns:
            Set of extracted keywords (lowercase)
        """
        if not text or not text.strip():
            return set()
        
        nlp = KeywordExtractorService._get_nlp()
        doc = nlp(text.lower())
        
        keywords = set()
        
        # Extract nouns and proper nouns
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) >= min_length:
                # Use lemma for better matching
                lemma = token.lemma_.lower()
                if lemma not in KeywordExtractorService.STOP_WORDS:
                    keywords.add(lemma)
        
        # Extract noun phrases (up to 3 words)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            # Only include phrases with 1-3 words
            if 1 <= len(phrase.split()) <= 3 and len(phrase) >= min_length:
                # Remove stop words from phrase
                words = phrase.split()
                filtered_words = [w for w in words if w not in KeywordExtractorService.STOP_WORDS]
                if filtered_words:
                    filtered_phrase = ' '.join(filtered_words)
                    keywords.add(filtered_phrase)
        
        # Remove very short tokens
        keywords = {kw for kw in keywords if len(kw) >= min_length}
        
        return keywords
    
    @staticmethod
    def calculate_keyword_frequency(text: str) -> Dict[str, int]:
        """
        Calculate frequency of each keyword in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary mapping keywords to their frequency counts
        """
        if not text or not text.strip():
            return {}
        
        keywords = KeywordExtractorService.extract_keywords(text)
        text_lower = text.lower()
        
        frequency = {}
        for keyword in keywords:
            # Count occurrences (case-insensitive)
            count = text_lower.count(keyword)
            if count > 0:
                frequency[keyword] = count
        
        return frequency
    
    @staticmethod
    def weight_keywords_by_importance(keywords: Set[str], context: str) -> Dict[str, float]:
        """
        Assign importance weights to keywords based on context.
        
        Args:
            keywords: Set of keywords to weight
            context: Context text (e.g., job description) to determine importance
            
        Returns:
            Dictionary mapping keywords to importance weights (0.0 to 1.0)
        """
        if not keywords or not context:
            return {kw: 0.5 for kw in keywords}
        
        # Calculate frequency in context
        context_freq = KeywordExtractorService.calculate_keyword_frequency(context)
        
        # Find max frequency for normalization
        max_freq = max(context_freq.values()) if context_freq else 1
        
        weights = {}
        for keyword in keywords:
            freq = context_freq.get(keyword, 0)
            # Normalize to 0.0-1.0 range
            # Keywords not in context get 0.1, keywords in context get 0.1-1.0
            if freq == 0:
                weights[keyword] = 0.1
            else:
                # Scale frequency to 0.1-1.0 range
                weights[keyword] = 0.1 + (0.9 * (freq / max_freq))
        
        return weights
