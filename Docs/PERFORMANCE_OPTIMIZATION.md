# Performance Optimization Guide

This document describes the performance optimization strategy for NextGenCV, including CSS, JavaScript, image optimization, and performance monitoring.

## Overview

The performance optimization implementation addresses Requirements 14.1-14.6:
- **14.1**: Optimize Bootstrap via SCSS overrides
- **14.2**: Remove unused CSS components
- **14.3**: Lazy load large images
- **14.4**: Compress static assets
- **14.5**: Avoid heavy JavaScript libraries
- **14.6**: Monitor animation frame rates and Core Web Vitals

## Performance Targets

### Core Web Vitals
- **First Contentful Paint (FCP)**: < 1.8 seconds
- **Largest Contentful Paint (LCP)**: < 2.5 seconds
- **First Input Delay (FID)**: < 100 milliseconds
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Time to First Byte (TTFB)**: < 600 milliseconds

### Animation Performance
- **Frame Rate**: > 50 FPS (target 60 FPS)
- **Animation Duration**: 150-250ms for micro-interactions

### Asset Sizes
- **CSS Bundle**: < 50KB (minified + gzipped)
- **JavaScript Bundle**: < 50KB per page (minified + gzipped)
- **Images**: < 200KB each (WebP format)
- **Total Page Weight**: < 1.5MB

## CSS Optimization

### 1. Bootstrap Customization

We use a custom Bootstrap configuration that includes only the components we need:

```scss
// static/scss/_bootstrap-custom.scss
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins";
@import "bootstrap/scss/root";
@import "bootstrap/scss/reboot";
@import "bootstrap/scss/type";
@import "bootstrap/scss/containers";
@import "bootstrap/scss/grid";
@import "bootstrap/scss/forms";
@import "bootstrap/scss/buttons";
// ... only needed components
```

**Removed Components** (not used):
- Accordion
- Breadcrumb
- Carousel
- Collapse
- List group
- Offcanvas
- Placeholders
- Popovers
- Progress (custom implementation)
- Scrollspy
- Spinners (custom implementation)
- Toasts (custom implementation)
- Tooltips (custom implementation)

### 2. CSS Compilation

**Development:**
```bash
python compile_scss.py
```

**Production:**
```bash
python compile_scss.py --production
```

This creates:
- `design-system.css` (minified)
- `design-system.css.gz` (gzipped)

**Results:**
- Original: ~200KB
- Minified: ~62KB (69% reduction)
- Gzipped: ~11KB (82% reduction from minified)

### 3. CSS Delivery

The `GzipStaticMiddleware` automatically serves pre-compressed files:

```python
# config/middleware.py
class GzipStaticMiddleware:
    def __call__(self, request):
        # Serves .gz files when available and client accepts gzip
        ...
```

## JavaScript Optimization

### 1. Minification

**Command:**
```bash
python manage.py optimize_js
```

Creates:
- `main.min.js` (minified)
- `main.min.js.gz` (gzipped)

**Results:**
- Original: ~80KB
- Minified: ~40KB (50% reduction)
- Gzipped: ~12KB (70% reduction from minified)

### 2. Deferred Loading

Use template tags for optimized script loading:

```django
{% load script_tags %}

{# Deferred (recommended for most scripts) #}
{% deferred_script 'js/main.js' %}

{# Async (for independent scripts) #}
{% async_script 'js/analytics.js' %}

{# Critical (only for essential scripts) #}
{% critical_script 'js/core.js' %}
```

### 3. Removed Dependencies

We removed heavy libraries and use native JavaScript:

**Before:**
- jQuery (~30KB gzipped)
- Lodash (~25KB gzipped)
- Moment.js (~20KB gzipped)

**After:**
- Native ES6+ features
- Native Date API
- Native DOM manipulation

**Savings:** ~75KB gzipped

## Image Optimization

### 1. Compression

**Command:**
```bash
python manage.py optimize_images --quality 85 --webp
```

**Process:**
1. Compresses JPEG/PNG files
2. Resizes images > 2000px width
3. Creates WebP versions
4. Reports compression ratios

**Results:**
- JPEG: 30-40% reduction
- PNG: 20-30% reduction
- WebP: 25-35% smaller than JPEG

