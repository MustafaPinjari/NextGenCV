"""
Django management command to compile SCSS files.

Usage:
    python manage.py compile_scss              # Compile once
    python manage.py compile_scss --watch      # Watch for changes
    python manage.py compile_scss --production # Compile with minification
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import sys
import time

try:
    import sass
except ImportError:
    sass = None


class Command(BaseCommand):
    help = 'Compile SCSS files to CSS for the NextGenCV design system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Watch for changes and recompile automatically',
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Compile with minification for production',
        )

    def handle(self, *args, **options):
        if sass is None:
            self.stdout.write(
                self.style.ERROR('Error: libsass is not installed.')
            )
            self.stdout.write('Please install it with: pip install libsass')
            sys.exit(1)

        # Paths
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        scss_dir = base_dir / 'static' / 'scss'
        css_dir = base_dir / 'static' / 'css'
        input_file = scss_dir / 'main.scss'
        output_file = css_dir / 'design-system.css'

        # Check if files exist
        if not scss_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Error: SCSS directory not found: {scss_dir}')
            )
            sys.exit(1)

        if not input_file.exists():
            self.stdout.write(
                self.style.ERROR(f'Error: Main SCSS file not found: {input_file}')
            )
            sys.exit(1)

        self.stdout.write('=' * 60)
        self.stdout.write('NextGenCV Design System - SCSS Compiler')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        if options['watch']:
            # Initial compilation
            self.compile_scss(input_file, output_file, scss_dir, options['production'])
            self.stdout.write('')
            # Watch for changes
            self.watch_scss(input_file, output_file, scss_dir)
        else:
            # Single compilation
            success = self.compile_scss(
                input_file, output_file, scss_dir, options['production']
            )
            if not success:
                sys.exit(1)

    def compile_scss(self, input_file, output_file, scss_dir, minify=False):
        """Compile SCSS to CSS."""
        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Compile SCSS
            output_style = 'compressed' if minify else 'expanded'

            self.stdout.write(f'Compiling {input_file} -> {output_file}')
            self.stdout.write(f'Output style: {output_style}')

            css_content = sass.compile(
                filename=str(input_file),
                output_style=output_style,
                include_paths=[str(scss_dir)]
            )

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(css_content)

            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully compiled to {output_file}')
            )
            self.stdout.write(f'  File size: {len(css_content)} bytes')
            return True

        except sass.CompileError as e:
            self.stdout.write(self.style.ERROR('✗ SCSS Compilation Error:'))
            self.stdout.write(f'  {e}')
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR('✗ Unexpected Error:'))
            self.stdout.write(f'  {e}')
            return False

    def watch_scss(self, input_file, output_file, scss_dir):
        """Watch SCSS files for changes and recompile."""
        self.stdout.write('Watching SCSS files for changes...')
        self.stdout.write('Press Ctrl+C to stop')

        last_modified = {}

        try:
            while True:
                changed = False

                # Check all SCSS files
                for scss_file in scss_dir.rglob('*.scss'):
                    mtime = scss_file.stat().st_mtime

                    if scss_file not in last_modified:
                        last_modified[scss_file] = mtime
                    elif last_modified[scss_file] != mtime:
                        self.stdout.write(
                            f'\nChange detected: {scss_file.relative_to(scss_dir.parent)}'
                        )
                        last_modified[scss_file] = mtime
                        changed = True

                if changed:
                    self.compile_scss(input_file, output_file, scss_dir, minify=False)

                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write('\n\nStopped watching.')
