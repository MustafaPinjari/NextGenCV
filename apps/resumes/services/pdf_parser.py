"""
PDF Parser Service for extracting and cleaning text from PDF files.

This service handles:
- Text extraction from PDF files using pdfplumber
- Text cleaning and sanitization
- Parsing confidence calculation
- Multi-column layout handling
"""

import re
import logging
import pdfplumber
import bleach
from typing import Dict, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFParserService:
    """Service for parsing PDF files and extracting structured text."""
    
    # Common section headers to help identify structure
    SECTION_HEADERS = [
        'experience', 'education', 'skills', 'summary', 'objective',
        'projects', 'certifications', 'awards', 'publications'
    ]
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """
        Extract text from PDF file using pdfplumber.
        
        Args:
            pdf_file: File object or file path
            
        Returns:
            str: Extracted text from all pages
            
        Raises:
            Exception: If PDF cannot be read or parsed
        """
        try:
            text = ""
            
            # Handle both file objects and file paths
            if hasattr(pdf_file, 'read'):
                # It's a file object, read it into BytesIO
                pdf_bytes = BytesIO(pdf_file.read())
                pdf_file.seek(0)  # Reset file pointer for potential reuse
                pdf_source = pdf_bytes
            else:
                # It's a file path
                pdf_source = pdf_file
            
            with pdfplumber.open(pdf_source) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text from page
                        page_text = page.extract_text()
                        
                        if page_text:
                            text += page_text + "\n\n"
                        else:
                            logger.warning(f"No text extracted from page {page_num}")
                            
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num}: {e}")
                        continue
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF. It may be a scanned image or empty.")
            
            return text
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """
        Clean and normalize extracted text with sanitization.
        
        This method:
        - Removes XSS vectors using bleach
        - Removes control characters
        - Normalizes whitespace
        - Fixes common PDF extraction artifacts
        - Preserves line breaks for structure
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove potential XSS vectors (strip all HTML tags)
        text = bleach.clean(text, tags=[], strip=True)
        
        # Remove control characters except newlines and tabs
        text = ''.join(
            char for char in text 
            if char.isprintable() or char in ['\n', '\t']
        )
        
        # Fix common PDF extraction artifacts
        # Remove excessive whitespace but preserve paragraph breaks
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\t+', ' ', text)  # Tabs to single space
        text = re.sub(r'\n{4,}', '\n\n\n', text)  # Max 3 consecutive newlines
        
        # Remove page numbers (common pattern: standalone numbers)
        text = re.sub(r'\n\d+\n', '\n', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove excessive blank lines at start and end
        text = text.strip()
        
        return text
    
    @staticmethod
    def calculate_parsing_confidence(text: str, parsed_data: Optional[Dict] = None) -> float:
        """
        Calculate confidence score for parsing accuracy.
        
        Confidence is based on:
        - Text length (longer is better, up to a point)
        - Presence of section headers
        - Presence of common resume patterns (emails, phones, dates)
        - Structure indicators (bullet points, line breaks)
        - Parsed data completeness (if provided)
        
        Args:
            text: Cleaned extracted text
            parsed_data: Optional dict with parsed sections
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if not text or len(text.strip()) < 50:
            return 0.0
        
        confidence = 0.0
        max_score = 100.0
        
        # 1. Text length score (20 points)
        # Optimal length: 500-5000 characters
        text_length = len(text)
        if 500 <= text_length <= 5000:
            confidence += 20
        elif 200 <= text_length < 500:
            confidence += 15
        elif text_length > 5000:
            confidence += 15
        else:
            confidence += 5
        
        # 2. Section headers score (25 points)
        text_lower = text.lower()
        found_sections = sum(
            1 for header in PDFParserService.SECTION_HEADERS 
            if header in text_lower
        )
        confidence += min(25, found_sections * 5)
        
        # 3. Contact information patterns (20 points)
        patterns_found = 0
        
        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            patterns_found += 1
        
        # Phone pattern
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            patterns_found += 1
        
        # Date patterns (for experience dates)
        if re.search(r'\b(19|20)\d{2}\b', text):
            patterns_found += 1
        
        # LinkedIn or website
        if re.search(r'linkedin\.com|github\.com|https?://', text_lower):
            patterns_found += 1
        
        confidence += patterns_found * 5
        
        # 4. Structure indicators (20 points)
        structure_score = 0
        
        # Bullet points
        if re.search(r'[•●○▪▫■□]', text) or re.search(r'^\s*[-*]\s', text, re.MULTILINE):
            structure_score += 7
        
        # Multiple paragraphs/sections
        if text.count('\n\n') >= 3:
            structure_score += 7
        
        # Capitalized words (likely headers or names)
        capitalized_words = len(re.findall(r'\b[A-Z][a-z]+\b', text))
        if capitalized_words >= 10:
            structure_score += 6
        
        confidence += structure_score
        
        # 5. Parsed data completeness (15 points)
        if parsed_data:
            completeness = 0
            if parsed_data.get('personal_info'):
                completeness += 5
            if parsed_data.get('experiences'):
                completeness += 5
            if parsed_data.get('education'):
                completeness += 3
            if parsed_data.get('skills'):
                completeness += 2
            confidence += completeness
        
        # Normalize to 0.0-1.0 range
        return min(1.0, confidence / max_score)
    
    @staticmethod
    def handle_multi_column_layout(text: str) -> str:
        """
        Attempt to detect and fix multi-column layout issues.
        
        Multi-column PDFs often extract with interleaved text.
        This method attempts to identify and reorder such text.
        
        Args:
            text: Extracted text that may have column issues
            
        Returns:
            str: Text with column issues potentially fixed
        """
        # Split into lines
        lines = text.split('\n')
        
        # Detect if we have a multi-column issue
        # Heuristic: Very short lines (< 40 chars) that alternate with other short lines
        short_lines = [i for i, line in enumerate(lines) if 0 < len(line.strip()) < 40]
        
        # If more than 30% of lines are very short, might be multi-column
        if len(short_lines) > len(lines) * 0.3:
            logger.info("Potential multi-column layout detected")
            # For now, just log it. Full column detection is complex
            # and would require more sophisticated analysis
            # This is a placeholder for future enhancement
        
        return text
