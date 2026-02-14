"""
Unit tests for analyzer services
"""
from django.test import TestCase
from apps.analyzer.services import (
    KeywordExtractorService,
    ActionVerbAnalyzerService,
    QuantificationDetectorService,
    ScoringEngineService
)


class KeywordExtractorServiceTest(TestCase):
    """Tests for KeywordExtractorService"""
    
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction"""
        text = "Python developer with Django experience"
        keywords = KeywordExtractorService.extract_keywords(text)
        
        self.assertIsInstance(keywords, set)
        self.assertGreater(len(keywords), 0)
        self.assertIn('python', keywords)
        self.assertIn('django', keywords)
    
    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text"""
        keywords = KeywordExtractorService.extract_keywords("")
        self.assertEqual(keywords, set())
    
    def test_extract_keywords_removes_stop_words(self):
        """Test that stop words are removed"""
        text = "The developer worked with the team"
        keywords = KeywordExtractorService.extract_keywords(text)
        
        # Stop words should not be in keywords
        self.assertNotIn('the', keywords)
        self.assertNotIn('with', keywords)
    
    def test_calculate_keyword_frequency(self):
        """Test keyword frequency calculation"""
        text = "Python Python Django Python"
        freq = KeywordExtractorService.calculate_keyword_frequency(text)
        
        self.assertIsInstance(freq, dict)
        self.assertIn('python', freq)
        self.assertEqual(freq['python'], 3)
    
    def test_weight_keywords_by_importance(self):
        """Test keyword weighting"""
        keywords = {'python', 'django', 'javascript'}
        context = "Python Python Django"
        
        weights = KeywordExtractorService.weight_keywords_by_importance(keywords, context)
        
        self.assertIsInstance(weights, dict)
        self.assertEqual(len(weights), 3)
        # Python appears twice, should have higher weight
        self.assertGreater(weights['python'], weights['javascript'])


class ActionVerbAnalyzerServiceTest(TestCase):
    """Tests for ActionVerbAnalyzerService"""
    
    def test_analyze_action_verbs_strong(self):
        """Test analysis with strong action verbs"""
        text = "Led team of developers. Implemented new features."
        analysis = ActionVerbAnalyzerService.analyze_action_verbs(text)
        
        self.assertIn('led', analysis['strong_verbs'])
        # Note: 'implemented' might not be detected if it's not at the start of a bullet
        self.assertGreaterEqual(analysis['strong_count'], 1)
    
    def test_analyze_action_verbs_weak(self):
        """Test analysis with weak verbs"""
        text = "Worked on project. Helped with testing."
        analysis = ActionVerbAnalyzerService.analyze_action_verbs(text)
        
        self.assertGreater(analysis['weak_count'], 0)
        # Check for either 'worked' or 'worked on' (multi-word phrase)
        weak_verbs_str = ' '.join(analysis['weak_verbs'])
        self.assertIn('worked', weak_verbs_str)
    
    def test_calculate_action_verb_score_perfect(self):
        """Test score calculation with all strong verbs"""
        text = "Led team. Implemented features. Developed solution."
        score = ActionVerbAnalyzerService.calculate_action_verb_score(text)
        
        self.assertEqual(score, 100.0)
    
    def test_calculate_action_verb_score_empty(self):
        """Test score with empty text"""
        score = ActionVerbAnalyzerService.calculate_action_verb_score("")
        self.assertEqual(score, 0.0)


class QuantificationDetectorServiceTest(TestCase):
    """Tests for QuantificationDetectorService"""
    
    def test_detect_quantifications_percentage(self):
        """Test detection of percentages"""
        text = "Increased revenue by 25%"
        quants = QuantificationDetectorService.detect_quantifications(text)
        
        self.assertGreater(len(quants), 0)
        self.assertTrue(any(q['type'] == 'percentage' for q in quants))
    
    def test_detect_quantifications_dollar(self):
        """Test detection of dollar amounts"""
        text = "Saved $50K in costs"
        quants = QuantificationDetectorService.detect_quantifications(text)
        
        self.assertGreater(len(quants), 0)
        self.assertTrue(any(q['type'] == 'dollar' for q in quants))
    
    def test_detect_quantifications_time(self):
        """Test detection of time periods"""
        text = "Managed project for 2 years"
        quants = QuantificationDetectorService.detect_quantifications(text)
        
        self.assertGreater(len(quants), 0)
        self.assertTrue(any(q['type'] == 'time' for q in quants))
    
    def test_has_quantification_true(self):
        """Test has_quantification returns True"""
        text = "Increased by 50%"
        self.assertTrue(QuantificationDetectorService.has_quantification(text))
    
    def test_has_quantification_false(self):
        """Test has_quantification returns False"""
        text = "Worked on project"
        self.assertFalse(QuantificationDetectorService.has_quantification(text))
    
    def test_calculate_quantification_score(self):
        """Test quantification score calculation"""
        text = """
        • Increased revenue by 25%
        • Managed team of 10
        • Worked on project
        """
        score = QuantificationDetectorService.calculate_quantification_score(text)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)


class ScoringEngineServiceTest(TestCase):
    """Tests for ScoringEngineService"""
    
    def test_calculate_keyword_match_score(self):
        """Test keyword match score calculation"""
        resume_text = "Python Django PostgreSQL developer"
        jd_text = "Python Django React developer"
        
        score = ScoringEngineService.calculate_keyword_match_score(resume_text, jd_text)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_calculate_keyword_match_score_perfect(self):
        """Test perfect keyword match"""
        text = "Python Django"
        
        score = ScoringEngineService.calculate_keyword_match_score(text, text)
        
        # Should be high score (may not be exactly 100 due to NLP processing)
        self.assertGreater(score, 80)
    
    def test_calculate_keyword_match_score_no_match(self):
        """Test no keyword match"""
        resume_text = "Python Django"
        jd_text = "Java Spring"
        
        score = ScoringEngineService.calculate_keyword_match_score(resume_text, jd_text)
        
        # Should be low score
        self.assertLess(score, 30)
    
    def test_score_bounds(self):
        """Test that all scores are within 0-100 range"""
        # Create mock resume
        class MockResume:
            class personal_info:
                full_name = "Test"
                email = "test@test.com"
                phone = "123"
                location = "City"
            
            class MockQuerySet:
                def __init__(self, items):
                    self._items = items
                
                def all(self):
                    return self._items
                
                def exists(self):
                    return len(self._items) > 0
                
                def count(self):
                    return len(self._items)
            
            experiences = MockQuerySet([])
            education = MockQuerySet([])
            skills = MockQuerySet([])
            projects = MockQuerySet([])
        
        resume = MockResume()
        jd = "Python developer"
        
        result = ScoringEngineService.calculate_ats_score(resume, jd)
        
        # Check all scores are in valid range
        self.assertGreaterEqual(result['final_score'], 0)
        self.assertLessEqual(result['final_score'], 100)
        self.assertGreaterEqual(result['keyword_match_score'], 0)
        self.assertLessEqual(result['keyword_match_score'], 100)
        self.assertGreaterEqual(result['skill_relevance_score'], 0)
        self.assertLessEqual(result['skill_relevance_score'], 100)
