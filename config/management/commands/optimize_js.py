"""
Django management command to optimize JavaScript for production.

This command:
1. Minifies JavaScript files
2. Creates gzipped versions
3. Analyzes dependencies and suggests removals
4. Reports file sizes and compression ratios

Requirements:
    pip install jsmin

Usage:
    python manage.py optimize_js
    python manage.py optimize_js --analyze  # Show detailed analysis
"""

import gzip
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from jsmin import jsmin
    JSMIN_AVAILABLE = True
except ImportError:
    JSMIN_AVAILABLE = False


class Command(BaseCommand):
    help = 'Optimize JavaScript files for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Show detailed analysis of JavaScript files',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('JavaScript Optimization for Production'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        if not JSMIN_AVAILABLE:
            self.stdout.write(self.style.WARNING(
                'Warning: jsmin is not installed. Install with: pip install jsmin'
            ))
            self.stdout.write('Skipping minification, will only create gzipped versions.')
            self.stdout.write('')

        base_dir = Path(settings.BASE_DIR)
        js_dir = base_dir / 'static' / 'js'

        if not js_dir.exists():
            self.stdout.write(self.style.ERROR(f'JavaScript directory not found: {js_dir}'))
            return

        # Find all JavaScript files
        js_files = list(js_dir.glob('*.js'))
        
        if not js_files:
            self.stdout.write('No JavaScript files found to optimize.')
            return

        self.stdout.write(f'Found {len(js_files)} JavaScript files to optimize')
        self.stdout.write('')

        total_original_size = 0
        total_minified_size = 0
        total_gzip_size = 0

        for js_file in js_files:
            # Skip already minified files
            if '.min.js' in js_file.name:
                continue

            try:
                original_size = js_file.stat().st_size
                total_original_size += original_size

                # Read original file
                with open(js_file, 'r', encoding='utf-8') as f:
                    js_content = f.read()

                # Minify if jsmin is available
                if JSMIN_AVAILABLE:
                    minified_content = jsmin(js_content)
                    
                    # Save minified version
                    minified_file = js_file.with_suffix('.min.js')
                    with open(minified_file, 'w', encoding='utf-8') as f:
                        f.write(minified_content)
                    
                    minified_size = len(minified_content)
                    total_minified_size += minified_size
                    compression = (1 - minified_size / original_size) * 100
                    
                    self.stdout.write(f'✓ {js_file.name}')
                    self.stdout.write(
                        f'  Original: {original_size:,} bytes, '
                        f'Minified: {minified_size:,} bytes '
                        f'({compression:.1f}% reduction)'
                    )
                    
                    # Create gzipped version of minified file
                    gzip_file = minified_file.with_suffix('.min.js.gz')
                    with gzip.open(gzip_file, 'wb') as f:
                        f.write(minified_content.encode('utf-8'))
                    
                    gzip_size = gzip_file.stat().st_size
                    total_gzip_size += gzip_size
                    gzip_compression = (1 - gzip_size / original_size) * 100
                    
                    self.stdout.write(
                        f'  Gzipped: {gzip_size:,} bytes '
                        f'({gzip_compression:.1f}% reduction from original)'
                    )
                else:
                    # Just create gzipped version of original
                    gzip_file = js_file.with_suffix('.js.gz')
                    with gzip.open(gzip_file, 'wb') as f:
                        f.write(js_content.encode('utf-8'))
                    
                    gzip_size = gzip_file.stat().st_size
                    total_gzip_size += gzip_size
                    compression = (1 - gzip_size / original_size) * 100
                    
                    self.stdout.write(f'✓ {js_file.name}')
                    self.stdout.write(
                        f'  Original: {original_size:,} bytes, '
                        f'Gzipped: {gzip_size:,} bytes '
                        f'({compression:.1f}% reduction)'
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error processing {js_file.name}: {e}'))

            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Optimization Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f'Total original size: {total_original_size:,} bytes ({total_original_size / 1024:.2f} KB)')
        
        if JSMIN_AVAILABLE and total_minified_size > 0:
            self.stdout.write(f'Total minified size: {total_minified_size:,} bytes ({total_minified_size / 1024:.2f} KB)')
            overall_compression = (1 - total_minified_size / total_original_size) * 100
            self.stdout.write(f'Minification: {overall_compression:.1f}%')

        if total_gzip_size > 0:
            self.stdout.write(f'Total gzipped size: {total_gzip_size:,} bytes ({total_gzip_size / 1024:.2f} KB)')
            gzip_compression = (1 - total_gzip_size / total_original_size) * 100
            self.stdout.write(f'Gzip compression: {gzip_compression:.1f}%')

        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Update templates to use .min.js files in production')
        self.stdout.write('2. Configure web server to serve .gz files when available')
        self.stdout.write('3. Run: python manage.py collectstatic')
        self.stdout.write('')

        if options['analyze']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Detailed Analysis:'))
            self.stdout.write('')
            self._analyze_js_dependencies(js_dir)

    def _analyze_js_dependencies(self, js_dir):
        """Analyze JavaScript dependencies and provide recommendations."""
        self.stdout.write('JavaScript Files Analysis:')
        self.stdout.write('')

        # Check for heavy libraries
        heavy_libraries = {
            'jquery': 'Consider using vanilla JavaScript or a lighter alternative',
            'lodash': 'Consider using native ES6 methods or import only needed functions',
            'moment': 'Consider using native Date API or date-fns (lighter)',
            'bootstrap.bundle': 'Already included, ensure not duplicated',
        }

        for js_file in js_dir.glob('*.js'):
            if '.min.js' in js_file.name:
                continue

            size = js_file.stat().st_size
            self.stdout.write(f'  {js_file.name:40} {size:>10,} bytes')

            # Check for heavy library usage
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for lib, recommendation in heavy_libraries.items():
                    if lib in content.lower():
                        self.stdout.write(self.style.WARNING(
                            f'    ⚠ Uses {lib}: {recommendation}'
                        ))
            except:
                pass

        self.stdout.write('')
        self.stdout.write('Recommendations:')
        self.stdout.write('1. Defer non-critical scripts with defer or async attributes')
        self.stdout.write('2. Use native JavaScript features instead of libraries when possible')
        self.stdout.write('3. Split large files into smaller modules')
        self.stdout.write('4. Consider code splitting for page-specific functionality')
        self.stdout.write('5. Remove unused functions and dead code')
