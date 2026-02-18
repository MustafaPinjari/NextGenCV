"""
Performance monitoring views for collecting and analyzing performance metrics.

Requirements: 14.6
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger('performance')


@csrf_exempt
@require_http_methods(["POST"])
def collect_metrics(request):
    """
    Collect performance metrics from client-side monitoring.
    
    Endpoint: /api/performance/metrics/
    Method: POST
    
    Expected payload:
    {
        "url": "https://example.com/page",
        "userAgent": "Mozilla/5.0...",
        "timestamp": "2024-01-01T12:00:00Z",
        "metrics": {
            "FCP": 1200,
            "LCP": 2000,
            "FID": 50,
            "CLS": 0.05,
            "TTFB": 400,
            "pageLoadTime": 3000,
            "domContentLoadedTime": 1500,
            "resourceLoadTime": 1500,
            "avgFPS": 58.5
        }
    }
    """
    try:
        data = json.loads(request.body)
        
        # Extract metrics
        url = data.get('url', '')
        user_agent = data.get('userAgent', '')
        timestamp = data.get('timestamp', '')
        metrics = data.get('metrics', {})
        
        # Log metrics
        logger.info(
            f"Performance metrics received: "
            f"URL={url}, "
            f"FCP={metrics.get('FCP')}, "
            f"LCP={metrics.get('LCP')}, "
            f"FID={metrics.get('FID')}, "
            f"CLS={metrics.get('CLS')}, "
            f"TTFB={metrics.get('TTFB')}, "
            f"PageLoad={metrics.get('pageLoadTime')}, "
            f"FPS={metrics.get('avgFPS')}"
        )
        
        # Store in cache for aggregation
        cache_key = f"perf_metrics_{datetime.now().strftime('%Y%m%d_%H')}"
        cached_metrics = cache.get(cache_key, [])
        cached_metrics.append({
            'url': url,
            'timestamp': timestamp,
            'metrics': metrics
        })
        cache.set(cache_key, cached_metrics, timeout=3600)  # 1 hour
        
        # Check for performance issues
        issues = []
        
        if metrics.get('FCP', 0) > 1800:
            issues.append('Slow First Contentful Paint')
        
        if metrics.get('LCP', 0) > 2500:
            issues.append('Slow Largest Contentful Paint')
        
        if metrics.get('FID', 0) > 100:
            issues.append('High First Input Delay')
        
        if metrics.get('CLS', 0) > 0.1:
            issues.append('High Cumulative Layout Shift')
        
        if metrics.get('avgFPS', 60) < 50:
            issues.append('Low frame rate')
        
        if issues:
            logger.warning(f"Performance issues detected on {url}: {', '.join(issues)}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Metrics received',
            'issues': issues
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error processing performance metrics: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


@require_http_methods(["GET"])
def performance_dashboard(request):
    """
    Display performance metrics dashboard.
    
    Endpoint: /performance/dashboard/
    Method: GET
    """
    # Get metrics from cache for the last 24 hours
    now = datetime.now()
    all_metrics = []
    
    for hour in range(24):
        timestamp = now - timedelta(hours=hour)
        cache_key = f"perf_metrics_{timestamp.strftime('%Y%m%d_%H')}"
        cached_metrics = cache.get(cache_key, [])
        all_metrics.extend(cached_metrics)
    
    # Calculate aggregates
    if all_metrics:
        fcp_values = [m['metrics'].get('FCP', 0) for m in all_metrics if m['metrics'].get('FCP')]
        lcp_values = [m['metrics'].get('LCP', 0) for m in all_metrics if m['metrics'].get('LCP')]
        fid_values = [m['metrics'].get('FID', 0) for m in all_metrics if m['metrics'].get('FID')]
        cls_values = [m['metrics'].get('CLS', 0) for m in all_metrics if m['metrics'].get('CLS')]
        fps_values = [m['metrics'].get('avgFPS', 0) for m in all_metrics if m['metrics'].get('avgFPS')]
        
        aggregates = {
            'total_samples': len(all_metrics),
            'avg_fcp': sum(fcp_values) / len(fcp_values) if fcp_values else 0,
            'avg_lcp': sum(lcp_values) / len(lcp_values) if lcp_values else 0,
            'avg_fid': sum(fid_values) / len(fid_values) if fid_values else 0,
            'avg_cls': sum(cls_values) / len(cls_values) if cls_values else 0,
            'avg_fps': sum(fps_values) / len(fps_values) if fps_values else 0,
            'p75_fcp': sorted(fcp_values)[int(len(fcp_values) * 0.75)] if fcp_values else 0,
            'p75_lcp': sorted(lcp_values)[int(len(lcp_values) * 0.75)] if lcp_values else 0,
        }
    else:
        aggregates = {
            'total_samples': 0,
            'avg_fcp': 0,
            'avg_lcp': 0,
            'avg_fid': 0,
            'avg_cls': 0,
            'avg_fps': 0,
            'p75_fcp': 0,
            'p75_lcp': 0,
        }
    
    return JsonResponse({
        'status': 'success',
        'period': '24 hours',
        'aggregates': aggregates,
        'recent_metrics': all_metrics[-10:] if all_metrics else []
    })


@require_http_methods(["GET"])
def performance_summary(request):
    """
    Get a quick summary of performance metrics.
    
    Endpoint: /api/performance/summary/
    Method: GET
    """
    # Get metrics from the last hour
    cache_key = f"perf_metrics_{datetime.now().strftime('%Y%m%d_%H')}"
    cached_metrics = cache.get(cache_key, [])
    
    if not cached_metrics:
        return JsonResponse({
            'status': 'success',
            'message': 'No metrics available',
            'summary': {}
        })
    
    # Calculate summary
    fcp_values = [m['metrics'].get('FCP', 0) for m in cached_metrics if m['metrics'].get('FCP')]
    lcp_values = [m['metrics'].get('LCP', 0) for m in cached_metrics if m['metrics'].get('LCP')]
    
    summary = {
        'samples': len(cached_metrics),
        'avg_fcp': sum(fcp_values) / len(fcp_values) if fcp_values else 0,
        'avg_lcp': sum(lcp_values) / len(lcp_values) if lcp_values else 0,
        'status': 'good' if (
            (sum(fcp_values) / len(fcp_values) if fcp_values else 0) < 1800 and
            (sum(lcp_values) / len(lcp_values) if lcp_values else 0) < 2500
        ) else 'needs_improvement'
    }
    
    return JsonResponse({
        'status': 'success',
        'summary': summary
    })
