# Static Files Optimization

This directory contains static files (CSS, JavaScript, images) for the ATS Resume Builder application.

## Structure

```
static/
├── css/
│   ├── style.css          # Main custom styles
│   └── resume_print.css   # Print-specific styles for PDF generation
├── js/
│   └── main.js            # Main JavaScript functionality
└── images/
    └── (application images)
```

## Features

### CSS Optimization
- Custom CSS variables for consistent theming
- Responsive design with mobile-first approach
- Professional styling for resume previews
- Enhanced analysis results display
- Smooth transitions and animations

### JavaScript Enhancements
- Client-side form validation with immediate feedback
- Delete confirmation dialogs
- Dynamic form fields for adding multiple entries
- Auto-dismissing alerts
- Bootstrap tooltips integration
- Character counters for text fields

### Performance Optimization
- Static files are collected and hashed for cache busting
- Gzip compression enabled for text files
- Long-term caching headers (1 year for static files)
- CDN-ready with proper cache control headers

## Development

### Adding New Static Files

1. Add your files to the appropriate subdirectory in `static/`
2. Reference them in templates using Django's `{% static %}` tag:
   ```django
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/your-file.css' %}">
   <script src="{% static 'js/your-file.js' %}"></script>
   ```

### Collecting Static Files

For development:
```bash
python manage.py collectstatic
```

For production with optimization:
```bash
python manage.py collectstatic_optimized --noinput
```

This will:
- Collect all static files to `STATIC_ROOT`
- Generate hashed filenames for cache busting
- Create `.htaccess` for Apache servers
- Create nginx configuration snippet

## Production Deployment

### Apache Configuration

The `collectstatic_optimized` command creates a `.htaccess` file with:
- Gzip compression for text files
- Long-term caching headers
- Security headers

### Nginx Configuration

A `nginx_static.conf` file is generated with:
- Gzip compression settings
- Cache control headers
- Security headers

Add the configuration to your nginx server block and update the paths.

### CDN Integration

For CDN deployment:
1. Set `STATIC_URL` to your CDN URL in settings
2. Upload collected static files to CDN
3. Ensure CDN respects cache headers

## Cache Headers

### Static Files (CSS, JS, Images)
- Cache-Control: public, max-age=31536000, immutable
- Expires: 1 year

### Media Files (User Uploads)
- Cache-Control: public, max-age=604800
- Expires: 1 week

### Dynamic Pages
- Cache-Control: no-cache, no-store, must-revalidate

## Security Headers

All responses include:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

## Browser Support

The application supports:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Performance Metrics

Target metrics:
- Page load time: < 2 seconds
- First Contentful Paint: < 1.5 seconds
- Time to Interactive: < 3 seconds

## Troubleshooting

### Static files not loading
1. Ensure `DEBUG = True` in development
2. Run `python manage.py collectstatic`
3. Check `STATIC_URL` and `STATIC_ROOT` settings
4. Verify middleware order in settings

### Cache not working
1. Check browser developer tools (Network tab)
2. Verify cache headers in response
3. Clear browser cache
4. Check server configuration

### JavaScript not working
1. Check browser console for errors
2. Ensure Bootstrap JS is loaded before custom JS
3. Verify jQuery is not required (we use vanilla JS)
4. Check for JavaScript syntax errors
