# Formatting standardization service
from typing import Dict, List
import re
from datetime import datetime


class FormattingStandardizerService:
    """
    Service for standardizing resume formatting to ATS-friendly formats.
    Handles section headings, date formats, and problematic formatting.
    """
    
    # Standard section heading mappings
    SECTION_HEADING_MAP = {
        # Experience variations
        'work history': 'Work Experience',
        'employment': 'Work Experience',
        'employment history': 'Work Experience',
        'professional experience': 'Work Experience',
        'work experience': 'Work Experience',
        'experience': 'Work Experience',
        'jobs': 'Work Experience',
        'career history': 'Work Experience',
        
        # Education variations
        'schooling': 'Education',
        'academic background': 'Education',
        'education': 'Education',
        'degrees': 'Education',
        'academic history': 'Education',
        'qualifications': 'Education',
        
        # Skills variations
        'technical skills': 'Skills',
        'core competencies': 'Skills',
        'skills': 'Skills',
        'competencies': 'Skills',
        'expertise': 'Skills',
        'proficiencies': 'Skills',
        'technical proficiencies': 'Skills',
        
        # Projects variations
        'projects': 'Projects',
        'portfolio': 'Projects',
        'key projects': 'Projects',
        'notable projects': 'Projects',
        
        # Certifications variations
        'certifications': 'Certifications',
        'certificates': 'Certifications',
        'professional certifications': 'Certifications',
        'licenses': 'Certifications',
        
        # Summary variations
        'summary': 'Professional Summary',
        'profile': 'Professional Summary',
        'professional summary': 'Professional Summary',
        'career summary': 'Professional Summary',
        'objective': 'Professional Summary',
    }
    
    # Date format patterns
    DATE_PATTERNS = {
        # MM/YYYY -> Month YYYY
        r'\b(\d{1,2})/(\d{4})\b': lambda m: FormattingStandardizerService._format_month_year(m.group(1), m.group(2)),
        # YYYY-MM -> Month YYYY
        r'\b(\d{4})-(\d{1,2})\b': lambda m: FormattingStandardizerService._format_month_year(m.group(2), m.group(1)),
        # MM-YYYY -> Month YYYY
        r'\b(\d{1,2})-(\d{4})\b': lambda m: FormattingStandardizerService._format_month_year(m.group(1), m.group(2)),
    }
    
    # Problematic formatting patterns to remove
    PROBLEMATIC_PATTERNS = [
        # Multiple consecutive spaces
        (r'\s{2,}', ' '),
        # Tabs
        (r'\t', ' '),
        # Multiple consecutive newlines (keep max 2)
        (r'\n{3,}', '\n\n'),
        # Trailing whitespace
        (r'[ \t]+$', ''),
        # Leading whitespace on lines
        (r'^[ \t]+', ''),
    ]
    
    @staticmethod
    def standardize_section_headings(text: str) -> Dict:
        """
        Standardize section headings to ATS-friendly formats.
        
        Args:
            text: Text containing section headings
            
        Returns:
            Dictionary containing:
                - original: Original text
                - standardized: Text with standardized headings
                - changes: List of changes made
        """
        if not text:
            return {
                'original': text,
                'standardized': text,
                'changes': []
            }
        
        standardized = text
        changes = []
        
        # Look for section headings (typically at start of line, may have formatting)
        for non_standard, standard in FormattingStandardizerService.SECTION_HEADING_MAP.items():
            # Case-insensitive pattern matching
            # Match heading at start of line or after newline
            pattern = r'(?:^|\n)([•\-\*\s]*)(' + re.escape(non_standard) + r')(\s*:?\s*)'
            
            def replace_heading(match):
                prefix = match.group(1)
                heading = match.group(2)
                suffix = match.group(3)
                
                # Only replace if it's actually different
                if heading.lower() != standard.lower():
                    changes.append({
                        'type': 'section_heading',
                        'old': heading,
                        'new': standard
                    })
                
                # Return standardized format (no prefix bullets, with colon)
                return f"\n{standard}:"
            
            standardized = re.sub(pattern, replace_heading, standardized, flags=re.IGNORECASE)
        
        return {
            'original': text,
            'standardized': standardized,
            'changes': changes
        }
    
    @staticmethod
    def standardize_date_formats(text: str) -> Dict:
        """
        Standardize date formats to "Month YYYY" format.
        
        Args:
            text: Text containing dates
            
        Returns:
            Dictionary containing:
                - original: Original text
                - standardized: Text with standardized dates
                - changes: List of changes made
        """
        if not text:
            return {
                'original': text,
                'standardized': text,
                'changes': []
            }
        
        standardized = text
        changes = []
        
        # Apply each date pattern
        for pattern, formatter in FormattingStandardizerService.DATE_PATTERNS.items():
            matches = list(re.finditer(pattern, standardized))
            
            for match in reversed(matches):  # Reverse to maintain positions
                old_date = match.group(0)
                new_date = formatter(match)
                
                if old_date != new_date:
                    changes.append({
                        'type': 'date_format',
                        'old': old_date,
                        'new': new_date
                    })
                    
                    # Replace in text
                    start, end = match.span()
                    standardized = standardized[:start] + new_date + standardized[end:]
        
        return {
            'original': text,
            'standardized': standardized,
            'changes': changes
        }
    
    @staticmethod
    def remove_problematic_formatting(text: str) -> Dict:
        """
        Remove ATS-unfriendly formatting patterns.
        
        Args:
            text: Text with potential formatting issues
            
        Returns:
            Dictionary containing:
                - original: Original text
                - cleaned: Text with formatting issues removed
                - changes: List of changes made
        """
        if not text:
            return {
                'original': text,
                'cleaned': text,
                'changes': []
            }
        
        cleaned = text
        changes = []
        
        # Apply each problematic pattern fix
        for pattern, replacement in FormattingStandardizerService.PROBLEMATIC_PATTERNS:
            matches = list(re.finditer(pattern, cleaned, flags=re.MULTILINE))
            
            if matches:
                changes.append({
                    'type': 'formatting_cleanup',
                    'pattern': pattern,
                    'occurrences': len(matches)
                })
                
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
        
        # Remove special characters that ATS might not handle well
        # Keep: letters, numbers, basic punctuation, newlines
        # Remove: fancy quotes, em dashes, special bullets, etc.
        special_char_map = {
            '"': '"',  # Smart quotes to regular
            '"': '"',
            ''': "'",
            ''': "'",
            '—': '-',  # Em dash to hyphen
            '–': '-',  # En dash to hyphen
            '•': '-',  # Bullet to hyphen
            '◦': '-',
            '▪': '-',
            '▫': '-',
        }
        
        for special, replacement in special_char_map.items():
            if special in cleaned:
                count = cleaned.count(special)
                cleaned = cleaned.replace(special, replacement)
                changes.append({
                    'type': 'special_character',
                    'old': special,
                    'new': replacement,
                    'occurrences': count
                })
        
        return {
            'original': text,
            'cleaned': cleaned,
            'changes': changes
        }
    
    @staticmethod
    def standardize_all(text: str) -> Dict:
        """
        Apply all standardization operations to text.
        
        Args:
            text: Text to standardize
            
        Returns:
            Dictionary containing:
                - original: Original text
                - standardized: Fully standardized text
                - all_changes: All changes made across all operations
        """
        if not text:
            return {
                'original': text,
                'standardized': text,
                'all_changes': []
            }
        
        all_changes = []
        current_text = text
        
        # 1. Standardize section headings
        heading_result = FormattingStandardizerService.standardize_section_headings(current_text)
        current_text = heading_result['standardized']
        all_changes.extend(heading_result['changes'])
        
        # 2. Standardize date formats
        date_result = FormattingStandardizerService.standardize_date_formats(current_text)
        current_text = date_result['standardized']
        all_changes.extend(date_result['changes'])
        
        # 3. Remove problematic formatting
        format_result = FormattingStandardizerService.remove_problematic_formatting(current_text)
        current_text = format_result['cleaned']
        all_changes.extend(format_result['changes'])
        
        return {
            'original': text,
            'standardized': current_text,
            'all_changes': all_changes
        }
    
    @staticmethod
    def _format_month_year(month: str, year: str) -> str:
        """
        Format month and year to "Month YYYY" format.
        
        Args:
            month: Month number (1-12)
            year: Year (YYYY)
            
        Returns:
            Formatted date string
        """
        try:
            month_num = int(month)
            if 1 <= month_num <= 12:
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                return f"{month_names[month_num - 1]} {year}"
        except (ValueError, IndexError):
            pass
        
        # If conversion fails, return original
        return f"{month}/{year}"
    
    @staticmethod
    def validate_ats_friendly(text: str) -> Dict:
        """
        Validate if text is ATS-friendly and identify issues.
        
        Args:
            text: Text to validate
            
        Returns:
            Dictionary containing:
                - is_ats_friendly: Boolean indicating if text is ATS-friendly
                - issues: List of identified issues
                - score: ATS-friendliness score (0-100)
        """
        if not text:
            return {
                'is_ats_friendly': True,
                'issues': [],
                'score': 100.0
            }
        
        issues = []
        score = 100.0
        
        # Check for problematic patterns
        if re.search(r'\t', text):
            issues.append('Contains tab characters')
            score -= 10
        
        if re.search(r'\s{3,}', text):
            issues.append('Contains excessive whitespace')
            score -= 5
        
        # Check for special characters
        special_chars = ['•', '◦', '▪', '—', '–', '"', '"', ''', ''']
        for char in special_chars:
            if char in text:
                issues.append(f'Contains special character: {char}')
                score -= 5
        
        # Check for non-standard section headings
        for non_standard in FormattingStandardizerService.SECTION_HEADING_MAP.keys():
            if re.search(r'\b' + re.escape(non_standard) + r'\b', text, re.IGNORECASE):
                standard = FormattingStandardizerService.SECTION_HEADING_MAP[non_standard]
                if non_standard.lower() != standard.lower():
                    issues.append(f'Non-standard section heading: "{non_standard}"')
                    score -= 3
        
        # Check for non-standard date formats
        if re.search(r'\d{1,2}/\d{4}', text) or re.search(r'\d{4}-\d{1,2}', text):
            issues.append('Contains non-standard date formats')
            score -= 5
        
        score = max(score, 0.0)
        is_ats_friendly = score >= 80.0
        
        return {
            'is_ats_friendly': is_ats_friendly,
            'issues': issues,
            'score': round(score, 2)
        }
