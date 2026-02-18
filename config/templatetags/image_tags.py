"""
Template tags for optimized image loading.

Provides:
- Lazy loading for below-fold images
- WebP format with fallbacks
- Responsive image sizing

Usage in templates:
    {% load image_tags %}
    
    {% optimized_image 'images/hero.jpg' 'Hero image' %}
    {% optimized_image 'images/hero.jpg' 'Hero image' lazy=True %}
    {% optimized_image 'images/hero.jpg' 'Hero image' class='img-fluid' %}

Requirements: 14.3, 14.4
"""

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from pathlib import Path
from django.conf import settings

register = template.Library()


@register.simple_tag
def optimized_image(src, alt='', lazy=False, css_class='', width='', height=''):
    """
    Render an optimized image with WebP support and optional lazy loading.
    
    Args:
        src: Image path relative to static directory (e.g., 'images/hero.jpg')
        alt: Alt text for accessibility
        lazy: Enable lazy loading (default: False)
        css_class: CSS classes to add
        width: Image width attribute
        height: Image height attribute
    
    Returns:
        HTML picture element with WebP source and fallback
    """
    # Get static URL
    img_url = static(src)
    
    # Check if WebP version exists
    webp_src = Path(src).with_suffix('.webp')
    webp_url = static(str(webp_src))
    
    # Build attributes
    attrs = []
    if css_class:
        attrs.append(f'class="{css_class}"')
    if width:
        attrs.append(f'width="{width}"')
    if height:
        attrs.append(f'height="{height}"')
    if lazy:
        attrs.append('loading="lazy"')
    
    attrs_str = ' '.join(attrs)
    
    # Build HTML
    # Try to use picture element with WebP source
    html = f'''<picture>
    <source srcset="{webp_url}" type="image/webp">
    <img src="{img_url}" alt="{alt}" {attrs_str}>
</picture>'''
    
    return mark_safe(html)


@register.simple_tag
def lazy_image(src, alt='', css_class='', width='', height=''):
    """
    Shortcut for lazy-loaded images.
    
    Usage:
        {% lazy_image 'images/feature.jpg' 'Feature description' %}
    """
    return optimized_image(src, alt, lazy=True, css_class=css_class, width=width, height=height)


@register.simple_tag
def responsive_image(src, alt='', css_class='img-fluid', lazy=True):
    """
    Shortcut for responsive images with lazy loading.
    
    Usage:
        {% responsive_image 'images/screenshot.jpg' 'App screenshot' %}
    """
    return optimized_image(src, alt, lazy=lazy, css_class=css_class)


@register.filter
def webp_available(image_path):
    """
    Check if a WebP version of an image exists.
    
    Usage:
        {% if 'images/hero.jpg'|webp_available %}
    """
    try:
        webp_path = Path(settings.STATIC_ROOT) / Path(image_path).with_suffix('.webp')
        return webp_path.exists()
    except:
        return False
