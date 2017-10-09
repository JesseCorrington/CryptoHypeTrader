import urllib.parse
import urllib.request
import json
import ssl


# TODO: figure out how to make SSL work and get ride of this
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CONFIG = json.loads(open("config.json").read())

def geturl_json(url):
    ret = urllib.request.urlopen(url, context=ctx)
    return json.loads(ret.read())


def geturl_text(url):
    ret = urllib.request.urlopen(url, context=ctx)
    return ret.read().decode()