### 2. Lazy Loading

Use template tags for optimized image loading:

```django
{% load image_tags %}

{# Lazy-loaded image with WebP support #}
{% lazy_image 'images/feature.jpg' 'Feature description' %}

{# Responsive image #}
{% responsive_image 'images/screenshot.jpg' 'App screenshot' %}

{# Custom attributes #}
{% optimized_image 'images/logo.png' 'Logo' class='logo' width='200' %}
```

**HTML Output:**
```html
<picture>
    <source srcset="/static/images/feature.webp" type="image/webp">
    <img src="/static/images/feature.jpg" alt="Feature description" loading="lazy">
</picture>
```

### 3. Format Selection

- **JPEG**: Photos, complex images
- **PNG**: Logos, icons, transparency
- **WebP**: Automatically created for all images
- **SVG**: Icons, logos (preferred when possible)

## Performance Monitoring

### 1. Client-Side Monitoring

The `performance-monitor.js` script tracks:

- **Core Web Vitals**: FCP, LCP, FID, CLS, TTFB
- **Page Load Times**: Total, DOM, Resources
- **Animation Performance**: Frame rates
- **Resource Timing**: CSS, JS, images
- **Long Tasks**: Main thread blocking

**Usage:**
```html
<script src="{% static 'js/performance-monitor.js' %}" defer></script>
```

**Console Output:**
```
🚀 Performance monitoring initialized
✓ FCP: 1200.00 ms
✓ LCP: 2000.00 ms
✓ FID: 50.00 ms
✓ CLS: 0.05
✓ TTFB: 400.00 ms
✓ Average FPS: 58.50 FPS
```

### 2. Server-Side Collection

Metrics are automatically sent to `/api/performance/metrics/` and stored in cache.

**View Dashboard:**
```
http://localhost:8000/performance/dashboard/
```

**API Endpoints:**
- `POST /api/performance/metrics/` - Collect metrics
- `GET /api/performance/summary/` - Get summary
- `GET /performance/dashboard/` - View dashboard (dev only)

### 3. Logging

Performance metrics are logged to `logs/performance.log`:

```
INFO Performance metrics received: URL=/dashboard/, FCP=1200, LCP=2000, FID=50, CLS=0.05
WARNING Performance issues detected on /dashboard/: Slow First Contentful Paint
```

## Deployment Checklist

### 1. Optimize Assets

```bash
# Compile and minify CSS
python compile_scss.py --production

# Optimize JavaScript
python manage.py optimize_js

# Optimize images
python manage.py optimize_images --quality 85 --webp

# Collect static files
python manage.py collectstatic --noinput
```

### 2. Configure Web Server

**Nginx Configuration:**

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_types text/css application/javascript image/svg+xml;
gzip_min_length 1024;

