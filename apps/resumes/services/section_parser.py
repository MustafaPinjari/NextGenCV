"""
Section Parser Service for identifying and extracting resume sections.

This service handles:
- Section identification using regex patterns
- Personal information extraction with NER
- Work experience parsing with date/company extraction
- Education parsing with institution extraction
- Skills extraction and categorization
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import spaCy, but make it optional for testing
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found. NER features will be limited.")
        nlp = None
except ImportError:
    logger.warning("spaCy not installed. NER features will be limited.")
    SPACY_AVAILABLE = False
    nlp = None


class SectionParserService:
    """Service for parsing resume sections and extracting structured data."""
    
    # Section header patterns (case-insensitive)
    SECTION_PATTERNS = {
        'experience': r'(?:work\s+)?(?:professional\s+)?(?:experience|employment|work\s+history)',
        'education': r'(?:education|academic\s+background|qualifications)',
        'skills': r'(?:skills|technical\s+skills|core\s+competencies|expertise)',
        'summary': r'(?:summary|profile|objective|about\s+me)',
        'projects': r'(?:projects|portfolio)',
        'certifications': r'(?:certifications|certificates|licenses)',
        'awards': r'(?:awards|honors|achievements)',
    }
    
    @staticmethod
    def identify_sections(text: str) -> Dict[str, str]:
        """
        Identify resume sections using regex patterns.
        
        Args:
            text: Cleaned resume text
            
        Returns:
            Dict mapping section names to their content
        """
        sections = {}
        lines = text.split('\n')
        
        # Find section boundaries
        section_indices = []
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            for section_name, pattern in SectionParserService.SECTION_PATTERNS.items():
                if re.match(f'^{pattern}\\s*:?\\s*$', line_lower):
                    section_indices.append((i, section_name))
                    break
        
        # Extract content between sections
        for idx, (line_num, section_name) in enumerate(section_indices):
            # Find the end of this section (start of next section or end of document)
            if idx + 1 < len(section_indices):
                end_line = section_indices[idx + 1][0]
            else:
                end_line = len(lines)
            
            # Extract section content (skip the header line itself)
            section_content = '\n'.join(lines[line_num + 1:end_line]).strip()
            sections[section_name] = section_content
        
        # If no sections found, try to extract personal info from the top
        if not sections and text:
            # Assume first 10 lines might be personal info
            first_lines = '\n'.join(lines[:10])
            sections['personal_info'] = first_lines
        
        return sections
    
    @staticmethod
    def parse_personal_info(text: str) -> Dict:
        """
        Extract personal information using entity extraction.
        
        Extracts:
        - Name (using NER or first line heuristic)
        - Email
        - Phone
        - Location
        - LinkedIn/Website
        
        Args:
            text: Text containing personal information (usually top of resume)
            
        Returns:
            Dict with personal information fields
        """
        info = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None,
            'linkedin': None,
            'website': None,
        }
        
        # Extract email
        email_match = re.search(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            text
        )
        if email_match:
            info['email'] = email_match.group(0)
        
        # Extract phone - improved patterns for international formats
        phone_patterns = [
            r'\+\d{1,3}\s*\d{10}',  # +91 8799849225
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-123-456-7890
            r'\b\d{10}\b',  # 8799849225
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',     # (123) 456-7890
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                info['phone'] = phone_match.group(0).strip()
                break
        
        # Extract LinkedIn
        linkedin_match = re.search(
            r'linkedin\.com/in/[\w-]+',
            text,
            re.IGNORECASE
        )
        if linkedin_match:
            info['linkedin'] = 'https://' + linkedin_match.group(0)
        
        # Extract website - improved to handle various formats
        website_patterns = [
            r'(?:www\.)?[\w-]+\.(?:netlify\.app|herokuapp\.com|vercel\.app|github\.io)(?:/[\w.-]*)*',
            r'https?://[\w.-]+\.[a-z]{2,}(?:/[\w.-]*)*',
        ]
        for pattern in website_patterns:
            website_match = re.search(pattern, text, re.IGNORECASE)
            if website_match and 'linkedin' not in website_match.group(0).lower():
                url = website_match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                info['website'] = url
                break
        
        # Extract name - improved logic
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First line is usually the name (all caps or title case)
            first_line = lines[0]
            # Check if it looks like a name (not email, phone, or URL)
            if '@' not in first_line and not re.search(r'\d{3}', first_line) and '.' not in first_line:
                info['name'] = first_line
            # Try second or third line if first didn't work
            elif len(lines) > 1:
                for line in lines[1:4]:
                    if '@' not in line and not re.search(r'\d{3}', line) and len(line.split()) <= 4:
                        # Looks like a name (2-4 words, no numbers/emails)
                        info['name'] = line
                        break
        
        # Extract location - look for pattern "City | email | website" or standalone city names
        # Common pattern: "Bhiwandi | email | website"
        location_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\|'
        location_match = re.search(location_pattern, text)
        if location_match:
            potential_location = location_match.group(1).strip()
            # Make sure it's not a name or common word
            if potential_location.lower() not in ['summary', 'education', 'experience', 'skills', 'projects']:
                # Check if it's not part of the name (appears after name)
                if info['name'] and potential_location not in info['name']:
                    info['location'] = potential_location
        
        # Use spaCy NER as fallback for location if not found
        if not info['location'] and nlp:
            try:
                doc = nlp(text[:500])
                for ent in doc.ents:
                    if ent.label_ in ['GPE', 'LOC']:
                        # Avoid common false positives
                        if ent.text.lower() not in ['python', 'django', 'java', 'javascript']:
                            info['location'] = ent.text
                            break
            except Exception as e:
                logger.warning(f"spaCy location extraction failed: {e}")
        
        return info
    
    @staticmethod
    def parse_experiences(text: str) -> List[Dict]:
        """
        Extract work experience entries with date/company extraction.
        
        Each experience should have:
        - Company name
        - Job title
        - Start date
        - End date (or "Present")
        - Description/bullet points
        
        Args:
            text: Text from experience section
            
        Returns:
            List of experience dicts
        """
        experiences = []
        
        if not text:
            return experiences
        
        # Split by double newlines or clear separators
        entries = re.split(r'\n\s*\n', text)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            exp = {
                'company': None,
                'title': None,
                'start_date': None,
                'end_date': None,
                'description': None,
                'location': None,
            }
            
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                continue
            
            # Extract dates - improved patterns
            date_patterns = [
                r'(\w+\s+\d{4,5})\s*[-–—]\s*(\w+\s+\d{4}|present|current)',  # July 20224 -present
                r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|present|current)',  # July 2022 - July 2025
                r'(\d{1,2}/\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|present|current)',
                r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)',
            ]
            
            dates_found = False
            for pattern in date_patterns:
                date_match = re.search(pattern, entry, re.IGNORECASE)
                if date_match:
                    exp['start_date'] = date_match.group(1)
                    exp['end_date'] = date_match.group(2)
                    dates_found = True
                    break
            
            # Extract title and company from first line
            # Pattern: "Title | Company Date - Date"
            first_line = lines[0] if lines else ''
            title_company_pattern = r'([^|]+?)\s*\|\s*([^|]+?)(?:\s+\w+\s+\d{4})?$'
            title_company_match = re.search(title_company_pattern, first_line)
            
            if title_company_match:
                exp['title'] = title_company_match.group(1).strip()
                company_part = title_company_match.group(2).strip()
                # Remove date from company if present
                company_clean = re.sub(r'\s+\w+\s+\d{4,5}\s*[-–—].*$', '', company_part)
                exp['company'] = company_clean.strip()
            else:
                # Fallback: first line is title
                if lines:
                    # Remove dates from title line
                    title_clean = re.sub(r'\s+\w+\s+\d{4,5}\s*[-–—].*$', '', lines[0])
                    exp['title'] = title_clean.strip()
            
            # Use spaCy NER to extract company names if not found
            if not exp['company'] and nlp:
                try:
                    doc = nlp(entry[:300])
                    for ent in doc.ents:
                        if ent.label__ == 'ORG':
                            exp['company'] = ent.text
                            break
                except Exception as e:
                    logger.warning(f"spaCy NER for experience failed: {e}")
            
            # Extract description - everything after first line
            if len(lines) > 1:
                exp['description'] = '\n'.join(lines[1:])
            
            # Only add if we have at least company or title
            if exp['company'] or exp['title']:
                experiences.append(exp)
        
        return experiences
    
    @staticmethod
    def parse_education(text: str) -> List[Dict]:
        """
        Extract education entries with institution extraction.
        
        Each education entry should have:
        - Institution name
        - Degree
        - Field of study
        - Graduation date
        - GPA (if present)
        
        Args:
            text: Text from education section
            
        Returns:
            List of education dicts
        """
        education_entries = []
        
        if not text:
            return education_entries
        
        # Split by double newlines
        entries = re.split(r'\n\s*\n', text)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            edu = {
                'institution': None,
                'degree': None,
                'field_of_study': None,
                'graduation_date': None,
                'gpa': None,
            }
            
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                continue
            
            # Extract dates - improved pattern
            date_match = re.search(
                r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4})',
                entry
            )
            if date_match:
                edu['graduation_date'] = date_match.group(2)  # Use end date as graduation
            else:
                # Try single year
                year_match = re.search(r'\b(20\d{2})\b', entry)
                if year_match:
                    edu['graduation_date'] = year_match.group(1)
            
            # Extract GPA
            gpa_match = re.search(
                r'GPA:?\s*(\d+\.\d+)',
                entry,
                re.IGNORECASE
            )
            if gpa_match:
                edu['gpa'] = gpa_match.group(1)
            
            # Extract degree from first line
            # Pattern: "Degree Date - Date"
            first_line = lines[0] if lines else ''
            degree_match = re.search(r'^([^|]+?)(?:\s+\w+\s+\d{4})', first_line)
            if degree_match:
                edu['degree'] = degree_match.group(1).strip()
            else:
                # Check for degree keywords
                degree_keywords = [
                    'Bachelor', 'Master', 'PhD', 'Doctorate', 'Associate',
                    'B.S.', 'B.A.', 'M.S.', 'M.A.', 'MBA', 'Ph.D.', 'BCA', 'MCA'
                ]
                for keyword in degree_keywords:
                    if keyword in entry:
                        for line in lines:
                            if keyword in line:
                                edu['degree'] = line.strip()
                                break
                        break
            
            # Extract institution from second line or using pipe separator
            if len(lines) > 1:
                # Pattern: "Institution | Department | Location"
                institution_line = lines[1]
                institution_parts = [p.strip() for p in institution_line.split('|')]
                if institution_parts:
                    edu['institution'] = institution_parts[0]
            
            # Extract field of study - look for "in" or "of" patterns
            field_match = re.search(
                r'(?:in|of)\s+([A-Z][a-zA-Z\s]+?)(?:\n|,|$)',
                entry
            )
            if field_match:
                edu['field_of_study'] = field_match.group(1).strip()
            
            # Only add if we have at least institution or degree
            if edu['institution'] or edu['degree']:
                education_entries.append(edu)
        
        return education_entries
    
    @staticmethod
    def parse_skills(text: str) -> List[Dict]:
        """
        Extract skills with categorization.
        
        Skills can be:
        - Listed with bullet points
        - Comma-separated
        - Categorized (e.g., "Programming Languages: Python, Java")
        
        Args:
            text: Text from skills section
            
        Returns:
            List of skill dicts with name and optional category
        """
        skills = []
        
        if not text:
            return skills
        
        # Check for categorized skills (e.g., "Category: skill1, skill2")
        category_pattern = r'([A-Za-z\s]+):\s*([^\n]+)'
        category_matches = re.findall(category_pattern, text)
        
        if category_matches:
            # Skills are categorized
            for category, skills_text in category_matches:
                category = category.strip()
                # Split by comma or bullet points
                skill_items = re.split(r'[,•●○▪]', skills_text)
                for skill in skill_items:
                    skill = skill.strip()
                    if skill:
                        skills.append({
                            'name': skill,
                            'category': category
                        })
        else:
            # Skills are not categorized, extract all
            # Split by newlines, commas, or bullet points
            skill_items = re.split(r'[,\n•●○▪]', text)
            for skill in skill_items:
                skill = skill.strip()
                # Filter out very short items and common words
                if skill and len(skill) > 2 and skill.lower() not in ['and', 'or', 'the']:
                    skills.append({
                        'name': skill,
                        'category': None
                    })
        
        return skills
    
    @staticmethod
    def parse_resume(text: str) -> Dict:
        """
        Parse complete resume text into structured data.
        
        This is the main entry point that orchestrates all parsing.
        
        Args:
            text: Complete cleaned resume text
            
        Returns:
            Dict with all parsed sections
        """
        # Identify sections
        sections = SectionParserService.identify_sections(text)
        
        # Parse each section
        parsed_data = {
            'personal_info': None,
            'experiences': [],
            'education': [],
            'skills': [],
            'summary': None,
        }
        
        # Parse personal info (from top of document or personal_info section)
        if 'personal_info' in sections:
            parsed_data['personal_info'] = SectionParserService.parse_personal_info(
                sections['personal_info']
            )
        else:
            # Try to extract from first few lines
            first_lines = '\n'.join(text.split('\n')[:10])
            parsed_data['personal_info'] = SectionParserService.parse_personal_info(
                first_lines
            )
        
        # Parse experience
        if 'experience' in sections:
            parsed_data['experiences'] = SectionParserService.parse_experiences(
                sections['experience']
            )
        
        # Parse education
        if 'education' in sections:
            parsed_data['education'] = SectionParserService.parse_education(
                sections['education']
            )
        
        # Parse skills
        if 'skills' in sections:
            parsed_data['skills'] = SectionParserService.parse_skills(
                sections['skills']
            )
        
        # Extract summary if present
        if 'summary' in sections:
            parsed_data['summary'] = sections['summary']
        
        return parsed_data
