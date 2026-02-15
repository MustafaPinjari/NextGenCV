"""
Caching utilities for analytics data.

Provides helper functions to cache expensive computations like
resume health scores and analytics data.

Requirements: 18.3
"""
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_resume_health_cache_key(resume_id):
    """
    Generate cache key for resume health score.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        str: Cache key
    """
    return f'resume_health_{resume_id}'


def get_analytics_cache_key(user_id):
    """
    Generate cache key for user analytics data.
    
    Args:
        user_id: ID of the user
        
    Returns:
        str: Cache key
    """
    return f'analytics_data_{user_id}'


def get_score_trends_cache_key(user_id):
    """
    Generate cache key for score trends data.
    
    Args:
        user_id: ID of the user
        
    Returns:
        str: Cache key
    """
    return f'score_trends_{user_id}'


def cache_resume_health(resume_id, health_score):
    """
    Cache resume health score.
    
    Args:
        resume_id: ID of the resume
        health_score: Health score to cache
        
    Returns:
        bool: True if cached successfully
    """
    cache_key = get_resume_health_cache_key(resume_id)
    timeout = getattr(settings, 'CACHE_TIMEOUT_RESUME_HEALTH', 300)
    
    try:
        cache.set(cache_key, health_score, timeout)
        logger.debug(f'Cached resume health for resume {resume_id}: {health_score}')
        return True
    except Exception as e:
        logger.error(f'Failed to cache resume health for resume {resume_id}: {e}')
        return False


def get_cached_resume_health(resume_id):
    """
    Get cached resume health score.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        float or None: Cached health score, or None if not cached
    """
    cache_key = get_resume_health_cache_key(resume_id)
    
    try:
        health_score = cache.get(cache_key)
        if health_score is not None:
            logger.debug(f'Cache hit for resume health: resume {resume_id}')
        return health_score
    except Exception as e:
        logger.error(f'Failed to get cached resume health for resume {resume_id}: {e}')
        return None


def invalidate_resume_health_cache(resume_id):
    """
    Invalidate cached resume health score.
    
    Should be called when resume is updated.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        bool: True if invalidated successfully
    """
    cache_key = get_resume_health_cache_key(resume_id)
    
    try:
        cache.delete(cache_key)
        logger.debug(f'Invalidated resume health cache for resume {resume_id}')
        return True
    except Exception as e:
        logger.error(f'Failed to invalidate resume health cache for resume {resume_id}: {e}')
        return False


def cache_analytics_data(user_id, analytics_data):
    """
    Cache analytics data for a user.
    
    Args:
        user_id: ID of the user
        analytics_data: Analytics data to cache
        
    Returns:
        bool: True if cached successfully
    """
    cache_key = get_analytics_cache_key(user_id)
    timeout = getattr(settings, 'CACHE_TIMEOUT_ANALYTICS', 300)
    
    try:
        cache.set(cache_key, analytics_data, timeout)
        logger.debug(f'Cached analytics data for user {user_id}')
        return True
    except Exception as e:
        logger.error(f'Failed to cache analytics data for user {user_id}: {e}')
        return False


def get_cached_analytics_data(user_id):
    """
    Get cached analytics data for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        dict or None: Cached analytics data, or None if not cached
    """
    cache_key = get_analytics_cache_key(user_id)
    
    try:
        analytics_data = cache.get(cache_key)
        if analytics_data is not None:
            logger.debug(f'Cache hit for analytics data: user {user_id}')
        return analytics_data
    except Exception as e:
        logger.error(f'Failed to get cached analytics data for user {user_id}: {e}')
        return None


def invalidate_analytics_cache(user_id):
    """
    Invalidate cached analytics data for a user.
    
    Should be called when user's resumes are updated or analyzed.
    
    Args:
        user_id: ID of the user
        
    Returns:
        bool: True if invalidated successfully
    """
    cache_key = get_analytics_cache_key(user_id)
    
    try:
        cache.delete(cache_key)
        logger.debug(f'Invalidated analytics cache for user {user_id}')
        return True
    except Exception as e:
        logger.error(f'Failed to invalidate analytics cache for user {user_id}: {e}')
        return False


def cache_score_trends(user_id, trends_data):
    """
    Cache score trends data for a user.
    
    Args:
        user_id: ID of the user
        trends_data: Trends data to cache
        
    Returns:
        bool: True if cached successfully
    """
    cache_key = get_score_trends_cache_key(user_id)
    timeout = getattr(settings, 'CACHE_TIMEOUT_SCORE_TRENDS', 600)
    
    try:
        cache.set(cache_key, trends_data, timeout)
        logger.debug(f'Cached score trends for user {user_id}')
        return True
    except Exception as e:
        logger.error(f'Failed to cache score trends for user {user_id}: {e}')
        return False


def get_cached_score_trends(user_id):
    """
    Get cached score trends data for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        dict or None: Cached trends data, or None if not cached
    """
    cache_key = get_score_trends_cache_key(user_id)
    
    try:
        trends_data = cache.get(cache_key)
        if trends_data is not None:
            logger.debug(f'Cache hit for score trends: user {user_id}')
        return trends_data
    except Exception as e:
        logger.error(f'Failed to get cached score trends for user {user_id}: {e}')
        return None


def invalidate_score_trends_cache(user_id):
    """
    Invalidate cached score trends for a user.
    
    Should be called when new analyses are created.
    
    Args:
        user_id: ID of the user
        
    Returns:
        bool: True if invalidated successfully
    """
    cache_key = get_score_trends_cache_key(user_id)
    
    try:
        cache.delete(cache_key)
        logger.debug(f'Invalidated score trends cache for user {user_id}')
        return True
    except Exception as e:
        logger.error(f'Failed to invalidate score trends cache for user {user_id}: {e}')
        return False


def invalidate_all_user_caches(user_id):
    """
    Invalidate all cached data for a user.
    
    Convenience function to clear all user-related caches.
    
    Args:
        user_id: ID of the user
        
    Returns:
        bool: True if all caches invalidated successfully
    """
    success = True
    success &= invalidate_analytics_cache(user_id)
    success &= invalidate_score_trends_cache(user_id)
    
    logger.debug(f'Invalidated all caches for user {user_id}')
    return success
