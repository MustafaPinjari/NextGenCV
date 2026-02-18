"""
Template tags for optimized script loading.

Provides:
- Deferred script loading for non-critical JavaScript
- Async script loading
- Conditional loading based on page type

Usage in templates:
    {% load script_tags %}
    
    {% deferred_script 'js/main.js' %}
    {% async_script 'js/analytics.js' %}
    {% critical_script 'js/core.js' %}

Requirements: 14.4, 14.5
"""

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.simple_tag
def deferred_script(src, use_minified=None):
    """
    Load a JavaScript file with defer attribute for non-critical scripts.
    
    Args:
        src: Script path relative to static directory (e.g., 'js/main.js')
        use_minified: Use minified version if available (default: True in production)
    
    Returns:
        HTML script tag with defer attribute
    """
    if use_minified is None:
        use_minified = not settings.DEBUG
    
    # Use minified version in production
    if use_minified and not src.endswith('.min.js'):
        minified_src = src.replace('.js', '.min.js')
        script_url = static(minified_src)
    else:
        script_url = static(src)
    
    return mark_safe(f'<script src="{script_url}" defer></script>')


@register.simple_tag
def async_script(src, use_minified=None):
    """
    Load a JavaScript file with async attribute for independent scripts.
    
    Args:
        src: Script path relative to static directory
        use_minified: Use minified version if available (default: True in production)
    
    Returns:
        HTML script tag with async attribute
    """
    if use_minified is None:
        use_minified = not settings.DEBUG
    
    # Use minified version in production
    if use_minified and not src.endswith('.min.js'):
        minified_src = src.replace('.js', '.min.js')
        script_url = static(minified_src)
    else:
        script_url = static(src)
    
    return mark_safe(f'<script src="{script_url}" async></script>')


@register.simple_tag
def critical_script(src, use_minified=None):
    """
    Load a critical JavaScript file without defer/async.
    Use only for scripts that must execute before page render.
    
    Args:
        src: Script path relative to static directory
        use_minified: Use minified version if available (default: True in production)
    
    Returns:
        HTML script tag without defer/async
    """
    if use_minified is None:
        use_minified = not settings.DEBUG
    
    # Use minified version in production
    if use_minified and not src.endswith('.min.js'):
        minified_src = src.replace('.js', '.min.js')
        script_url = static(minified_src)
    else:
        script_url = static(src)
    
    return mark_safe(f'<script src="{script_url}"></script>')


@register.simple_tag
def inline_script(content):
    """
    Inline a small JavaScript snippet.
    Use for critical, small scripts that must execute immediately.
    
    Args:
        content: JavaScript code to inline
    
    Returns:
        HTML script tag with inline content
    """
    return mark_safe(f'<script>{content}</script>')


@register.simple_tag
def preload_script(src):
    """
    Preload a JavaScript file for faster loading.
    Use for scripts that will be needed soon.
    
    Args:
        src: Script path relative to static directory
    
    Returns:
        HTML link tag with rel="preload"
    """
    script_url = static(src)
    return mark_safe(f'<link rel="preload" href="{script_url}" as="script">')


@register.simple_tag
def module_script(src, use_minified=None):
    """
    Load a JavaScript module (ES6 modules).
    
    Args:
        src: Script path relative to static directory
        use_minified: Use minified version if available (default: True in production)
    
    Returns:
        HTML script tag with type="module"
    """
    if use_minified is None:
        use_minified = not settings.DEBUG
    
    # Use minified version in production
    if use_minified and not src.endswith('.min.js'):
        minified_src = src.replace('.js', '.min.js')
        script_url = static(minified_src)
    else:
        script_url = static(src)
    
    return mark_safe(f'<script type="module" src="{script_url}"></script>')


@register.filter
def is_production(value=None):
    """
    Check if running in production mode.
    
    Usage:
        {% if ''|is_production %}
    """
    return not settings.DEBUG
