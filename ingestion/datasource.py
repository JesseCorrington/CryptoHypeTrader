import urllib.parse
import urllib.request
import json
from xml.dom import minidom
from bs4 import BeautifulSoup


class DataSource:
    def __init__(self, url, params={}, format="json"):
        self.url = url
        self.params = params
        self.format = format  # json | text | xml | soup

    # TODO: add support for retries and centralized error handling/tracking
    def get(self):
        text = self._get(self.url, self.params)

        if self.format == "text":
            data = text
        elif self.format == "json":
            data = json.loads(text)
        elif self.format == "xml":
            data = minidom.parse(text)
        elif self.format == "soup":
            data = BeautifulSoup(text, "lxml")
        else:
            raise ValueError("Unsupported data source format: {0}".format(self.format))

        self.validate(data)
        data = self.pre_parse(data)
        return self.parse(data)

    def parse(self, data):
        raise NotImplementedError("DataSource's must implement parse")

    def pre_parse(self, data):
        return data

    def validate(self, data):
        pass

    @staticmethod
    def _get(url, params={}):
        str_params = urllib.parse.urlencode(params)
        if len(str_params) > 0:
            url += "?" + str_params

        ret = urllib.request.urlopen(url)

        return ret.read().decode("utf-8")

