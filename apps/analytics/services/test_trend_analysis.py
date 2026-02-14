"""
Unit tests for TrendAnalysisService
"""
from django.test import TestCase
from apps.analytics.services.trend_analysis import TrendAnalysisService


class TrendAnalysisServiceTest(TestCase):
    """Test cases for TrendAnalysisService"""
    
    def test_calculate_moving_average_basic(self):
        """Test basic moving average calculation"""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        window_size = 3
        
        result = TrendAnalysisService.calculate_moving_average(values, window_size)
        
        self.assertEqual(len(result), len(values))
        self.assertEqual(result[0], 10.0)  # First value
        self.assertEqual(result[1], 15.0)  # (10 + 20) / 2
        self.assertEqual(result[2], 20.0)  # (10 + 20 + 30) / 3
        self.assertEqual(result[3], 30.0)  # (20 + 30 + 40) / 3
        self.assertEqual(result[4], 40.0)  # (30 + 40 + 50) / 3
    
    def test_calculate_moving_average_window_larger_than_data(self):
        """Test moving average when window is larger than data"""
        values = [10.0, 20.0, 30.0]
        window_size = 10
        
        result = TrendAnalysisService.calculate_moving_average(values, window_size)
        
        self.assertEqual(len(result), len(values))
        # All values should be cumulative averages
        self.assertEqual(result[0], 10.0)
        self.assertEqual(result[1], 15.0)
        self.assertEqual(result[2], 20.0)
    
    def test_calculate_moving_average_empty_list(self):
        """Test moving average with empty list"""
        result = TrendAnalysisService.calculate_moving_average([], 5)
        self.assertEqual(len(result), 0)
    
    def test_calculate_moving_average_invalid_window(self):
        """Test moving average with invalid window size"""
        values = [10.0, 20.0, 30.0]
        
        with self.assertRaises(ValueError):
            TrendAnalysisService.calculate_moving_average(values, 0)
        
        with self.assertRaises(ValueError):
            TrendAnalysisService.calculate_moving_average(values, -1)
    
    def test_calculate_improvement_rate_improving(self):
        """Test improvement rate calculation for improving scores"""
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        rate = TrendAnalysisService.calculate_improvement_rate(scores)
        
        self.assertGreater(rate, 0)
        self.assertAlmostEqual(rate, 5.0, places=2)
    
    def test_calculate_improvement_rate_declining(self):
        """Test improvement rate calculation for declining scores"""
        scores = [80.0, 75.0, 70.0, 65.0, 60.0]
        
        rate = TrendAnalysisService.calculate_improvement_rate(scores)
        
        self.assertLess(rate, 0)
        self.assertAlmostEqual(rate, -5.0, places=2)
    
    def test_calculate_improvement_rate_stable(self):
        """Test improvement rate calculation for stable scores"""
        scores = [70.0, 70.0, 70.0, 70.0, 70.0]
        
        rate = TrendAnalysisService.calculate_improvement_rate(scores)
        
        self.assertAlmostEqual(rate, 0.0, places=2)
    
    def test_calculate_improvement_rate_empty_list(self):
        """Test improvement rate with empty list"""
        rate = TrendAnalysisService.calculate_improvement_rate([])
        self.assertEqual(rate, 0.0)
    
    def test_calculate_improvement_rate_single_value(self):
        """Test improvement rate with single value"""
        rate = TrendAnalysisService.calculate_improvement_rate([70.0])
        self.assertEqual(rate, 0.0)
    
    def test_identify_trend_direction_improving(self):
        """Test trend direction identification for improving scores"""
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        direction = TrendAnalysisService.identify_trend_direction(scores)
        
        self.assertEqual(direction, 'improving')
    
    def test_identify_trend_direction_declining(self):
        """Test trend direction identification for declining scores"""
        scores = [80.0, 75.0, 70.0, 65.0, 60.0]
        
        direction = TrendAnalysisService.identify_trend_direction(scores)
        
        self.assertEqual(direction, 'declining')
    
    def test_identify_trend_direction_stable(self):
        """Test trend direction identification for stable scores"""
        scores = [70.0, 70.2, 69.8, 70.1, 70.0]
        
        direction = TrendAnalysisService.identify_trend_direction(scores)
        
        self.assertEqual(direction, 'stable')
    
    def test_identify_trend_direction_no_data(self):
        """Test trend direction with no data"""
        direction = TrendAnalysisService.identify_trend_direction([])
        self.assertEqual(direction, 'no_data')
    
    def test_identify_trend_direction_single_value(self):
        """Test trend direction with single value"""
        direction = TrendAnalysisService.identify_trend_direction([70.0])
        self.assertEqual(direction, 'stable')
    
    def test_calculate_volatility_basic(self):
        """Test volatility calculation"""
        scores = [60.0, 70.0, 65.0, 75.0, 68.0]
        
        volatility = TrendAnalysisService.calculate_volatility(scores)
        
        self.assertGreater(volatility, 0)
        self.assertIsInstance(volatility, float)
    
    def test_calculate_volatility_no_variation(self):
        """Test volatility with no variation"""
        scores = [70.0, 70.0, 70.0, 70.0, 70.0]
        
        volatility = TrendAnalysisService.calculate_volatility(scores)
        
        self.assertEqual(volatility, 0.0)
    
    def test_calculate_volatility_empty_list(self):
        """Test volatility with empty list"""
        volatility = TrendAnalysisService.calculate_volatility([])
        self.assertEqual(volatility, 0.0)
    
    def test_calculate_volatility_single_value(self):
        """Test volatility with single value"""
        volatility = TrendAnalysisService.calculate_volatility([70.0])
        self.assertEqual(volatility, 0.0)
    
    def test_detect_anomalies_basic(self):
        """Test anomaly detection"""
        scores = [70.0, 71.0, 69.0, 70.5, 95.0, 70.0, 71.0]
        
        anomalies = TrendAnalysisService.detect_anomalies(scores, threshold=2.0)
        
        self.assertGreater(len(anomalies), 0)
        # The 95.0 score should be detected as anomaly
        anomaly_scores = [score for _, score in anomalies]
        self.assertIn(95.0, anomaly_scores)
    
    def test_detect_anomalies_no_anomalies(self):
        """Test anomaly detection with no anomalies"""
        scores = [70.0, 71.0, 69.0, 70.5, 71.5, 70.0, 71.0]
        
        anomalies = TrendAnalysisService.detect_anomalies(scores, threshold=2.0)
        
        self.assertEqual(len(anomalies), 0)
    
    def test_detect_anomalies_empty_list(self):
        """Test anomaly detection with empty list"""
        anomalies = TrendAnalysisService.detect_anomalies([])
        self.assertEqual(len(anomalies), 0)
    
    def test_detect_anomalies_insufficient_data(self):
        """Test anomaly detection with insufficient data"""
        anomalies = TrendAnalysisService.detect_anomalies([70.0, 71.0])
        self.assertEqual(len(anomalies), 0)
    
    def test_calculate_trend_strength_strong_trend(self):
        """Test trend strength calculation for strong trend"""
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        strength = TrendAnalysisService.calculate_trend_strength(scores)
        
        self.assertGreater(strength, 0.9)  # Should be close to 1 for perfect linear trend
        self.assertLessEqual(strength, 1.0)
    
    def test_calculate_trend_strength_weak_trend(self):
        """Test trend strength calculation for weak trend"""
        scores = [70.0, 65.0, 75.0, 68.0, 72.0]
        
        strength = TrendAnalysisService.calculate_trend_strength(scores)
        
        self.assertGreaterEqual(strength, 0.0)
        self.assertLessEqual(strength, 1.0)
    
    def test_calculate_trend_strength_no_trend(self):
        """Test trend strength calculation for no trend"""
        scores = [70.0, 70.0, 70.0, 70.0, 70.0]
        
        strength = TrendAnalysisService.calculate_trend_strength(scores)
        
        # No variation means no trend
        self.assertEqual(strength, 0.0)
    
    def test_calculate_trend_strength_empty_list(self):
        """Test trend strength with empty list"""
        strength = TrendAnalysisService.calculate_trend_strength([])
        self.assertEqual(strength, 0.0)
    
    def test_calculate_trend_strength_single_value(self):
        """Test trend strength with single value"""
        strength = TrendAnalysisService.calculate_trend_strength([70.0])
        self.assertEqual(strength, 0.0)
    
    def test_get_trend_summary_comprehensive(self):
        """Test comprehensive trend summary"""
        scores = [60.0, 65.0, 70.0, 75.0, 80.0]
        
        summary = TrendAnalysisService.get_trend_summary(scores, window_size=3)
        
        self.assertIn('direction', summary)
        self.assertIn('improvement_rate', summary)
        self.assertIn('volatility', summary)
        self.assertIn('trend_strength', summary)
        self.assertIn('moving_average', summary)
        self.assertIn('anomalies', summary)
        self.assertIn('summary', summary)
        
        self.assertEqual(summary['direction'], 'improving')
        self.assertGreater(summary['improvement_rate'], 0)
        self.assertEqual(len(summary['moving_average']), len(scores))
    
    def test_get_trend_summary_no_data(self):
        """Test trend summary with no data"""
        summary = TrendAnalysisService.get_trend_summary([])
        
        self.assertEqual(summary['direction'], 'no_data')
        self.assertEqual(summary['improvement_rate'], 0.0)
        self.assertEqual(summary['volatility'], 0.0)
        self.assertEqual(len(summary['moving_average']), 0)
    
    def test_get_trend_summary_declining(self):
        """Test trend summary for declining scores"""
        scores = [80.0, 75.0, 70.0, 65.0, 60.0]
        
        summary = TrendAnalysisService.get_trend_summary(scores)
        
        self.assertEqual(summary['direction'], 'declining')
        self.assertLess(summary['improvement_rate'], 0)
        self.assertIn('declining', summary['summary'].lower())
    
    def test_get_trend_summary_stable(self):
        """Test trend summary for stable scores"""
        scores = [70.0, 70.2, 69.8, 70.1, 70.0]
        
        summary = TrendAnalysisService.get_trend_summary(scores)
        
        self.assertEqual(summary['direction'], 'stable')
        self.assertIn('stable', summary['summary'].lower())
    
    def test_get_trend_summary_high_volatility(self):
        """Test trend summary with high volatility"""
        scores = [60.0, 80.0, 65.0, 85.0, 70.0]
        
        summary = TrendAnalysisService.get_trend_summary(scores)
        
        self.assertGreater(summary['volatility'], 10)
        self.assertIn('variation', summary['summary'].lower())
