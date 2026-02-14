# Trend analysis service
from typing import List, Dict, Tuple
from statistics import mean, stdev


class TrendAnalysisService:
    """
    Service for analyzing trends in resume metrics over time.
    Provides statistical analysis of score changes and improvement patterns.
    """
    
    @staticmethod
    def calculate_moving_average(values: List[float], window_size: int = 5) -> List[float]:
        """
        Calculate moving average for a list of values.
        
        Args:
            values: List of numeric values
            window_size: Size of the moving window (default: 5)
            
        Returns:
            List[float]: Moving average values
        """
        if not values:
            return []
        
        if window_size <= 0:
            raise ValueError("Window size must be positive")
        
        moving_avg = []
        for i in range(len(values)):
            # Calculate average of window ending at current position
            start_idx = max(0, i - window_size + 1)
            window = values[start_idx:i + 1]
            avg = sum(window) / len(window)
            moving_avg.append(round(avg, 2))
        
        return moving_avg
    
    @staticmethod
    def calculate_improvement_rate(scores: List[float]) -> float:
        """
        Calculate the rate of improvement across scores.
        
        Uses linear regression slope to determine improvement rate.
        Positive values indicate improvement, negative indicate decline.
        
        Args:
            scores: List of scores in chronological order
            
        Returns:
            float: Improvement rate (change per data point)
        """
        if not scores or len(scores) < 2:
            return 0.0
        
        n = len(scores)
        
        # Simple linear regression: y = mx + b
        # Calculate slope (m) which represents improvement rate
        x_values = list(range(n))
        x_mean = mean(x_values)
        y_mean = mean(scores)
        
        # Calculate slope using least squares method
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, scores))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        return round(slope, 4)
    
    @staticmethod
    def identify_trend_direction(scores: List[float], threshold: float = 0.5) -> str:
        """
        Identify the overall trend direction based on improvement rate.
        
        Args:
            scores: List of scores in chronological order
            threshold: Minimum absolute improvement rate to be considered trending
            
        Returns:
            str: Trend direction ('improving', 'declining', 'stable', 'no_data')
        """
        if not scores:
            return 'no_data'
        
        if len(scores) < 2:
            return 'stable'
        
        improvement_rate = TrendAnalysisService.calculate_improvement_rate(scores)
        
        if improvement_rate > threshold:
            return 'improving'
        elif improvement_rate < -threshold:
            return 'declining'
        else:
            return 'stable'
    
    @staticmethod
    def calculate_volatility(scores: List[float]) -> float:
        """
        Calculate volatility (standard deviation) of scores.
        
        Higher volatility indicates more variation in scores over time.
        
        Args:
            scores: List of scores
            
        Returns:
            float: Standard deviation of scores
        """
        if not scores or len(scores) < 2:
            return 0.0
        
        return round(stdev(scores), 2)
    
    @staticmethod
    def detect_anomalies(scores: List[float], threshold: float = 2.0) -> List[Tuple[int, float]]:
        """
        Detect anomalous scores that deviate significantly from the mean.
        
        Uses z-score method to identify outliers.
        
        Args:
            scores: List of scores
            threshold: Number of standard deviations to consider anomalous (default: 2.0)
            
        Returns:
            List[Tuple[int, float]]: List of (index, score) tuples for anomalies
        """
        if not scores or len(scores) < 3:
            return []
        
        mean_score = mean(scores)
        std_dev = stdev(scores)
        
        if std_dev == 0:
            return []
        
        anomalies = []
        for i, score in enumerate(scores):
            z_score = abs((score - mean_score) / std_dev)
            if z_score > threshold:
                anomalies.append((i, score))
        
        return anomalies
    
    @staticmethod
    def calculate_trend_strength(scores: List[float]) -> float:
        """
        Calculate the strength of the trend (R-squared value).
        
        Returns a value between 0 and 1, where:
        - 0 indicates no trend
        - 1 indicates perfect linear trend
        
        Args:
            scores: List of scores in chronological order
            
        Returns:
            float: R-squared value indicating trend strength
        """
        if not scores or len(scores) < 2:
            return 0.0
        
        n = len(scores)
        x_values = list(range(n))
        
        # Calculate means
        x_mean = mean(x_values)
        y_mean = mean(scores)
        
        # Calculate slope and intercept
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, scores))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        ss_total = sum((y - y_mean) ** 2 for y in scores)
        ss_residual = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, scores))
        
        if ss_total == 0:
            return 0.0
        
        r_squared = 1 - (ss_residual / ss_total)
        
        return round(max(0.0, min(1.0, r_squared)), 4)
    
    @staticmethod
    def get_trend_summary(scores: List[float], window_size: int = 5) -> Dict:
        """
        Get comprehensive trend summary with all metrics.
        
        Args:
            scores: List of scores in chronological order
            window_size: Window size for moving average
            
        Returns:
            Dict: Comprehensive trend analysis
        """
        if not scores:
            return {
                'direction': 'no_data',
                'improvement_rate': 0.0,
                'volatility': 0.0,
                'trend_strength': 0.0,
                'moving_average': [],
                'anomalies': [],
                'summary': 'No data available for trend analysis.'
            }
        
        direction = TrendAnalysisService.identify_trend_direction(scores)
        improvement_rate = TrendAnalysisService.calculate_improvement_rate(scores)
        volatility = TrendAnalysisService.calculate_volatility(scores)
        trend_strength = TrendAnalysisService.calculate_trend_strength(scores)
        moving_avg = TrendAnalysisService.calculate_moving_average(scores, window_size)
        anomalies = TrendAnalysisService.detect_anomalies(scores)
        
        # Generate summary text
        if direction == 'improving':
            summary = f"Your scores are improving at a rate of {improvement_rate:.2f} points per analysis."
        elif direction == 'declining':
            summary = f"Your scores are declining at a rate of {abs(improvement_rate):.2f} points per analysis."
        else:
            summary = "Your scores are relatively stable with no significant trend."
        
        if volatility > 10:
            summary += " There is high variation in your scores."
        
        return {
            'direction': direction,
            'improvement_rate': improvement_rate,
            'volatility': volatility,
            'trend_strength': trend_strength,
            'moving_average': moving_avg,
            'anomalies': anomalies,
            'summary': summary
        }

