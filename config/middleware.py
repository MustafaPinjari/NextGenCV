"""
Custom middleware for ATS Resume Builder
"""
import os
from pathlib import Path
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.http import FileResponse, Http404


class GzipStaticMiddleware:
    """
    Middleware to serve pre-compressed gzip files for static assets.
    
    If a .gz version of a static file exists and the client accepts gzip encoding,
    serve the compressed version instead.
    
    Requirements: 14.4
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only process static file requests
        if not request.path.startswith('/static/'):
            return response
        
        # Check if client accepts gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in accept_encoding.lower():
            return response
        
        # Check if this is a CSS or JS file
        if not (request.path.endswith('.css') or request.path.endswith('.js')):
            return response
        
        # Check if gzipped version exists
        from django.conf import settings
        static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else None
        
        if static_root and static_root.exists():
            # In production with collected static files
            file_path = static_root / request.path.replace('/static/', '', 1)
            gzip_path = Path(str(file_path) + '.gz')
            
            if gzip_path.exists():
                try:
                    # Serve the gzipped file
                    response = FileResponse(open(gzip_path, 'rb'))
                    response['Content-Encoding'] = 'gzip'
                    
                    # Set appropriate content type
                    if request.path.endswith('.css'):
                        response['Content-Type'] = 'text/css'
                    elif request.path.endswith('.js'):
                        response['Content-Type'] = 'application/javascript'
                    
                    # Add cache headers
                    patch_cache_control(
                        response,
                        public=True,
                        max_age=31536000,
                        immutable=True
                    )
                    
                    return response
                except (IOError, OSError):
                    pass
        
        return response


class StaticFilesCacheMiddleware:
    """
    Middleware to add caching headers for static files
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cache headers for static files
        if request.path.startswith('/static/'):
            # Cache static files for 1 year (31536000 seconds)
            patch_cache_control(
                response,
                public=True,
                max_age=31536000,
                immutable=True
            )
        
        # Add cache headers for media files
        elif request.path.startswith('/media/'):
            # Cache media files for 1 week (604800 seconds)
            patch_cache_control(
                response,
                public=True,
                max_age=604800
            )
        
        # Don't cache dynamic pages
        elif not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            add_never_cache_headers(response)
        
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response


class PerformanceMonitoringMiddleware:
    """
    Middleware to monitor request performance and log slow queries/requests.
    
    Tracks:
    - Request processing time
    - Database query count and time
    - Slow queries and requests
    
    Requirements: 18.4
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        from django.db import connection, reset_queries
        import time
        import logging
        
        # Skip if monitoring is disabled
        if not getattr(settings, 'PERFORMANCE_MONITORING_ENABLED', False):
            return self.get_response(request)
        
        logger = logging.getLogger('performance')
        
        # Reset query log
        reset_queries()
        
        # Record start time
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Get query statistics
        query_count = len(connection.queries)
        query_time = sum(float(q['time']) for q in connection.queries)
        
        # Log performance metrics
        log_data = {
            'path': request.path,
            'method': request.method,
            'duration': f'{duration:.3f}s',
            'query_count': query_count,
            'query_time': f'{query_time:.3f}s',
            'status': response.status_code,
        }
        
        # Check for slow requests
        slow_request_threshold = getattr(settings, 'PERFORMANCE_SLOW_REQUEST_THRESHOLD', 2.0)
        if getattr(settings, 'PERFORMANCE_LOG_SLOW_REQUESTS', True) and duration > slow_request_threshold:
            logger.warning(f'Slow request detected: {log_data}')
        else:
            logger.debug(f'Request performance: {log_data}')
        
        # Check for slow queries
        slow_query_threshold = getattr(settings, 'PERFORMANCE_SLOW_QUERY_THRESHOLD', 0.5)
        if getattr(settings, 'PERFORMANCE_LOG_SLOW_QUERIES', True):
            for query in connection.queries:
                query_duration = float(query['time'])
                if query_duration > slow_query_threshold:
                    logger.warning(
                        f'Slow query detected ({query_duration:.3f}s): {query["sql"][:200]}'
                    )
        
        # Add performance headers to response (for debugging)
        if settings.DEBUG:
            response['X-Request-Duration'] = f'{duration:.3f}s'
            response['X-Query-Count'] = str(query_count)
            response['X-Query-Time'] = f'{query_time:.3f}s'
        
        return response
