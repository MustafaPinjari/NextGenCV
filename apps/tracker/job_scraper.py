import re
import urllib.request
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    """Minimal HTML parser that strips tags and extracts visible text."""

    SKIP_TAGS = {'script', 'style', 'head', 'nav', 'footer', 'header', 'aside'}

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.chunks.append(text)


def scrape_job_description(url: str) -> dict:
    """
    Fetch a job posting URL and return extracted text.
    Returns {'success': bool, 'text': str, 'error': str}
    """
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NextGenCV/2.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_html = resp.read().decode('utf-8', errors='ignore')

        parser = _TextExtractor()
        parser.feed(raw_html)
        full_text = '\n'.join(parser.chunks)

        # Collapse excessive whitespace
        full_text = re.sub(r'\n{3,}', '\n\n', full_text).strip()

        # Heuristic: keep the largest contiguous block that looks like a JD
        # (contains common JD keywords)
        jd_keywords = ['responsibilities', 'requirements', 'qualifications',
                        'experience', 'skills', 'about the role', 'what you']
        lines = full_text.split('\n')
        best_start, best_len, cur_start, cur_len = 0, 0, 0, 0
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in jd_keywords):
                if cur_len == 0:
                    cur_start = i
                cur_len += 1
                if cur_len > best_len:
                    best_len, best_start = cur_len, cur_start
            else:
                cur_len = 0

        if best_len > 3:
            # Take a window around the best block
            start = max(0, best_start - 5)
            end = min(len(lines), best_start + best_len + 30)
            extracted = '\n'.join(lines[start:end]).strip()
        else:
            # Fallback: first 3000 chars
            extracted = full_text[:3000]

        if len(extracted) < 100:
            return {'success': False, 'text': '', 'error': 'Could not extract meaningful job description from this URL.'}

        return {'success': True, 'text': extracted, 'error': ''}

    except Exception as e:
        return {'success': False, 'text': '', 'error': str(e)}
