import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import requesttimeout, maxredirects
from utils import getsession

def bypasshttp(url):
    session = getsession()
    try:
        resp = session.get(url, timeout=requesttimeout, allow_redirects=True, max_redirects=maxredirects)
        finalurl = resp.url
        if finalurl != url:
            return finalurl
        html = resp.text
        patterns = [
            r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'meta\s+http-equiv=["\']refresh["\']\s+content=["\']\d+;\s*url=([^"\']+)["\']'
        ]
        for pattern in patterns:
            m = re.search(pattern, html, re.I)
            if m:
                return urljoin(finalurl, m.group(1))
        return None
    except:
        return None
