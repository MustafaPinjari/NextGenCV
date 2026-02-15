"""
Customization Service
Handles template customization including colors, fonts, and custom CSS.
"""
import re
from apps.templates_mgmt.models import TemplateCustomization, DEFAULT_COLOR_SCHEMES, ATS_SAFE_FONTS


class CustomizationService:
    """Service for managing template customizations"""
    
    @staticmethod
    def apply_customization(html, customization):
        """
        Apply customization settings to rendered HTML.
        
        Args:
            html (str): Base HTML template
            customization (TemplateCustomization): Customization settings
            
        Returns:
            str: HTML with customizations applied
        """
        # Apply color scheme
        if customization.color_scheme:
            html = CustomizationService.apply_color_scheme(html, customization.color_scheme)
        
        # Apply font family
        if customization.font_family:
            html = CustomizationService.apply_font_family(html, customization.font_family)
        
        # Inject custom CSS
        if customization.custom_css:
            html = CustomizationService.inject_custom_css(html, customization.custom_css)
        
        return html
    
    @staticmethod
    def apply_color_scheme(html, color_scheme_name):
        """
        Apply a color scheme to the HTML by replacing color values in styles.
        
        Args:
            html (str): HTML content
            color_scheme_name (str): Name of the color scheme
            
        Returns:
            str: HTML with color scheme applied
        """
        # Get color scheme
        colors = DEFAULT_COLOR_SCHEMES.get(color_scheme_name, DEFAULT_COLOR_SCHEMES['professional'])
        
        # Find the style tag
        style_pattern = r'(<style>)(.*?)(</style>)'
        match = re.search(style_pattern, html, re.DOTALL)
        
        if match:
            style_content = match.group(2)
            
            # Replace color values based on context
            # Primary color (main headings, borders)
            style_content = re.sub(
                r'color:\s*#2c3e50',
                f"color: {colors['primary']}",
                style_content
            )
            style_content = re.sub(
                r'border-bottom:\s*[^;]*#3498db',
                f"border-bottom: 3px solid {colors['accent']}",
                style_content
            )
            style_content = re.sub(
                r'border-bottom:\s*[^;]*#333',
                f"border-bottom: 2px solid {colors['primary']}",
                style_content
            )
            
            # Accent color (links, highlights)
            style_content = re.sub(
                r'color:\s*#3498db',
                f"color: {colors['accent']}",
                style_content
            )
            
            # Secondary color
            style_content = re.sub(
                r'color:\s*#7f8c8d',
                f"color: {colors['secondary']}",
                style_content
            )
            
            # Text color
            style_content = re.sub(
                r'color:\s*#000',
                f"color: {colors['text']}",
                style_content
            )
            
            # Reconstruct HTML with modified styles
            html = html[:match.start()] + match.group(1) + style_content + match.group(3) + html[match.end():]
        
        return html
    
    @staticmethod
    def apply_font_family(html, font_family):
        """
        Apply a font family to the HTML.
        
        Args:
            html (str): HTML content
            font_family (str): Font family name
            
        Returns:
            str: HTML with font family applied
        """
        # Validate font is ATS-safe
        if font_family not in ATS_SAFE_FONTS:
            font_family = 'Arial'  # Default to Arial if not safe
        
        # Find the style tag
        style_pattern = r'(<style>)(.*?)(</style>)'
        match = re.search(style_pattern, html, re.DOTALL)
        
        if match:
            style_content = match.group(2)
            
            # Replace font-family in body style
            style_content = re.sub(
                r"font-family:\s*[^;]+;",
                f"font-family: '{font_family}', 'Helvetica', sans-serif;",
                style_content,
                count=1  # Only replace first occurrence (body)
            )
            
            # Reconstruct HTML with modified styles
            html = html[:match.start()] + match.group(1) + style_content + match.group(3) + html[match.end():]
        
        return html
    
    @staticmethod
    def inject_custom_css(html, custom_css):
        """
        Inject custom CSS into the HTML.
        
        Args:
            html (str): HTML content
            custom_css (str): Custom CSS to inject
            
        Returns:
            str: HTML with custom CSS injected
        """
        # Sanitize custom CSS (basic sanitization)
        custom_css = CustomizationService._sanitize_css(custom_css)
        
        # Find the closing style tag
        style_close_pattern = r'</style>'
        match = re.search(style_close_pattern, html)
        
        if match:
            # Inject custom CSS before closing style tag
            injection_point = match.start()
            html = html[:injection_point] + '\n\n        /* Custom CSS */\n        ' + custom_css + '\n    ' + html[injection_point:]
        
        return html
    
    @staticmethod
    def _sanitize_css(css):
        """
        Basic CSS sanitization to prevent injection attacks.
        
        Args:
            css (str): CSS to sanitize
            
        Returns:
            str: Sanitized CSS
        """
        # Remove any script tags or javascript
        css = re.sub(r'<script[^>]*>.*?</script>', '', css, flags=re.DOTALL | re.IGNORECASE)
        css = re.sub(r'javascript:', '', css, flags=re.IGNORECASE)
        css = re.sub(r'on\w+\s*=', '', css, flags=re.IGNORECASE)
        
        # Remove any @import statements (could be used for external resource loading)
        css = re.sub(r'@import[^;]+;', '', css, flags=re.IGNORECASE)
        
        return css
    
    @staticmethod
    def get_available_color_schemes():
        """
        Get list of available color schemes.
        
        Returns:
            list: List of color scheme names
        """
        return list(DEFAULT_COLOR_SCHEMES.keys())
    
    @staticmethod
    def get_available_fonts():
        """
        Get list of ATS-safe fonts.
        
        Returns:
            list: List of font names
        """
        return ATS_SAFE_FONTS
    
    @staticmethod
    def create_or_update_customization(resume, template, color_scheme=None, font_family=None, custom_css=None):
        """
        Create or update customization for a resume.
        
        Args:
            resume: Resume object
            template: ResumeTemplate object
            color_scheme (str, optional): Color scheme name
            font_family (str, optional): Font family name
            custom_css (str, optional): Custom CSS
            
        Returns:
            TemplateCustomization: Created or updated customization
        """
        customization, created = TemplateCustomization.objects.get_or_create(
            resume=resume,
            defaults={
                'template': template,
                'color_scheme': color_scheme or '',
                'font_family': font_family or '',
                'custom_css': custom_css or ''
            }
        )
        
        if not created:
            # Update existing customization
            if color_scheme is not None:
                customization.color_scheme = color_scheme
            if font_family is not None:
                customization.font_family = font_family
            if custom_css is not None:
                customization.custom_css = custom_css
            customization.template = template
            customization.save()
        
        return customization