# Serve pre-compressed files
location ~* \.(css|js)$ {
    gzip_static on;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Cache static files
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Cache images
location ~* \.(jpg|jpeg|png|gif|webp|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Apache Configuration:**

```apache
# Enable gzip compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/css application/javascript image/svg+xml
</IfModule>

# Serve pre-compressed files
<IfModule mod_rewrite.c>
    RewriteCond %{HTTP:Accept-Encoding} gzip
    RewriteCond %{REQUEST_FILENAME}\.gz -f
    RewriteRule ^(.*)$ $1.gz [L]
</IfModule>

# Cache static files
<FilesMatch "\.(css|js|jpg|jpeg|png|gif|webp|svg)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>
```

### 3. Django Settings

**Production Settings:**

```python
# settings.py

# Use ManifestStaticFilesStorage for cache busting
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Enable middleware
MIDDLEWARE = [
    'config.middleware.GzipStaticMiddleware',  # Serve pre-compressed files
    'config.middleware.StaticFilesCacheMiddleware',  # Add cache headers
    # ...
]

# Disable performance monitoring in production
PERFORMANCE_MONITORING_ENABLED = False
```

## Performance Testing

### 1. Lighthouse Audit

```bash
# Install Lighthouse
npm install -g lighthouse

# Run audit
lighthouse https://your-site.com --view

# Target scores:
# - Performance: > 90
# - Accessibility: > 90
# - Best Practices: > 90
# - SEO: > 90
```

### 2. WebPageTest

Visit [webpagetest.org](https://www.webpagetest.org/) and test your site:

- **First Byte Time**: < 600ms
- **Start Render**: < 1.8s
- **Speed Index**: < 3.0s
- **Fully Loaded**: < 5.0s

### 3. Chrome DevTools

**Performance Tab:**
1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Interact with page
5. Stop recording
6. Analyze:
   - FPS graph (should be 60 FPS)
   - Main thread activity
   - Long tasks (should be minimal)

**Network Tab:**
1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check:
   - Total size (< 1.5MB)
   - Number of requests (< 50)
   - Load time (< 3s)
   - Gzipped files are served

**Lighthouse Tab:**
1. Open DevTools (F12)
2. Go to Lighthouse tab
3. Select categories
4. Click "Generate report"
5. Review scores and recommendations

## Monitoring in Production

### 1. Real User Monitoring (RUM)

Consider integrating:
- Google Analytics 4 (Core Web Vitals)
- New Relic Browser
- Datadog RUM
- Sentry Performance

### 2. Synthetic Monitoring

Set up automated tests:
- Lighthouse CI
- WebPageTest API
- Pingdom
- UptimeRobot

### 3. Alerts

Configure alerts for:
- FCP > 1.8s
- LCP > 2.5s
- FID > 100ms
- CLS > 0.1
- Page load time > 3s
- Error rate > 1%

## Troubleshooting

### Slow Page Load

**Symptoms:**
- Page takes > 3 seconds to load
- High TTFB

**Solutions:**
1. Check database queries (use Django Debug Toolbar)
2. Enable query caching
3. Optimize database indexes
4. Use CDN for static files
5. Enable server-side caching

### Low Frame Rate

**Symptoms:**
- Animations are janky
- FPS < 50

**Solutions:**
1. Reduce animation complexity
2. Use CSS transforms instead of position changes
3. Use `will-change` CSS property
4. Debounce scroll/resize events
5. Use `requestAnimationFrame` for animations

### Large Bundle Size

**Symptoms:**
- CSS/JS files > 100KB
- Long download times

**Solutions:**
1. Remove unused code
2. Split code into smaller chunks
3. Use dynamic imports
4. Enable tree shaking
5. Compress assets

### Images Not Optimized

**Symptoms:**
- Images > 500KB
- Slow image loading

**Solutions:**
1. Run `python manage.py optimize_images --webp`
2. Use appropriate image formats
3. Resize images before upload
4. Enable lazy loading
5. Use responsive images

## Best Practices

### CSS
- Use CSS custom properties for theming
- Minimize specificity
- Avoid `@import` in CSS
- Use shorthand properties
- Remove unused styles

### JavaScript
- Use native features over libraries
- Defer non-critical scripts
- Minimize DOM manipulation
- Use event delegation
- Cache DOM queries

### Images
- Use WebP with fallbacks
- Lazy load below-fold images
- Specify dimensions to prevent layout shift
- Use SVG for icons and logos
- Compress before uploading

### General
- Minimize HTTP requests
- Enable compression
- Use CDN for static files
- Implement caching strategy
- Monitor performance regularly

## Resources

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [PageSpeed Insights](https://pagespeed.web.dev/)

### Documentation
- [Web Vitals](https://web.dev/vitals/)
- [Performance Best Practices](https://web.dev/fast/)
- [Image Optimization](https://web.dev/fast/#optimize-your-images)
- [JavaScript Performance](https://web.dev/fast/#optimize-your-javascript)

### Libraries
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [libsass](https://sass.github.io/libsass-python/) - SCSS compilation
- [jsmin](https://github.com/tikitu/jsmin) - JavaScript minification

## Conclusion

This performance optimization strategy provides:
- **60-80% reduction** in CSS bundle size
- **50-70% reduction** in JavaScript bundle size
- **25-35% reduction** in image sizes
- **Comprehensive monitoring** of Core Web Vitals
- **Automated optimization** commands
- **Production-ready** deployment configuration

Regular monitoring and optimization ensure the application maintains excellent performance as it grows.
