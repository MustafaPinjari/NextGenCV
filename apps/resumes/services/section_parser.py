"""
Section Parser Service - robust resume section detection and data extraction.
Handles real-world PDF output: ALL CAPS headers, inline headers, varied formats.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found. NER features will be limited.")
        nlp = None
        SPACY_AVAILABLE = False
except ImportError:
    nlp = None
    SPACY_AVAILABLE = False


# ── Section header patterns ────────────────────────────────────────────────
# Matches headers in any casing, with or without trailing colon/dash
SECTION_PATTERNS = {
    'experience': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:work\s+)?(?:professional\s+)?(?:relevant\s+)?'
        r'(?:experience|employment|work\s+history|career\s+history|positions?\s+held)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'education': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:education(?:al)?\s*(?:background|qualifications?)?|academic\s+(?:background|history)|qualifications?)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'skills': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:(?:technical\s+|core\s+|key\s+|professional\s+)?skills?'
        r'|competenc(?:y|ies)|expertise|technologies?|tech\s+stack|tools?(?:\s+&\s+technologies?)?)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'summary': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:(?:professional\s+)?summary|profile|objective|about\s+(?:me|myself)|career\s+(?:summary|objective)|overview)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'projects': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:projects?|portfolio|personal\s+projects?|key\s+projects?|notable\s+projects?)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'certifications': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:certifications?|certificates?|licenses?|credentials?|accreditations?)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'awards': re.compile(
        r'^[\s\-_=*#]*'
        r'(?:awards?|honors?|achievements?|accomplishments?|recognition)'
        r'[\s\-_:]*$',
        re.IGNORECASE
    ),
    'languages': re.compile(
        r'^[\s\-_=*#]*languages?[\s\-_:]*$',
        re.IGNORECASE
    ),
}

MONTH_NAMES = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
DATE_PATTERN = re.compile(
    rf'({MONTH_NAMES}\.?\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})\s*[-–—to]+\s*({MONTH_NAMES}\.?\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}}|present|current|now)',
    re.IGNORECASE
)


class SectionParserService:

    @staticmethod
    def identify_sections(text: str) -> Dict[str, str]:
        lines = text.split('\n')
        section_indices = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or len(stripped) > 80:
                continue
            for section_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(stripped):
                    section_indices.append((i, section_name))
                    break

        sections = {}
        for idx, (line_num, section_name) in enumerate(section_indices):
            end_line = section_indices[idx + 1][0] if idx + 1 < len(section_indices) else len(lines)
            content = '\n'.join(lines[line_num + 1:end_line]).strip()
            if content:
                sections[section_name] = content

        return sections

    @staticmethod
    def parse_personal_info(text: str) -> Dict:
        info = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'website': '',
        }

        # Email
        email_m = re.search(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b', text)
        if email_m:
            info['email'] = email_m.group(0)

        # Phone — broad international patterns
        phone_m = re.search(
            r'(?:\+\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
            r'|\+\d{1,3}\s?\d{6,12}'
            r'|\b\d{10}\b',
            text
        )
        if phone_m:
            info['phone'] = phone_m.group(0).strip()

        # LinkedIn
        li_m = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?', text, re.IGNORECASE)
        if li_m:
            url = li_m.group(0)
            info['linkedin'] = url if url.startswith('http') else 'https://' + url

        # GitHub / website
        gh_m = re.search(r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?', text, re.IGNORECASE)
        if gh_m:
            url = gh_m.group(0)
            info['website'] = url if url.startswith('http') else 'https://' + url
        else:
            web_m = re.search(r'https?://[^\s,|]+', text)
            if web_m and 'linkedin' not in web_m.group(0).lower():
                info['website'] = web_m.group(0)

        # Name — first non-empty line that looks like a name
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:5]:
            # Skip lines that are clearly not names
            if re.search(r'[@|/\\]|\d{3}|http|linkedin|github|\.com', line, re.IGNORECASE):
                continue
            words = line.split()
            if 1 < len(words) <= 5 and all(re.match(r"[A-Za-z'\-\.]+$", w) for w in words):
                info['name'] = line
                break

        # Location — look for "City, State" or "City, Country" patterns
        loc_patterns = [
            r'\b([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z]+)\b',  # City, ST or City, Country
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[|,]\s*(?=[A-Z])',  # City | or City,
        ]
        for pat in loc_patterns:
            loc_m = re.search(pat, text)
            if loc_m:
                candidate = loc_m.group(0).strip().rstrip(',|').strip()
                # Exclude common false positives
                if candidate.lower() not in ('summary', 'education', 'experience', 'skills', 'projects'):
                    info['location'] = candidate
                    break

        # spaCy fallback for location
        if not info['location'] and nlp:
            try:
                doc = nlp(text[:600])
                for ent in doc.ents:
                    if ent.label_ in ('GPE', 'LOC') and len(ent.text) > 2:
                        if not re.search(r'\d', ent.text):
                            info['location'] = ent.text
                            break
            except Exception:
                pass

        return info

    @staticmethod
    def parse_experiences(text: str) -> List[Dict]:
        if not text:
            return []

        experiences = []
        # Split on blank lines or lines that look like new job entries
        blocks = re.split(r'\n\s*\n', text.strip())

        for block in blocks:
            block = block.strip()
            if not block or len(block) < 20:
                continue

            exp = {
                'company': '',
                'title': '',
                'start_date': None,
                'end_date': None,
                'description': '',
                'achievements': '',
                'location': '',
            }

            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            # Extract dates from the whole block
            date_m = DATE_PATTERN.search(block)
            if date_m:
                exp['start_date'] = date_m.group(1).strip()
                exp['end_date'] = date_m.group(2).strip()

            # Parse first 1-3 lines for title/company
            header_lines = lines[:3]
            header_text = ' | '.join(header_lines)

            # Pattern: "Title | Company | Location | Dates"
            # Pattern: "Title at Company"
            # Pattern: "Company\nTitle\nDates"
            pipe_parts = [p.strip() for p in re.split(r'\s*[|,]\s*', header_lines[0]) if p.strip()]

            if len(pipe_parts) >= 2:
                exp['title'] = pipe_parts[0]
                # Remove date from company part
                company_raw = pipe_parts[1]
                exp['company'] = re.sub(DATE_PATTERN, '', company_raw).strip().rstrip('–—-').strip()
            elif re.search(r'\bat\b', header_lines[0], re.IGNORECASE):
                parts = re.split(r'\s+at\s+', header_lines[0], maxsplit=1, flags=re.IGNORECASE)
                exp['title'] = parts[0].strip()
                exp['company'] = re.sub(DATE_PATTERN, '', parts[1]).strip() if len(parts) > 1 else ''
            else:
                # First line = title, second line = company
                exp['title'] = re.sub(DATE_PATTERN, '', lines[0]).strip()
                if len(lines) > 1:
                    second = re.sub(DATE_PATTERN, '', lines[1]).strip()
                    # Only use as company if it doesn't look like a bullet
                    if not second.startswith(('•', '-', '*', '–')):
                        exp['company'] = second

            # spaCy ORG fallback
            if not exp['company'] and nlp:
                try:
                    doc = nlp(block[:300])
                    for ent in doc.ents:
                        if ent.label_ == 'ORG':
                            exp['company'] = ent.text
                            break
                except Exception:
                    pass

            # Separate bullet achievements from prose description
            bullet_lines = []
            prose_lines = []
            content_start = 1 if (exp['title'] or exp['company']) else 0
            for line in lines[content_start:]:
                if re.match(r'^[•\-\*–▪●○]\s*', line) or re.match(r'^\d+\.\s+', line):
                    bullet_lines.append(re.sub(r'^[•\-\*–▪●○\d\.]\s*', '', line).strip())
                elif line and not DATE_PATTERN.search(line):
                    prose_lines.append(line)

            exp['achievements'] = '\n'.join(bullet_lines)
            exp['description'] = ' '.join(prose_lines[:3])  # first few prose lines as description

            if exp['title'] or exp['company']:
                experiences.append(exp)

        return experiences

    @staticmethod
    def parse_education(text: str) -> List[Dict]:
        if not text:
            return []

        education = []
        blocks = re.split(r'\n\s*\n', text.strip())

        for block in blocks:
            block = block.strip()
            if not block or len(block) < 10:
                continue

            edu = {
                'institution': '',
                'degree': '',
                'field_of_study': '',
                'graduation_date': '',
                'gpa': None,
            }

            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            # GPA
            gpa_m = re.search(r'GPA\s*:?\s*(\d+\.\d+)', block, re.IGNORECASE)
            if gpa_m:
                edu['gpa'] = gpa_m.group(1)

            # Dates
            date_m = DATE_PATTERN.search(block)
            if date_m:
                edu['graduation_date'] = date_m.group(2).strip()
            else:
                year_m = re.search(r'\b(20\d{2}|19\d{2})\b', block)
                if year_m:
                    edu['graduation_date'] = year_m.group(1)

            # Degree keywords
            degree_re = re.compile(
                r'\b(Bachelor(?:\'s)?(?:\s+of\s+\w+)?|Master(?:\'s)?(?:\s+of\s+\w+)?|'
                r'B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|MBA|Ph\.?D\.?|'
                r'BCA|MCA|B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|'
                r'Associate(?:\'s)?|Diploma|Certificate)\b',
                re.IGNORECASE
            )

            for line in lines:
                dm = degree_re.search(line)
                if dm and not edu['degree']:
                    edu['degree'] = re.sub(DATE_PATTERN, '', line).strip()
                    # Extract field from "Bachelor of Science in Computer Science"
                    field_m = re.search(r'\bin\s+([A-Za-z\s]+?)(?:\s*,|\s*\(|\s*\d|$)', line, re.IGNORECASE)
                    if field_m:
                        edu['field_of_study'] = field_m.group(1).strip()

            # Institution — first line that doesn't contain degree keywords and isn't a date
            for line in lines:
                clean = re.sub(DATE_PATTERN, '', line).strip()
                if not degree_re.search(clean) and len(clean) > 3 and not re.match(r'^[\d\s,]+$', clean):
                    edu['institution'] = clean
                    break

            if edu['institution'] or edu['degree']:
                education.append(edu)

        return education

    @staticmethod
    def parse_skills(text: str) -> List[Dict]:
        if not text:
            return []

        skills = []
        seen = set()

        # Categorised: "Languages: Python, Java"
        cat_pattern = re.compile(r'^([A-Za-z][A-Za-z\s/&+]{2,40})\s*:\s*(.+)$', re.MULTILINE)
        cat_matches = cat_pattern.findall(text)

        if cat_matches:
            for category, skills_text in cat_matches:
                category = category.strip()
                for skill in re.split(r'[,|•·/]', skills_text):
                    skill = skill.strip().strip('•-–*')
                    if skill and len(skill) > 1 and skill.lower() not in seen:
                        seen.add(skill.lower())
                        skills.append({'name': skill, 'category': category})
        else:
            # Flat list — split by commas, bullets, pipes, newlines
            for item in re.split(r'[,\n•·|/●▪]', text):
                skill = item.strip().strip('•-–*').strip()
                if skill and 1 < len(skill) < 60 and skill.lower() not in seen:
                    if skill.lower() not in ('and', 'or', 'the', 'with', 'using'):
                        seen.add(skill.lower())
                        skills.append({'name': skill, 'category': None})

        return skills

    @staticmethod
    def parse_resume(text: str) -> Dict:
        sections = SectionParserService.identify_sections(text)

        parsed_data = {
            'personal_info': None,
            'experiences': [],
            'education': [],
            'skills': [],
            'summary': '',
        }

        # Personal info — always try from top of document
        header_text = '\n'.join(text.split('\n')[:15])
        parsed_data['personal_info'] = SectionParserService.parse_personal_info(header_text)

        if 'experience' in sections:
            parsed_data['experiences'] = SectionParserService.parse_experiences(sections['experience'])

        if 'education' in sections:
            parsed_data['education'] = SectionParserService.parse_education(sections['education'])

        if 'skills' in sections:
            parsed_data['skills'] = SectionParserService.parse_skills(sections['skills'])

        if 'summary' in sections:
            parsed_data['summary'] = sections['summary'].strip()

        # Fallback: if no sections found at all, try to extract skills from full text
        if not parsed_data['skills'] and not sections:
            parsed_data['skills'] = SectionParserService.parse_skills(text)

        logger.info(
            f"Parsed resume: personal_info={'yes' if parsed_data['personal_info'] else 'no'}, "
            f"experiences={len(parsed_data['experiences'])}, "
            f"education={len(parsed_data['education'])}, "
            f"skills={len(parsed_data['skills'])}"
        )

        return parsed_data
