import json
import hashlib
import random
import time
from datetime import datetime, timedelta
from curl_cffi import requests as curl_requests
from config import useragents, cacheenabled, cachefile

cachedata = {}

def loadcache():
    global cachedata
    if not cacheenabled:
        return
    try:
        with open(cachefile, 'r') as f:
            cachedata = json.load(f)
    except:
        cachedata = {}

def savecache():
    if not cacheenabled:
        return
    try:
        with open(cachefile, 'w') as f:
            json.dump(cachedata, f)
    except:
        pass

def getcachekey(url):
    return hashlib.md5(url.encode()).hexdigest()

def getcached(url, ttlhours=24):
    if not cacheenabled:
        return None
    key = getcachekey(url)
    if key in cachedata:
        entry = cachedata[key]
        expiry = datetime.fromisoformat(entry['expiry'])
        if datetime.now() < expiry:
            return entry['result']
        else:
            del cachedata[key]
    return None

def setcache(url, result):
    if not cacheenabled:
        return
    key = getcachekey(url)
    expiry = datetime.now() + timedelta(hours=24)
    cachedata[key] = {
        'result': result,
        'expiry': expiry.isoformat()
    }
    savecache()

def randomuseragent():
    return random.choice(useragents)

def getsession(impersonate="chrome131"):
    session = curl_requests.Session(impersonate=impersonate)
    session.headers.update({
        'User-Agent': randomuseragent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })
    return session
