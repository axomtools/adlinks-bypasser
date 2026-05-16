from utils import loadcache, savecache, getcached, setcache
from httpbypasser import bypasshttp
from browserbypasser import bypassbrowser
from config import usebrowser

loadcache()

def bypassadlink(url):
    cached = getcached(url)
    if cached:
        return cached
    result = None
    if usebrowser:
        result = bypassbrowser(url)
    if not result:
        result = bypasshttp(url)
    if result:
        setcache(url, result)
        return result
    return None

def getfinalcontent(url):
    finalurl = bypassadlink(url)
    if not finalurl:
        return None
    from utils import getsession
    session = getsession()
    try:
        resp = session.get(finalurl, timeout=30)
        return resp.text
    except:
        return None
