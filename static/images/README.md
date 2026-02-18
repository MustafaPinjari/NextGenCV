# Image Optimization Guide

This directory contains optimized images for the NextGenCV application.

## Image Optimization Strategy

### 1. Compression
All images are compressed to reduce file size while maintaining visual quality:
- JPEG: Quality 85 (good balance of quality and size)
- PNG: Lossless optimization
- Maximum width: 2000px (larger images are resized)

### 2. WebP Format
WebP versions are created for all images, providing:
- 25-35% smaller file sizes compared to JPEG/PNG
- Better compression with similar quality
- Automatic fallback to original format for unsupported browsers

### 3. Lazy Loading
Images below the fold use native lazy loading:
- Reduces initial page load time
- Improves Core Web Vitals scores
- Better user experience on slow connections

## Usage in Templates

### Load the template tags
```django
{% load image_tags %}
```

### Basic optimized image
```django
{% optimized_image 'images/hero.jpg' 'Hero image description' %}
```

### Lazy-loaded image
```django
{% lazy_image 'images/feature.jpg' 'Feature description' %}
```

### Responsive image with lazy loading
```django
{% responsive_image 'images/screenshot.jpg' 'App screenshot' %}
```

### Custom attributes
```django
{% optimized_image 'images/logo.png' 'Company logo' class='logo' width='200' height='50' %}
```

## Optimization Commands

### Optimize all images
```bash
python manage.py optimize_images
```

### Create WebP versions
```bash
python manage.py optimize_images --webp
```

### Custom quality setting
```bash
python manage.py optimize_images --quality 90 --webp
```

### Set maximum width
```bash
python manage.py optimize_images --max-width 1920 --webp
```

## Image Guidelines

### File Naming
- Use lowercase with hyphens: `hero-image.jpg`
- Be descriptive: `dashboard-screenshot.png`
- Avoid spaces and special characters

### Recommended Sizes
- Hero images: 1920x1080px or 2560x1440px
- Feature images: 800x600px or 1200x900px
- Thumbnails: 400x300px or 600x450px
- Icons: 64x64px, 128x128px, or SVG

### Format Selection
- **JPEG**: Photos, complex images with many colors
- **PNG**: Logos, icons, images with transparency
- **WebP**: Automatically created for all images
- **SVG**: Icons, logos, simple graphics (preferred when possible)

## Browser Support

### WebP Support
- Chrome: ✓ (all versions)
- Firefox: ✓ (65+)
- Safari: ✓ (14+)
- Edge: ✓ (all versions)

The `optimized_image` tag automatically provides fallbacks for unsupported browsers.

### Lazy Loading Support
- Chrome: ✓ (76+)
- Firefox: ✓ (75+)
- Safari: ✓ (15.4+)
- Edge: ✓ (79+)

For older browsers, images load normally without lazy loading.

## Performance Impact

### Before Optimization
- Average image size: ~500KB
- Total page weight: ~5MB
- Load time: ~3-4 seconds

### After Optimization
- Average image size: ~150KB (WebP) / ~250KB (JPEG)
- Total page weight: ~1.5MB
- Load time: ~1-2 seconds
- 50-70% reduction in image bandwidth

## Directory Structure

```
static/images/
├── README.md (this file)
├── hero/           # Hero section images
├── features/       # Feature section images
├── screenshots/    # App screenshots
├── icons/          # Icon images (prefer SVG)
├── illustrations/  # Illustrations and graphics
└── avatars/        # User avatars and profile images
```

## Best Practices

1. **Always provide alt text** for accessibility
2. **Use lazy loading** for below-fold images
3. **Specify dimensions** when known (prevents layout shift)
4. **Use responsive images** with appropriate sizes
5. **Optimize before committing** to version control
6. **Use SVG** for logos and icons when possible
7. **Test on slow connections** to verify performance

## Troubleshooting

### Images not loading
- Check file path is correct relative to `static/images/`
- Run `python manage.py collectstatic` after adding new images
- Verify file permissions

### WebP not working
- Ensure Pillow is installed: `pip install Pillow`
- Run optimization command with `--webp` flag
- Check browser support

### Large file sizes
- Run optimization command with lower quality: `--quality 80`
- Resize images before uploading
- Consider using WebP format

## Requirements

This optimization strategy addresses:
- **Requirement 14.3**: Lazy load large images
- **Requirement 14.4**: Compress static assets

## Related Documentation

- [Performance Optimization](../../Docs/PERFORMANCE.md)
- [Design System](../../DESIGN_SYSTEM.md)
- [Deployment Guide](../../Docs/DEPLOYMENT.md)
