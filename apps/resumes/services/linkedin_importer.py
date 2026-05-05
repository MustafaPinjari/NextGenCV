"""
LinkedIn Profile Importer.

Parses a LinkedIn public profile URL and extracts structured resume data.
Uses requests + regex parsing since LinkedIn's official API requires OAuth
and partner approval. This scrapes the public profile page.

Note: LinkedIn's ToS restricts automated scraping. This is provided for
personal use (users importing their own data). For production, integrate
the official LinkedIn API with OAuth.
"""
import re
import logging
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Headers to mimic a real browser request
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


class LinkedInImporter:
    """
    Import resume data from a LinkedIn public profile URL.

    Usage:
        importer = LinkedInImporter()
        data = importer.import_profile('https://linkedin.com/in/username')
        # data = {name, headline, location, summary, experiences, education, skills}
    """

    def import_profile(self, url: str) -> Dict:
        """
        Import a LinkedIn profile and return structured resume data.

        Args:
            url: LinkedIn profile URL (https://linkedin.com/in/username)

        Returns:
            {
                'success': bool,
                'data': {name, headline, location, summary, experiences, education, skills},
                'error': str (if success=False),
                'source': 'linkedin',
            }
        """
        url = self._normalise_url(url)
        if not url:
            return {'success': False, 'error': 'Invalid LinkedIn URL', 'data': {}}

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 999:
                return {
                    'success': False,
                    'error': (
                        'LinkedIn blocked the request. '
                        'Please paste your profile text manually or use the PDF export from LinkedIn.'
                    ),
                    'data': {},
                }
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Could not fetch profile (HTTP {response.status_code}). '
                             'Make sure the profile is public.',
                    'data': {},
                }

            data = self._parse_html(response.text, url)
            return {'success': True, 'data': data, 'source': 'linkedin'}

        except requests.Timeout:
            return {'success': False, 'error': 'Request timed out. Try again.', 'data': {}}
        except requests.RequestException as e:
            logger.error(f"LinkedIn import failed for {url}: {e}")
            return {'success': False, 'error': str(e), 'data': {}}

    def _normalise_url(self, url: str) -> Optional[str]:
        """Ensure URL is a valid LinkedIn profile URL."""
        url = url.strip()
        if not url.startswith('http'):
            url = 'https://' + url
        # Must match linkedin.com/in/username pattern
        if not re.search(r'linkedin\.com/in/[\w\-]+', url):
            return None
        # Remove query params and fragments
        url = re.sub(r'[?#].*$', '', url)
        return url

    def _parse_html(self, html: str, url: str) -> Dict:
        """
        Parse LinkedIn profile HTML into structured data.
        LinkedIn's HTML structure changes frequently — this uses multiple
        fallback patterns for resilience.
        """
        data = {
            'name': '',
            'headline': '',
            'location': '',
            'summary': '',
            'linkedin_url': url,
            'experiences': [],
            'education': [],
            'skills': [],
        }

        # ── Name ──────────────────────────────────────────────────────────────
        name_patterns = [
            r'<h1[^>]*class="[^"]*top-card-layout__title[^"]*"[^>]*>([^<]+)</h1>',
            r'"firstName":"([^"]+)","lastName":"([^"]+)"',
            r'<title>([^|<]+)',
        ]
        for pattern in name_patterns:
            m = re.search(pattern, html)
            if m:
                if m.lastindex == 2:
                    data['name'] = f"{m.group(1)} {m.group(2)}".strip()
                else:
                    name = m.group(1).strip()
                    # Clean " | LinkedIn" suffix from title
                    name = re.sub(r'\s*\|.*$', '', name).strip()
                    if name and len(name) < 100:
                        data['name'] = name
                break

        # ── Headline ──────────────────────────────────────────────────────────
        headline_patterns = [
            r'<h2[^>]*class="[^"]*top-card-layout__headline[^"]*"[^>]*>([^<]+)</h2>',
            r'"headline":"([^"]+)"',
        ]
        for pattern in headline_patterns:
            m = re.search(pattern, html)
            if m:
                data['headline'] = self._clean_text(m.group(1))
                break

        # ── Location ──────────────────────────────────────────────────────────
        loc_patterns = [
            r'<span[^>]*class="[^"]*top-card__subline-item[^"]*"[^>]*>([^<]+)</span>',
            r'"geoLocationName":"([^"]+)"',
        ]
        for pattern in loc_patterns:
            m = re.search(pattern, html)
            if m:
                data['location'] = self._clean_text(m.group(1))
                break

        # ── Summary / About ───────────────────────────────────────────────────
        summary_patterns = [
            r'<div[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</div>',
            r'"summary":"([^"]+)"',
        ]
        for pattern in summary_patterns:
            m = re.search(pattern, html, re.DOTALL)
            if m:
                text = self._strip_html(m.group(1))
                if len(text) > 50:
                    data['summary'] = text[:1000]
                    break

        # ── Experience ────────────────────────────────────────────────────────
        # Try JSON-LD structured data first
        json_ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        if json_ld:
            try:
                import json
                ld = json.loads(json_ld.group(1))
                if isinstance(ld, dict) and ld.get('@type') == 'Person':
                    data['name'] = data['name'] or ld.get('name', '')
                    for work in ld.get('worksFor', []):
                        if isinstance(work, dict):
                            data['experiences'].append({
                                'company': work.get('name', ''),
                                'role': work.get('jobTitle', ''),
                                'description': '',
                                'start_date': None,
                                'end_date': None,
                            })
            except Exception:
                pass

        # HTML fallback for experience
        if not data['experiences']:
            exp_section = re.search(
                r'experience.*?(?=education|skills|$)',
                html, re.IGNORECASE | re.DOTALL
            )
            if exp_section:
                exp_html = exp_section.group(0)
                # Extract role + company pairs
                role_company = re.findall(
                    r'<span[^>]*>([^<]{5,80})</span>.*?<span[^>]*>([^<]{3,80})</span>',
                    exp_html[:5000]
                )
                seen = set()
                for role, company in role_company[:10]:
                    role = self._clean_text(role)
                    company = self._clean_text(company)
                    key = f"{role}|{company}"
                    if key not in seen and len(role) > 3 and len(company) > 2:
                        seen.add(key)
                        data['experiences'].append({
                            'company': company,
                            'role': role,
                            'description': '',
                            'start_date': None,
                            'end_date': None,
                        })

        # ── Skills ────────────────────────────────────────────────────────────
        skills_section = re.search(
            r'skills.*?(?=recommendations|accomplishments|$)',
            html, re.IGNORECASE | re.DOTALL
        )
        if skills_section:
            skill_names = re.findall(
                r'<span[^>]*aria-hidden="true"[^>]*>([^<]{2,50})</span>',
                skills_section.group(0)[:3000]
            )
            seen_skills = set()
            for skill in skill_names:
                skill = self._clean_text(skill)
                if skill and skill not in seen_skills and len(skill) > 1:
                    seen_skills.add(skill)
                    data['skills'].append({'name': skill, 'category': 'General'})

        return data

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove HTML entities and extra whitespace."""
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&#\d+;', '', text)
        return text.strip()

    @staticmethod
    def _strip_html(html: str) -> str:
        """Remove all HTML tags and clean whitespace."""
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
