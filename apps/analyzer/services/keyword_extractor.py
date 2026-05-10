# Keyword extraction service
import threading
import logging
import string
from typing import Set, Dict

logger = logging.getLogger(__name__)

# ── Thread-safe spaCy singleton ───────────────────────────────────────────────
_nlp_lock = threading.Lock()
_nlp = None
_nlp_failed = False


def _get_nlp():
    global _nlp, _nlp_failed
    if _nlp is not None:
        return _nlp
    if _nlp_failed:
        return None
    with _nlp_lock:
        if _nlp is None and not _nlp_failed:
            try:
                import spacy
                _nlp = spacy.load('en_core_web_sm')
                logger.info('spaCy en_core_web_sm loaded successfully')
            except OSError:
                logger.error(
                    "spaCy model missing. Run: python -m spacy download en_core_web_sm. "
                    "Falling back to simple tokenisation."
                )
                _nlp_failed = True
            except Exception as exc:
                logger.error(f"spaCy load failed unexpectedly: {exc}")
                _nlp_failed = True
    return _nlp


class KeywordExtractorService:
    """
    Keyword extraction using spaCy NLP with thread-safe singleton.
    Falls back to simple tokenisation if spaCy is unavailable.
    """

    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them',
        'their', 'my', 'your', 'his', 'her', 'its', 'our'
    }

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

        nlp = _get_nlp()
        if not nlp:
            # Fallback: simple tokenisation without NLP
            tokens = text.lower().translate(
                str.maketrans('', '', string.punctuation)
            ).split()
            return {
                t for t in tokens
                if len(t) >= min_length and t not in KeywordExtractorService.STOP_WORDS
            }

        doc = nlp(text.lower())
        keywords = set()

        # Extract nouns and proper nouns
        for token in doc:
            if token.pos_ in ('NOUN', 'PROPN') and len(token.text) >= min_length:
                lemma = token.lemma_.lower()
                if lemma not in KeywordExtractorService.STOP_WORDS:
                    keywords.add(lemma)

        # Extract noun phrases (1–3 words)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            if 1 <= len(phrase.split()) <= 3 and len(phrase) >= min_length:
                filtered = ' '.join(
                    w for w in phrase.split()
                    if w not in KeywordExtractorService.STOP_WORDS
                )
                if filtered:
                    keywords.add(filtered)

        return {kw for kw in keywords if len(kw) >= min_length}

    @staticmethod
    def calculate_keyword_frequency(text: str) -> Dict[str, int]:
        """Calculate frequency of each keyword in text."""
        if not text or not text.strip():
            return {}
        keywords = KeywordExtractorService.extract_keywords(text)
        text_lower = text.lower()
        return {kw: text_lower.count(kw) for kw in keywords if text_lower.count(kw) > 0}

    @staticmethod
    def weight_keywords_by_importance(keywords: Set[str], context: str) -> Dict[str, float]:
        """Assign importance weights to keywords based on context frequency."""
        if not keywords or not context:
            return {kw: 0.5 for kw in keywords}
        context_freq = KeywordExtractorService.calculate_keyword_frequency(context)
        max_freq = max(context_freq.values()) if context_freq else 1
        return {
            kw: 0.1 + 0.9 * (context_freq.get(kw, 0) / max_freq)
            for kw in keywords
        }
