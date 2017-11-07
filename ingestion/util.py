import urllib.parse
import urllib.request
import json


# TODO: allow these to take query params, and replace usage of ? in code
def geturl_json(url):
    ret = urllib.request.urlopen(url)
    return json.loads(ret.read().decode("utf-8"))


def geturl_text(url):
    ret = urllib.request.urlopen(url)
    return ret.read().decode("utf-8")


def list_to_set(l, key):
    ret = set()
    for i in l:
        ret.add(i[key])

    return ret


def list_to_dict(l, key):
    ret = {}
    for i in l:
        ret[i[key]] = i

    return ret
