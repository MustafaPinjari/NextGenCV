"""
Template customization service for resume styling.
Provides color schemes and font options for resume templates.

Requirements: 13.1-13.6, 14.1-14.6
"""
from typing import Dict, List


class TemplateCustomizationService:
    """
    Service for managing template customization options.
    Provides color schemes and font selections for resumes.
    """
    
    # Preset color schemes (Requirements: 13.6)
    COLOR_SCHEMES = {
        'professional_blue': {
            'name': 'Professional Blue',
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#3498DB',    # Bright blue
            'accent': '#1ABC9C',       # Teal
            'text': '#2C3E50',         # Dark blue-gray
            'description': 'Classic and professional, ideal for corporate roles'
        },
        'creative_purple': {
            'name': 'Creative Purple',
            'primary': '#8E44AD',      # Purple
            'secondary': '#9B59B6',    # Light purple
            'accent': '#E74C3C',       # Red accent
            'text': '#2C3E50',         # Dark gray
            'description': 'Bold and creative, perfect for design and creative fields'
        },
        'modern_green': {
            'name': 'Modern Green',
            'primary': '#27AE60',      # Green
            'secondary': '#2ECC71',    # Light green
            'accent': '#F39C12',       # Orange accent
            'text': '#2C3E50',         # Dark gray
            'description': 'Fresh and modern, great for tech and startups'
        },
        'classic_black': {
            'name': 'Classic Black',
            'primary': '#2C3E50',      # Dark gray
            'secondary': '#34495E',    # Medium gray
            'accent': '#7F8C8D',       # Light gray
            'text': '#2C3E50',         # Dark gray
            'description': 'Timeless and elegant, suitable for any industry'
        },
        'warm_orange': {
            'name': 'Warm Orange',
            'primary': '#E67E22',      # Orange
            'secondary': '#F39C12',    # Light orange
            'accent': '#D35400',       # Dark orange
            'text': '#2C3E50',         # Dark gray
            'description': 'Energetic and approachable, ideal for sales and marketing'
        }
    }
    
    # ATS-safe fonts (Requirements: 14.2, 14.6)
    FONT_FAMILIES = {
        'Arial': {
            'name': 'Arial',
            'family': 'Arial, sans-serif',
            'description': 'Clean and widely supported, excellent ATS compatibility',
            'ats_safe': True
        },
        'Calibri': {
            'name': 'Calibri',
            'family': 'Calibri, sans-serif',
            'description': 'Modern and professional, Microsoft Office default',
            'ats_safe': True
        },
        'Georgia': {
            'name': 'Georgia',
            'family': 'Georgia, serif',
            'description': 'Elegant serif font, great for traditional industries',
            'ats_safe': True
        },
        'Times New Roman': {
            'name': 'Times New Roman',
            'family': '"Times New Roman", Times, serif',
            'description': 'Classic serif font, highly compatible with ATS',
            'ats_safe': True
        },
        'Helvetica': {
            'name': 'Helvetica',
            'family': 'Helvetica, Arial, sans-serif',
            'description': 'Clean and professional, excellent readability',
            'ats_safe': True
        },
        'Verdana': {
            'name': 'Verdana',
            'family': 'Verdana, sans-serif',
            'description': 'Highly readable, great for digital viewing',
            'ats_safe': True
        }
    }
    
    @staticmethod
    def get_color_scheme(scheme_name: str) -> Dict:
        """
        Get color scheme details by name.
        
        Args:
            scheme_name: Name of the color scheme
            
        Returns:
            Dict with color values and metadata
        """
        return TemplateCustomizationService.COLOR_SCHEMES.get(
            scheme_name,
            TemplateCustomizationService.COLOR_SCHEMES['professional_blue']
        )
    
    @staticmethod
    def get_all_color_schemes() -> Dict[str, Dict]:
        """
        Get all available color schemes.
        
        Returns:
            Dict of all color schemes with their details
        """
        return TemplateCustomizationService.COLOR_SCHEMES
    
    @staticmethod
    def get_font_family(font_name: str) -> Dict:
        """
        Get font family details by name.
        
        Args:
            font_name: Name of the font
            
        Returns:
            Dict with font family and metadata
        """
        return TemplateCustomizationService.FONT_FAMILIES.get(
            font_name,
            TemplateCustomizationService.FONT_FAMILIES['Arial']
        )
    
    @staticmethod
    def get_all_fonts() -> Dict[str, Dict]:
        """
        Get all available ATS-safe fonts.
        
        Returns:
            Dict of all fonts with their details
        """
        return TemplateCustomizationService.FONT_FAMILIES
    
    @staticmethod
    def apply_customization_to_resume(resume, color_scheme: str = None, font_family: str = None):
        """
        Apply customization settings to a resume.
        
        Args:
            resume: Resume model instance
            color_scheme: Color scheme name (optional)
            font_family: Font family name (optional)
            
        Returns:
            Updated resume instance
        """
        if color_scheme:
            # Validate color scheme exists
            if color_scheme in TemplateCustomizationService.COLOR_SCHEMES:
                resume.color_scheme = color_scheme
        
        if font_family:
            # Validate font exists
            if font_family in TemplateCustomizationService.FONT_FAMILIES:
                resume.font_family = font_family
        
        resume.save()
        return resume
    
    @staticmethod
    def get_css_variables(resume) -> str:
        """
        Generate CSS variables for a resume's customization.
        
        Args:
            resume: Resume model instance
            
        Returns:
            CSS string with custom properties
        """
        color_scheme = TemplateCustomizationService.get_color_scheme(resume.color_scheme)
        font_info = TemplateCustomizationService.get_font_family(resume.font_family)
        
        css = f"""
        :root {{
            --primary-color: {color_scheme['primary']};
            --secondary-color: {color_scheme['secondary']};
            --accent-color: {color_scheme['accent']};
            --text-color: {color_scheme['text']};
            --font-family: {font_info['family']};
        }}
        """
        
        return css
