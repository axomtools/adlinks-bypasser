from utils import loadcache, savecache, getcached, setcache, getsession
from httpbypasser import bypasshttp

loadcache()

def bypassadlink(url):
    cached = getcached(url)
    if cached:
        return cached
    result = bypasshttp(url)
    if result:
        setcache(url, result)
        return result
    return None

def getfinalcontent(url):
    finalurl = bypassadlink(url)
    if not finalurl:
        return None
    session = getsession()
    try:
        resp = session.get(finalurl, timeout=30)
        return resp.text
    except:
        return None
