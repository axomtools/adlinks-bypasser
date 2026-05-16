import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import requesttimeout, maxredirects
from utils import getsession

def extractfromhtml(html, baseurl):
    soup = BeautifulSoup(html, 'html.parser')
    patterns = [
        r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'window\.location\.replace\([\'"]([^\'"]+)[\'"]\)',
        r'location\.href\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'window\.open\([\'"]([^\'"]+)[\'"]',
        r'window\.location\.assign\([\'"]([^\'"]+)[\'"]\)',
        r'var\s+\w+\s*=\s*[\'"]([^\'"]+)[\'"]\s*;\s*window\.location',
        r'setAttribute\(["\']href["\'],\s*["\']([^"\']+)["\']',
        r'data-url=["\']([^"\']+)["\']',
        r'data-href=["\']([^"\']+)["\']'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if match and not match.startswith('#'):
                return urljoin(baseurl, match)
    meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta and meta.get('content'):
        content = meta.get('content')
        match = re.search(r'url=([^"\']+)', content, re.IGNORECASE)
        if match:
            return urljoin(baseurl, match.group(1))
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True).lower()
        if 'free' in text or 'continue' in text or 'access' in text or 'skip' in text:
            return urljoin(baseurl, link['href'])
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            for line in script.string.split('\n'):
                if 'window.location' in line or 'location.href' in line:
                    match = re.search(r'[\'"](https?://[^\'"]+)[\'"]', line)
                    if match:
                        return match.group(1)
    return None

def bypasshttp(url):
    session = getsession()
    try:
        response = session.get(url, timeout=requesttimeout, allow_redirects=True, max_redirects=maxredirects)
        finalurl = response.url
        if finalurl != url:
            return finalurl
        extracted = extractfromhtml(response.text, finalurl)
        if extracted:
            return extracted
        return None
    except Exception:
        return None
