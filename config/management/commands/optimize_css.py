"""
Django management command to optimize CSS for production.

This command:
1. Compiles SCSS with minification
2. Creates gzipped versions of CSS files
3. Removes unused CSS (optional)
4. Reports file sizes and compression ratios

Usage:
    python manage.py optimize_css
    python manage.py optimize_css --analyze  # Show detailed analysis
"""

import gzip
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    import sass
except ImportError:
    sass = None


class Command(BaseCommand):
    help = 'Optimize CSS files for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Show detailed analysis of CSS files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('CSS Optimization for Production'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        if not sass:
            self.stdout.write(self.style.ERROR(
                'Error: libsass is not installed. Install with: pip install libsass'
            ))
            return

        base_dir = Path(settings.BASE_DIR)
        scss_dir = base_dir / 'static' / 'scss'
        css_dir = base_dir / 'static' / 'css'
        
        # Compile main SCSS file
        input_file = scss_dir / 'main.scss'
        output_file = css_dir / 'design-system.css'
        
        if not input_file.exists():
            self.stdout.write(self.style.ERROR(f'SCSS file not found: {input_file}'))
            return
        
        self.stdout.write('Compiling SCSS with minification...')
        
        try:
            # Compile with compression
            css_content = sass.compile(
                filename=str(input_file),
                output_style='compressed',
                include_paths=[str(scss_dir)]
            )
            
            # Ensure output directory exists
            css_dir.mkdir(parents=True, exist_ok=True)
            
            # Write minified CSS
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            original_size = len(css_content)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Compiled: {output_file.name}'
            ))
            self.stdout.write(f'  Size: {original_size:,} bytes ({original_size / 1024:.2f} KB)')
            
            # Create gzipped version
            gzip_file = output_file.with_suffix('.css.gz')
            with gzip.open(gzip_file, 'wb') as f:
                f.write(css_content.encode('utf-8'))
            
            gzip_size = gzip_file.stat().st_size
            compression_ratio = (1 - gzip_size / original_size) * 100
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Gzipped: {gzip_file.name}'
            ))
            self.stdout.write(f'  Size: {gzip_size:,} bytes ({gzip_size / 1024:.2f} KB)')
            self.stdout.write(f'  Compression: {compression_ratio:.1f}% reduction')
            
        except sass.CompileError as e:
            self.stdout.write(self.style.ERROR(f'SCSS Compilation Error: {e}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected Error: {e}'))
            return
        
        self.stdout.write('')
        
        # Optimize other CSS files in static directory
        self.stdout.write('Optimizing other CSS files...')
        css_files = list(css_dir.glob('*.css'))
        
        for css_file in css_files:
            if css_file.suffix == '.css' and not css_file.name.endswith('.min.css'):
                # Skip if already processed
                if css_file == output_file:
                    continue
                
                # Create gzipped version
                gzip_file = css_file.with_suffix('.css.gz')
                
                with open(css_file, 'rb') as f_in:
                    with gzip.open(gzip_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                original_size = css_file.stat().st_size
                gzip_size = gzip_file.stat().st_size
                compression_ratio = (1 - gzip_size / original_size) * 100
                
                self.stdout.write(f'✓ {css_file.name}')
                self.stdout.write(f'  Original: {original_size:,} bytes')
                self.stdout.write(f'  Gzipped: {gzip_size:,} bytes ({compression_ratio:.1f}% reduction)')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('CSS Optimization Complete'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Run: python manage.py collectstatic')
        self.stdout.write('2. Configure your web server to serve .gz files when available')
        self.stdout.write('3. Enable gzip compression in your web server configuration')
        self.stdout.write('')
        
        if options['analyze']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Detailed Analysis:'))
            self.stdout.write('')
            self._analyze_css_usage(css_dir)
    
    def _analyze_css_usage(self, css_dir):
        """Analyze CSS file sizes and provide recommendations."""
        self.stdout.write('CSS Files in static directory:')
        self.stdout.write('')
        
        total_size = 0
        total_gzip_size = 0
        
        for css_file in sorted(css_dir.glob('*.css')):
            size = css_file.stat().st_size
            total_size += size
            
            gzip_file = css_file.with_suffix('.css.gz')
            if gzip_file.exists():
                gzip_size = gzip_file.stat().st_size
                total_gzip_size += gzip_size
                self.stdout.write(
                    f'  {css_file.name:40} {size:>10,} bytes  '
                    f'(gzip: {gzip_size:>10,} bytes)'
                )
            else:
                self.stdout.write(f'  {css_file.name:40} {size:>10,} bytes')
        
        self.stdout.write('')
        self.stdout.write(f'Total CSS size: {total_size:,} bytes ({total_size / 1024:.2f} KB)')
        if total_gzip_size > 0:
            self.stdout.write(
                f'Total gzipped: {total_gzip_size:,} bytes ({total_gzip_size / 1024:.2f} KB)'
            )
            compression_ratio = (1 - total_gzip_size / total_size) * 100
            self.stdout.write(f'Overall compression: {compression_ratio:.1f}%')
