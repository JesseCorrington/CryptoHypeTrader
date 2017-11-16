import urllib.parse
import urllib.request
import json
from xml.dom import minidom
from bs4 import BeautifulSoup


class HTTPError(Exception):
    pass


class ParseError(Exception):
    pass


class ValidationError(Exception):
    pass


class DataSource:
    """Abstract base class for data sources to derive from"""

    def __init__(self, url, params={}, response_format="json"):
        self.url = url
        self.params = params
        self.format = response_format  # json | text | xml | soup

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
            raise ValueError("Unsupported data source format: {}".format(self.format))

        error_msg = self.validate(data)
        if error_msg is not None:
            raise ValidationError(error_msg)

        try:
            data = self.pre_parse(data)
            return self.parse(data)
        except Exception as err:
            raise ParseError(str(err))

    def parse(self, data):
        raise NotImplementedError("DataSource's must implement parse")

    @staticmethod
    def pre_parse(data):
        return data

    @staticmethod
    def validate(data):
        return None

    @staticmethod
    def _get(url, params={}):
        str_params = urllib.parse.urlencode(params)
        if len(str_params) > 0:
            url += "?" + str_params

        try:
            ret = urllib.request.urlopen(url, timeout=20)
            return ret.read().decode("utf-8")
        except Exception as err:
            raise HTTPError(str(err))
