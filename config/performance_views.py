"""
Performance monitoring views for development.

Provides a simple dashboard to view performance metrics.

Requirements: 18.4
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import os


@staff_member_required
def performance_dashboard(request):
    """
    Display performance monitoring dashboard.
    
    Shows:
    - Recent slow queries
    - Recent slow requests
    - Performance statistics
    
    Only accessible to staff members in DEBUG mode.
    """
    if not settings.DEBUG:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Performance monitoring is only available in DEBUG mode.")
    
    # Read performance log
    log_file = settings.BASE_DIR / 'logs' / 'performance.log'
    
    slow_requests = []
    slow_queries = []
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                recent_lines = lines[-100:]
                
                for line in recent_lines:
                    if 'Slow request detected' in line:
                        slow_requests.append(line.strip())
                    elif 'Slow query detected' in line:
                        slow_queries.append(line.strip())
        except Exception as e:
            pass
    
    context = {
        'slow_requests': slow_requests[-20:],  # Last 20 slow requests
        'slow_queries': slow_queries[-20:],  # Last 20 slow queries
        'monitoring_enabled': settings.PERFORMANCE_MONITORING_ENABLED,
        'slow_request_threshold': settings.PERFORMANCE_SLOW_REQUEST_THRESHOLD,
        'slow_query_threshold': settings.PERFORMANCE_SLOW_QUERY_THRESHOLD,
    }
    
    return render(request, 'performance/dashboard.html', context)
