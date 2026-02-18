"""
Django management command to optimize images for production.

This command:
1. Compresses images using Pillow
2. Converts images to WebP format with fallbacks
3. Reports file sizes and compression ratios

Requirements:
    pip install Pillow

Usage:
    python manage.py optimize_images
    python manage.py optimize_images --quality 85
    python manage.py optimize_images --webp  # Create WebP versions
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class Command(BaseCommand):
    help = 'Optimize images for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='JPEG quality (1-100, default: 85)',
        )
        parser.add_argument(
            '--webp',
            action='store_true',
            help='Create WebP versions of images',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=2000,
            help='Maximum image width (default: 2000px)',
        )

    def handle(self, *args, **options):
        if not PIL_AVAILABLE:
            self.stdout.write(self.style.ERROR(
                'Error: Pillow is not installed. Install with: pip install Pillow'
            ))
            return

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Image Optimization for Production'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        quality = options['quality']
        create_webp = options['webp']
        max_width = options['max_width']

        base_dir = Path(settings.BASE_DIR)
        static_dir = base_dir / 'static'
        images_dir = static_dir / 'images'

        if not images_dir.exists():
            self.stdout.write(self.style.WARNING(
                f'Images directory not found: {images_dir}'
            ))
            self.stdout.write('Creating images directory...')
            images_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS('✓ Created images directory'))
            self.stdout.write('')
            self.stdout.write('No images to optimize yet.')
            return

        # Find all images
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        images = []
        for ext in image_extensions:
            images.extend(images_dir.rglob(f'*{ext}'))

        if not images:
            self.stdout.write('No images found to optimize.')
            return

        self.stdout.write(f'Found {len(images)} images to optimize')
        self.stdout.write('')

        total_original_size = 0
        total_optimized_size = 0
        total_webp_size = 0

        for img_path in images:
            try:
                # Skip already optimized files
                if '.optimized' in img_path.stem or '.webp' in img_path.suffix:
                    continue

                original_size = img_path.stat().st_size
                total_original_size += original_size

                # Open image
                with Image.open(img_path) as img:
                    # Convert RGBA to RGB for JPEG
                    if img.mode in ('RGBA', 'LA', 'P'):
                        if img_path.suffix.lower() in ['.jpg', '.jpeg']:
                            # Create white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background

                    # Resize if too large
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        self.stdout.write(f'  Resized to {max_width}x{new_height}')

                    # Optimize and save
                    optimize_params = {
                        'optimize': True,
                        'quality': quality,
                    }

                    if img_path.suffix.lower() == '.png':
                        optimize_params = {'optimize': True}

                    img.save(img_path, **optimize_params)

                optimized_size = img_path.stat().st_size
                total_optimized_size += optimized_size
                compression = (1 - optimized_size / original_size) * 100

                self.stdout.write(f'✓ {img_path.name}')
                self.stdout.write(
                    f'  Original: {original_size:,} bytes, '
                    f'Optimized: {optimized_size:,} bytes '
                    f'({compression:.1f}% reduction)'
                )

                # Create WebP version if requested
                if create_webp:
                    webp_path = img_path.with_suffix('.webp')
                    with Image.open(img_path) as img:
                        img.save(webp_path, 'WEBP', quality=quality, method=6)

                    webp_size = webp_path.stat().st_size
                    total_webp_size += webp_size
                    webp_compression = (1 - webp_size / original_size) * 100

                    self.stdout.write(
                        f'  WebP: {webp_size:,} bytes '
                        f'({webp_compression:.1f}% reduction from original)'
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error processing {img_path.name}: {e}'))

            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Optimization Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f'Total original size: {total_original_size:,} bytes ({total_original_size / 1024:.2f} KB)')
        self.stdout.write(f'Total optimized size: {total_optimized_size:,} bytes ({total_optimized_size / 1024:.2f} KB)')

        if total_original_size > 0:
            overall_compression = (1 - total_optimized_size / total_original_size) * 100
            self.stdout.write(f'Overall compression: {overall_compression:.1f}%')

        if create_webp and total_webp_size > 0:
            self.stdout.write('')
            self.stdout.write(f'Total WebP size: {total_webp_size:,} bytes ({total_webp_size / 1024:.2f} KB)')
            webp_compression = (1 - total_webp_size / total_original_size) * 100
            self.stdout.write(f'WebP compression: {webp_compression:.1f}%')

        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Use the {% load image_tags %} template tag for lazy loading')
        self.stdout.write('2. Use {% optimized_image %} tag in templates')
        self.stdout.write('3. Run: python manage.py collectstatic')
