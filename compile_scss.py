#!/usr/bin/env python3
"""
SCSS Compilation Script for NextGenCV Design System

This script compiles SCSS files to CSS using libsass.
It can be run manually or integrated into the Django build process.

Usage:
    python compile_scss.py              # Compile once
    python compile_scss.py --watch      # Watch for changes (development)
    python compile_scss.py --production # Compile with minification and gzip
"""

import os
import sys
import time
import gzip
import argparse
from pathlib import Path

try:
    import sass
except ImportError:
    print("Error: libsass is not installed.")
    print("Please install it with: pip install libsass")
    sys.exit(1)

# Paths
BASE_DIR = Path(__file__).resolve().parent
SCSS_DIR = BASE_DIR / 'static' / 'scss'
CSS_DIR = BASE_DIR / 'static' / 'css'
INPUT_FILE = SCSS_DIR / 'main.scss'
OUTPUT_FILE = CSS_DIR / 'design-system.css'


def compile_scss(minify=False, enable_gzip=False):
    """Compile SCSS to CSS with optional minification and gzip compression."""
    try:
        # Ensure output directory exists
        CSS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Compile SCSS
        output_style = 'compressed' if minify else 'expanded'
        
        print(f"Compiling {INPUT_FILE} -> {OUTPUT_FILE}")
        print(f"Output style: {output_style}")
        
        css_content = sass.compile(
            filename=str(INPUT_FILE),
            output_style=output_style,
            include_paths=[str(SCSS_DIR)]
        )
        
        # Write to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        original_size = len(css_content)
        print(f"✓ Successfully compiled to {OUTPUT_FILE}")
        print(f"  File size: {original_size:,} bytes ({original_size / 1024:.2f} KB)")
        
        # Create gzipped version for production
        if enable_gzip:
            gzip_file = OUTPUT_FILE.with_suffix('.css.gz')
            with gzip.open(gzip_file, 'wb') as f:
                f.write(css_content.encode('utf-8'))
            
            gzip_size = gzip_file.stat().st_size
            compression_ratio = (1 - gzip_size / original_size) * 100
            print(f"✓ Created gzipped version: {gzip_file}")
            print(f"  Gzip size: {gzip_size:,} bytes ({gzip_size / 1024:.2f} KB)")
            print(f"  Compression: {compression_ratio:.1f}% reduction")
        
        return True
        
    except sass.CompileError as e:
        print(f"✗ SCSS Compilation Error:")
        print(f"  {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected Error:")
        print(f"  {e}")
        return False


def watch_scss():
    """Watch SCSS files for changes and recompile."""
    print("Watching SCSS files for changes...")
    print("Press Ctrl+C to stop")
    
    last_modified = {}
    
    try:
        while True:
            changed = False
            
            # Check all SCSS files
            for scss_file in SCSS_DIR.rglob('*.scss'):
                mtime = scss_file.stat().st_mtime
                
                if scss_file not in last_modified:
                    last_modified[scss_file] = mtime
                elif last_modified[scss_file] != mtime:
                    print(f"\nChange detected: {scss_file.relative_to(BASE_DIR)}")
                    last_modified[scss_file] = mtime
                    changed = True
            
            if changed:
                compile_scss(minify=False)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopped watching.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Compile SCSS files for NextGenCV Design System'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch for changes and recompile automatically'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='Compile with minification and gzip compression for production'
    )
    
    args = parser.parse_args()
    
    # Check if SCSS directory exists
    if not SCSS_DIR.exists():
        print(f"Error: SCSS directory not found: {SCSS_DIR}")
        sys.exit(1)
    
    # Check if main.scss exists
    if not INPUT_FILE.exists():
        print(f"Error: Main SCSS file not found: {INPUT_FILE}")
        sys.exit(1)
    
    print("=" * 60)
    print("NextGenCV Design System - SCSS Compiler")
    print("=" * 60)
    print()
    
    if args.watch:
        # Initial compilation
        compile_scss(minify=False, enable_gzip=False)
        print()
        # Watch for changes
        watch_scss()
    else:
        # Single compilation
        success = compile_scss(minify=args.production, enable_gzip=args.production)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
