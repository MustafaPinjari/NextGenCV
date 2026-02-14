"""
Custom middleware for ATS Resume Builder
"""
from django.utils.cache import add_never_cache_headers, patch_cache_control


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
