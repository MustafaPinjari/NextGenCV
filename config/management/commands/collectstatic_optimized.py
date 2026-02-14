"""
Custom management command to collect static files with optimization
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Collect static files with optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Do not prompt for user input',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting optimized static file collection...'))
        
        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', interactive=not options.get('noinput', False))
        
        # Create .htaccess for Apache (if needed)
        self.create_htaccess()
        
        # Create nginx config snippet (if needed)
        self.create_nginx_config()
        
        self.stdout.write(self.style.SUCCESS('Static files collected and optimized successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Static files location: {settings.STATIC_ROOT}'))

    def create_htaccess(self):
        """Create .htaccess file for Apache with caching rules"""
        htaccess_content = """# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Set cache headers
<IfModule mod_expires.c>
    ExpiresActive On
    
    # Images
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType image/x-icon "access plus 1 year"
    
    # CSS and JavaScript
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType text/javascript "access plus 1 year"
    
    # Fonts
    ExpiresByType font/woff "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresByType application/font-woff "access plus 1 year"
    ExpiresByType application/font-woff2 "access plus 1 year"
</IfModule>

# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "DENY"
    Header set X-XSS-Protection "1; mode=block"
</IfModule>
"""
        
        htaccess_path = os.path.join(settings.STATIC_ROOT, '.htaccess')
        try:
            with open(htaccess_path, 'w') as f:
                f.write(htaccess_content)
            self.stdout.write(self.style.SUCCESS(f'Created .htaccess at {htaccess_path}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create .htaccess: {e}'))

    def create_nginx_config(self):
        """Create nginx config snippet with caching rules"""
        nginx_content = """# Nginx configuration snippet for static files
# Add this to your nginx server block

location /static/ {
    alias /path/to/your/staticfiles/;
    
    # Enable gzip compression
    gzip on;
    gzip_types text/css application/javascript text/javascript application/json;
    gzip_min_length 1000;
    
    # Cache static files for 1 year
    expires 1y;
    add_header Cache-Control "public, immutable";
    
    # Security headers
    add_header X-Content-Type-Options "nosniff";
    add_header X-Frame-Options "DENY";
    add_header X-XSS-Protection "1; mode=block";
}

location /media/ {
    alias /path/to/your/media/;
    
    # Cache media files for 1 week
    expires 7d;
    add_header Cache-Control "public";
}
"""
        
        nginx_path = os.path.join(settings.BASE_DIR, 'nginx_static.conf')
        try:
            with open(nginx_path, 'w') as f:
                f.write(nginx_content)
            self.stdout.write(self.style.SUCCESS(f'Created nginx config snippet at {nginx_path}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create nginx config: {e}'))
