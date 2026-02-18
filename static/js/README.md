## JavaScript Optimization Guide

This directory contains optimized JavaScript files for the NextGenCV application.

## Optimization Strategy

### 1. Minification
All JavaScript files are minified for production:
- Removes whitespace and comments
- Shortens variable names
- Reduces file size by 30-50%
- Creates `.min.js` versions

### 2. Gzip Compression
Gzipped versions are created for all files:
- 60-70% smaller than minified files
- Served automatically by web server
- Transparent to browsers

### 3. Deferred Loading
Non-critical scripts use deferred loading:
- Scripts load after HTML parsing
- Improves initial page load time
- Better Core Web Vitals scores

### 4. Code Splitting
Page-specific functionality is separated:
- Core functionality in `main.js`
- Page-specific code in separate files
- Reduces unnecessary code loading

## File Structure

```
static/js/
├── README.md (this file)
├── main.js                    # Core functionality (all pages)
├── main.min.js                # Minified version
├── main.min.js.gz             # Gzipped version
├── accessibility.js           # Accessibility enhancements
├── progress-indicators.js     # Progress components
├── tutorials.js               # Tutorial/help system
└── components/                # Component-specific scripts
    ├── sidebar.js
    ├── wizard.js
    └── file-upload.js
```

## Usage in Templates

### Load the template tags
```django
{% load script_tags %}
```

### Deferred script (recommended for most scripts)
```django
{% deferred_script 'js/main.js' %}
```

### Async script (for independent scripts)
```django
{% async_script 'js/analytics.js' %}
```

### Critical script (only for essential scripts)
```django
{% critical_script 'js/core.js' %}
```

### Inline script (for small, critical code)
```django
{% inline_script 'console.log("Page loaded");' %}
```

### Preload script (for scripts needed soon)
```django
{% preload_script 'js/wizard.js' %}
```

## Optimization Commands

### Minify all JavaScript files
```bash
python manage.py optimize_js
```

### Analyze JavaScript dependencies
```bash
python manage.py optimize_js --analyze
```

## Script Loading Strategy

### Critical Scripts (load immediately)
- Core functionality required before page render
- Very small scripts (<5KB)
- Example: Theme initialization, critical polyfills

```django
{% critical_script 'js/theme-init.js' %}
```

### Deferred Scripts (load after HTML parsing)
- Main application logic
- UI enhancements
- Form validation
- Most scripts should use this

```django
{% deferred_script 'js/main.js' %}
{% deferred_script 'js/accessibility.js' %}
```

### Async Scripts (load independently)
- Analytics
- Third-party widgets
- Non-essential features

```django
{% async_script 'js/analytics.js' %}
```

## Performance Best Practices

### 1. Minimize Dependencies
- Use native JavaScript features instead of libraries
- Import only needed functions from libraries
- Avoid heavy libraries (jQuery, Lodash) when possible

### 2. Code Splitting
- Separate page-specific code
- Load only what's needed for current page
- Use dynamic imports for large features

### 3. Defer Non-Critical Code
- Use `defer` attribute for most scripts
- Use `async` for independent scripts
- Inline only critical, small scripts

### 4. Optimize Event Listeners
- Use event delegation for dynamic content
- Debounce/throttle frequent events (scroll, resize)
- Remove listeners when no longer needed

### 5. Minimize DOM Manipulation
- Batch DOM updates
- Use DocumentFragment for multiple insertions
- Cache DOM queries

### 6. Lazy Load Features
- Load features only when needed
- Use Intersection Observer for scroll-based loading
- Defer initialization of below-fold components

## File Size Guidelines

### Target Sizes (minified + gzipped)
- Critical scripts: <5KB
- Main application: <30KB
- Page-specific: <10KB each
- Total per page: <50KB

### Current Sizes
- main.js: ~25KB (minified + gzipped)
- accessibility.js: ~8KB (minified + gzipped)
- progress-indicators.js: ~5KB (minified + gzipped)

## Browser Compatibility

### Modern Features Used
- ES6+ syntax (const, let, arrow functions)
- Promises and async/await
- Fetch API
- IntersectionObserver
- Native form validation

### Polyfills (if needed)
For older browsers, consider adding polyfills:
- Promise polyfill
- Fetch polyfill
- IntersectionObserver polyfill

## Debugging

### Development Mode
In development (DEBUG=True):
- Uses unminified files
- Includes source maps
- Detailed error messages

### Production Mode
In production (DEBUG=False):
- Uses minified files
- Serves gzipped versions
- Minimal error messages

### Enable Source Maps
For debugging minified code:
```bash
# Generate source maps during minification
python manage.py optimize_js --source-maps
```

## Common Issues

### Scripts not loading
- Check file path is correct
- Run `python manage.py collectstatic`
- Verify file permissions
- Check browser console for errors

### Minified files not used
- Ensure DEBUG=False in production
- Check template uses script_tags
- Verify .min.js files exist

### Performance issues
- Check file sizes with `--analyze`
- Review Network tab in DevTools
- Use Lighthouse for performance audit
- Check for blocking scripts

## Migration from Legacy Code

### Before (legacy)
```html
<script src="{% static 'js/jquery.min.js' %}"></script>
<script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
<script src="{% static 'js/main.js' %}"></script>
```

### After (optimized)
```django
{% load script_tags %}
{% deferred_script 'js/main.js' %}
{% deferred_script 'js/accessibility.js' %}
```

### Removed Dependencies
- jQuery (replaced with vanilla JavaScript)
- Heavy utility libraries (use native ES6)
- Unused Bootstrap components

## Testing

### Performance Testing
```bash
# Run Lighthouse audit
lighthouse https://your-site.com --view

# Check Core Web Vitals
# - First Contentful Paint (FCP): <1.8s
# - Largest Contentful Paint (LCP): <2.5s
# - Total Blocking Time (TBT): <200ms
```

### Functionality Testing
```bash
# Test with minified files
DEBUG=False python manage.py runserver

# Test in different browsers
# - Chrome
# - Firefox
# - Safari
# - Edge
```

## Requirements

This optimization strategy addresses:
- **Requirement 14.4**: Compress static assets
- **Requirement 14.5**: Avoid heavy JavaScript libraries
- **Requirement 14.6**: Monitor animation frame rates

## Related Documentation

- [Performance Optimization](../../Docs/PERFORMANCE.md)
- [CSS Optimization](../css/README.md)
- [Image Optimization](../images/README.md)
- [Deployment Guide](../../Docs/DEPLOYMENT.md)

## Tools and Resources

### Minification
- jsmin (Python): Used by optimize_js command
- Terser: Advanced JavaScript minifier
- UglifyJS: Alternative minifier

### Analysis
- Lighthouse: Performance auditing
- WebPageTest: Detailed performance analysis
- Chrome DevTools: Network and Performance tabs

### Monitoring
- Core Web Vitals: Real user metrics
- Performance API: Custom metrics
- Error tracking: Sentry, Rollbar

## Future Improvements

1. **Module Bundling**: Use webpack or rollup for better optimization
2. **Tree Shaking**: Remove unused code automatically
3. **Code Splitting**: Dynamic imports for large features
4. **Service Workers**: Cache scripts for offline use
5. **HTTP/2 Push**: Push critical scripts proactively
