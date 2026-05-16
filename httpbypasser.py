import re
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config import requesttimeout, maxredirects
from utils import getsession, randomuseragent

def extractjsredirects(html, baseurl):
    patterns = [
        r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'window\.location\.replace\([\'"]([^\'"]+)[\'"]\)',
        r'location\.href\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'window\.open\([\'"]([^\'"]+)[\'"]',
        r'window\.location\.assign\([\'"]([^\'"]+)[\'"]\)',
        r'setTimeout\(function\(\)\s*{\s*window\.location\.href\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'setTimeout\([\'"]([^\'"]+)[\'"]\s*,\s*\d+\)',
        r'var\s+\w+\s*=\s*[\'"]([^\'"]+)[\'"]\s*;\s*window\.location',
        r'setAttribute\(["\']href["\'],\s*["\']([^"\']+)["\']',
        r'data-url=["\']([^"\']+)["\']',
        r'data-href=["\']([^"\']+)["\']',
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?(?:free|continue|skip|access).*?</a>',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if match and not match.startswith('#') and match.startswith(('http','//')):
                return urljoin(baseurl, match)
    return None

def bypasslinkvertise(url, session):
    try:
        resp = session.get(url, timeout=requesttimeout)
        html = resp.text
        
        if 'api.linkvertise.com' in html:
            api_match = re.search(r'https?://api\.linkvertise\.com/v[0-9]+/redirects/consume/[a-f0-9]+', html)
            if not api_match:
                api_match = re.search(r'https?://api\.linkvertise\.com/[^\s\'"]+', html)
            if api_match:
                api_url = api_match.group(0)
                headers = {'Accept': 'application/json', 'Referer': url}
                api_resp = session.get(api_url, headers=headers)
                if api_resp.status_code == 200:
                    data = api_resp.json()
                    if 'link' in data:
                        return data['link']
                    if 'destination' in data:
                        return data['destination']
        
        direct = re.search(r'window\.open\(["\']([^"\']+)["\']\)', html)
        if direct:
            return direct.group(1)
        
        soup = BeautifulSoup(html, 'html.parser')
        for btn in soup.find_all('a', class_=re.compile(r'btn.*free|btn.*continue|btn.*skip', re.I)):
            href = btn.get('href')
            if href:
                return urljoin(url, href)
        
        token_match = re.search(r'data-token=["\']([a-f0-9]+)["\']', html)
        if token_match:
            token = token_match.group(1)
            api_resp = session.get(f'https://api.linkvertise.com/v1/redirects/consume/{token}')
            if api_resp.status_code == 200:
                return api_resp.json().get('link')
        
        return None
    except:
        return None

def bypasslootlabs(url, session):
    try:
        resp = session.get(url, timeout=requesttimeout)
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup.find_all('script'):
            if script.string and 'var destination' in script.string:
                match = re.search(r'destination\s*=\s*["\']([^"\']+)["\']', script.string)
                if match:
                    return match.group(1)
        form = soup.find('form', {'id': 'gateway-form'})
        if form and form.get('action'):
            data = {}
            for inp in form.find_all('input'):
                if inp.get('name'):
                    data[inp['name']] = inp.get('value', '')
            resp2 = session.post(urljoin(url, form['action']), data=data)
            if resp2.url != url:
                return resp2.url
        return None
    except:
        return None

def bypassadfly(url, session):
    try:
        resp = session.get(url, timeout=requesttimeout)
        html = resp.text
        match = re.search(r'var ysmm\s*=\s*["\']([^"\']+)["\']', html)
        if match:
            ysmm = match.group(1)
            decoded = ''
            for i in range(0, len(ysmm), 2):
                if i+1 < len(ysmm):
                    decoded += ysmm[i+1] + ysmm[i]
            final = re.sub(r'^.*?=', '', decoded)
            final = re.sub(r'%3A', ':', final)
            final = re.sub(r'%2F', '/', final)
            if final.startswith('http'):
                return final
        return None
    except:
        return None

def bypasstimerredirect(html, baseurl, session):
    timers = re.findall(r'setTimeout\(function\(\)\s*{\s*(?:window\.location\.href\s*=\s*["\']([^"\']+)["\']|location\.replace\(["\']([^"\']+)["\']\))\s*},\s*(\d+)\)', html, re.IGNORECASE)
    for match in timers:
        target = match[0] or match[1]
        delay = int(match[2])
        if delay > 0 and target:
            time.sleep(min(delay/1000, 10))
            return target
    return None

def bypasshttp(url):
    session = getsession()
    try:
        response = session.get(url, timeout=requesttimeout, allow_redirects=True, max_redirects=maxredirects)
        finalurl = response.url
        if finalurl != url:
            return finalurl
        
        html = response.text
        
        if 'linkvertise.com' in url.lower():
            result = bypasslinkvertise(url, session)
            if result:
                return result
        
        if 'lootlabs' in url.lower():
            result = bypasslootlabs(url, session)
            if result:
                return result
        
        if 'adf.ly' in url.lower() or 'q.gs' in url.lower():
            result = bypassadfly(url, session)
            if result:
                return result
        
        timer_target = bypasstimerredirect(html, finalurl, session)
        if timer_target:
            return urljoin(finalurl, timer_target)
        
        extracted = extractjsredirects(html, finalurl)
        if extracted:
            return extracted
        
        soup = BeautifulSoup(html, 'html.parser')
        meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta and meta.get('content'):
            match = re.search(r'url=([^"\']+)', meta['content'], re.I)
            if match:
                return urljoin(finalurl, match.group(1))
        
        return None
    except Exception as e:
        return None
