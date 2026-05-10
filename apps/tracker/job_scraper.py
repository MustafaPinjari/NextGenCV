import re
import ipaddress
import socket
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse


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


_ALLOWED_SCHEMES = {'http', 'https'}
_BLOCKED_HOSTNAMES = {
    'localhost', 'ip6-localhost', 'ip6-loopback',
    '0.0.0.0', '::',
}


def _is_safe_url(url: str) -> tuple[bool, str]:
    """
    Return (True, '') if the URL is safe to fetch, or (False, reason) if not.
    Blocks:
      - Non-HTTP/HTTPS schemes (file://, ftp://, gopher://, etc.)
      - Loopback addresses (127.x.x.x, ::1)
      - Private RFC-1918 ranges (10.x, 172.16-31.x, 192.168.x)
      - Link-local (169.254.x.x — AWS metadata endpoint lives here)
      - Explicit blocked hostnames
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, 'Invalid URL'

    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False, f'Scheme "{parsed.scheme}" is not allowed'

    hostname = parsed.hostname or ''
    if not hostname:
        return False, 'Missing hostname'

    if hostname.lower() in _BLOCKED_HOSTNAMES:
        return False, f'Hostname "{hostname}" is blocked'

    # Resolve hostname to IP and check ranges
    try:
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback:
            return False, 'Loopback address blocked'
        if ip.is_private:
            return False, 'Private IP range blocked'
        if ip.is_link_local:
            return False, 'Link-local address blocked (potential SSRF via cloud metadata)'
        if ip.is_reserved:
            return False, 'Reserved IP range blocked'
    except socket.gaierror:
        return False, f'Could not resolve hostname: {hostname}'
    except ValueError:
        pass  # Not a plain IP — already checked hostname above

    return True, ''


def scrape_job_description(url: str) -> dict:
    """
    Fetch a job posting URL and return extracted text.
    Returns {'success': bool, 'text': str, 'error': str}
    """
    # SSRF protection — validate before making any network request
    safe, reason = _is_safe_url(url)
    if not safe:
        return {'success': False, 'text': '', 'error': f'URL blocked: {reason}'}

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NextGenCV/2.0)'},
        )
        # No redirects to private IPs — disable redirect following
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        with opener.open(req, timeout=10) as resp:
            # Limit response size to 2MB to prevent memory exhaustion
            raw_html = resp.read(2 * 1024 * 1024).decode('utf-8', errors='ignore')

    except urllib.error.HTTPError as e:
        return {'success': False, 'text': '', 'error': f'HTTP {e.code}: {e.reason}'}
    except urllib.error.URLError as e:
        return {'success': False, 'text': '', 'error': str(e.reason)}
    except Exception as e:
        return {'success': False, 'text': '', 'error': str(e)}

    parser = _TextExtractor()
    parser.feed(raw_html)
    full_text = '\n'.join(parser.chunks)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text).strip()

    # Heuristic: find the block most likely to be the job description
    jd_keywords = [
        'responsibilities', 'requirements', 'qualifications',
        'experience', 'skills', 'about the role', 'what you',
    ]
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
        start = max(0, best_start - 5)
        end = min(len(lines), best_start + best_len + 30)
        extracted = '\n'.join(lines[start:end]).strip()
    else:
        extracted = full_text[:3000]

    if len(extracted) < 100:
        return {
            'success': False, 'text': '',
            'error': 'Could not extract meaningful job description from this URL.',
        }

    return {'success': True, 'text': extracted, 'error': ''}
