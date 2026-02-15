"""
Unit tests for PDFParserService
"""
from django.test import TestCase, skipIf
from apps.resumes.services.pdf_parser import PDFParserService
from io import BytesIO
import os

# Check if reportlab is available
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@skipIf(not REPORTLAB_AVAILABLE, "reportlab not installed")
class PDFParserServiceTest(TestCase):
    """Test cases for PDFParserService"""
    
    def _create_test_pdf(self, content: str) -> BytesIO:
        """Helper to create a simple PDF with text content"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Add text to PDF
        y_position = 750
        for line in content.split('\n'):
            c.drawString(100, y_position, line)
            y_position -= 20
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def test_extract_text_from_pdf_basic(self):
        """Test basic text extraction from PDF"""
        content = "John Doe\nSoftware Engineer\nPython Developer"
        pdf_file = self._create_test_pdf(content)
        
        text = PDFParserService.extract_text_from_pdf(pdf_file)
        
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)
        self.assertIn('John Doe', text)
        self.assertIn('Software Engineer', text)
    
    def test_extract_text_from_pdf_empty(self):
        """Test extraction from empty PDF raises error"""
        pdf_file = self._create_test_pdf("")
        
        with self.assertRaises(Exception) as context:
            PDFParserService.extract_text_from_pdf(pdf_file)
        
        self.assertIn('No text could be extracted', str(context.exception))
    
    def test_extract_text_from_pdf_multi_page(self):
        """Test extraction from multi-page PDF"""
        # Create a PDF with multiple pages
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Page 1 Content")
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Page 2 Content")
        c.showPage()
        
        c.save()
        buffer.seek(0)
        
        text = PDFParserService.extract_text_from_pdf(buffer)
        
        self.assertIn('Page 1 Content', text)
        self.assertIn('Page 2 Content', text)
    
    def test_clean_extracted_text_basic(self):
        """Test basic text cleaning"""
        raw_text = "  John   Doe  \n\n\n\n  Software Engineer  "
        
        cleaned = PDFParserService.clean_extracted_text(raw_text)
        
        self.assertEqual(cleaned.count('  '), 0)  # No double spaces
        self.assertLess(cleaned.count('\n\n\n'), raw_text.count('\n\n\n'))
        self.assertEqual(cleaned.strip(), cleaned)  # No leading/trailing whitespace
    
    def test_clean_extracted_text_empty(self):
        """Test cleaning empty text"""
        cleaned = PDFParserService.clean_extracted_text("")
        self.assertEqual(cleaned, "")
    
    def test_clean_extracted_text_removes_page_numbers(self):
        """Test that standalone page numbers are removed"""
        text = "Content here\n5\nMore content\n10\nFinal content"
        
        cleaned = PDFParserService.clean_extracted_text(text)
        
        # Page numbers should be removed
        lines = cleaned.split('\n')
        self.assertNotIn('5', [line.strip() for line in lines if line.strip()])
    
    def test_clean_extracted_text_normalizes_whitespace(self):
        """Test whitespace normalization"""
        text = "Word1\t\t\tWord2     Word3"
        
        cleaned = PDFParserService.clean_extracted_text(text)
        
        self.assertNotIn('\t', cleaned)
        self.assertNotIn('  ', cleaned)  # No double spaces
    
    def test_calculate_parsing_confidence_empty(self):
        """Test confidence calculation with empty text"""
        confidence = PDFParserService.calculate_parsing_confidence("")
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_parsing_confidence_short_text(self):
        """Test confidence with very short text"""
        confidence = PDFParserService.calculate_parsing_confidence("Hi")
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_parsing_confidence_good_resume(self):
        """Test confidence with well-structured resume text"""
        text = """
        John Doe
        john@example.com
        555-123-4567
        
        EXPERIENCE
        Software Engineer at Tech Corp
        2020-2023
        • Developed web applications
        • Improved performance by 50%
        
        EDUCATION
        BS Computer Science
        University Name
        2016-2020
        
        SKILLS
        Python, Django, JavaScript
        """
        
        confidence = PDFParserService.calculate_parsing_confidence(text)
        
        self.assertGreater(confidence, 0.5)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_parsing_confidence_with_parsed_data(self):
        """Test confidence calculation with parsed data"""
        text = "Some resume text with email@example.com and 555-1234"
        parsed_data = {
            'personal_info': {'name': 'John Doe'},
            'experiences': [{'company': 'Tech Corp'}],
            'education': [{'institution': 'University'}],
            'skills': ['Python']
        }
        
        confidence = PDFParserService.calculate_parsing_confidence(text, parsed_data)
        
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_parsing_confidence_bounds(self):
        """Test that confidence is always between 0 and 1"""
        test_texts = [
            "",
            "Short",
            "Medium length text with some content here",
            "Very long text " * 100,
            "Resume with EXPERIENCE and EDUCATION sections\nemail@test.com\n555-1234"
        ]
        
        for text in test_texts:
            confidence = PDFParserService.calculate_parsing_confidence(text)
            self.assertGreaterEqual(confidence, 0.0, f"Confidence {confidence} < 0 for text: {text[:50]}")
            self.assertLessEqual(confidence, 1.0, f"Confidence {confidence} > 1 for text: {text[:50]}")
    
    def test_calculate_parsing_confidence_detects_email(self):
        """Test that email presence increases confidence"""
        text_without_email = "John Doe\nSoftware Engineer\n" * 10
        text_with_email = text_without_email + "\njohn.doe@example.com"
        
        conf_without = PDFParserService.calculate_parsing_confidence(text_without_email)
        conf_with = PDFParserService.calculate_parsing_confidence(text_with_email)
        
        self.assertGreater(conf_with, conf_without)
    
    def test_calculate_parsing_confidence_detects_phone(self):
        """Test that phone number presence increases confidence"""
        text_without_phone = "John Doe\nSoftware Engineer\n" * 10
        text_with_phone = text_without_phone + "\n555-123-4567"
        
        conf_without = PDFParserService.calculate_parsing_confidence(text_without_phone)
        conf_with = PDFParserService.calculate_parsing_confidence(text_with_phone)
        
        self.assertGreater(conf_with, conf_without)
    
    def test_calculate_parsing_confidence_detects_sections(self):
        """Test that section headers increase confidence"""
        text_without_sections = "Some random text here\n" * 10
        text_with_sections = "EXPERIENCE\nSome text\nEDUCATION\nMore text\nSKILLS\nSkill list"
        
        conf_without = PDFParserService.calculate_parsing_confidence(text_without_sections)
        conf_with = PDFParserService.calculate_parsing_confidence(text_with_sections)
        
        self.assertGreater(conf_with, conf_without)
    
    def test_calculate_parsing_confidence_detects_structure(self):
        """Test that bullet points and structure increase confidence"""
        text_without_structure = "Plain text without any structure or formatting"
        text_with_structure = """
        • Bullet point one
        • Bullet point two
        
        Section Header
        
        More content here
        """
        
        conf_without = PDFParserService.calculate_parsing_confidence(text_without_structure)
        conf_with = PDFParserService.calculate_parsing_confidence(text_with_structure)
        
        self.assertGreater(conf_with, conf_without)
    
    def test_handle_multi_column_layout(self):
        """Test multi-column layout detection"""
        # Single column text
        single_column = "This is a normal single column text\nWith multiple lines\nOf reasonable length"
        
        # Multi-column text (simulated with short lines)
        multi_column = "\n".join(["Short" for _ in range(20)])
        
        result_single = PDFParserService.handle_multi_column_layout(single_column)
        result_multi = PDFParserService.handle_multi_column_layout(multi_column)
        
        # Should return text (even if not fully fixed)
        self.assertIsInstance(result_single, str)
        self.assertIsInstance(result_multi, str)
    
    def test_extract_text_preserves_line_breaks(self):
        """Test that line breaks are preserved for structure"""
        content = "Line 1\nLine 2\nLine 3"
        pdf_file = self._create_test_pdf(content)
        
        text = PDFParserService.extract_text_from_pdf(pdf_file)
        
        # Should have multiple lines
        self.assertGreater(text.count('\n'), 0)
    
    def test_clean_extracted_text_preserves_paragraph_breaks(self):
        """Test that paragraph breaks are preserved"""
        text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
        
        cleaned = PDFParserService.clean_extracted_text(text)
        
        # Should still have paragraph breaks
        self.assertIn('\n\n', cleaned)
