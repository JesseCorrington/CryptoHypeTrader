import urllib.parse
import urllib.request
import json
import time


def geturl_json(url):
    ret = urllib.request.urlopen(url)
    return json.loads(ret.read().decode("utf-8"))


def geturl_text(url):
    ret = urllib.request.urlopen(url)
    return ret.read().decode("utf-8")


# TODO: get rid of this and use datatime objects everything for consistency
def timestamp():
    return int(round(time.time() * 1000))
