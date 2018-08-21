from unittest import TestCase
import ingestion.datasource as datasource


class TextDataSource(datasource.DataSource):
    def __init__(self):
        super().__init__("https://nghttp2.org/httpbin/html", response_format="text")

    def parse(self, data):
        return data


class JsonDataSource(datasource.DataSource):
    def __init__(self):
        super().__init__("https://api.coinmarketcap.com/v1/ticker", {"limit": 1})

    def parse(self, data):
        btc = data[0]
        return {"id": btc["id"], "symbol": btc["symbol"]}


class XmlDataSource(datasource.DataSource):
    def __init__(self):
        super().__init__("https://nghttp2.org/httpbin/xml", response_format="xml")

    def parse(self, xml):
        el = xml.getElementsByTagName("slide")
        return el[0].getAttribute("type")


class SoupDataSource(datasource.DataSource):
    def __init__(self):
        super().__init__("https://nghttp2.org/httpbin/html", response_format="soup")

    def parse(self, html):
        heading = html.find("h1")
        return heading.text


class TestDataSource(TestCase):
    def test_parse_text(self):
        ds = TextDataSource()
        data = ds.get()
        self.assertTrue(data.startswith("<!DOCTYPE html>"))

    def test_parse_json(self):
        ds = JsonDataSource()
        data = ds.get()
        self.assertEqual(data["id"], "bitcoin")
        self.assertEqual(data["symbol"], "BTC")

    def test_parse_xml(self):
        ds = XmlDataSource()
        data = ds.get()
        self.assertEqual(data, "all")

    def test_parse_soup(self):
        ds = SoupDataSource()
        data = ds.get()
        self.assertEqual(data, "Herman Melville - Moby-Dick")

    def test_parse_invalid(self):
        self.fail("TODO")

    def test_validation_error(self):
        self.fail("TODO")

    def test_parse_error(self):
        self.fail("TODO")

    def test_http_error(self):
        self.fail("TODO")

    def test_query_params(self):
        self.fail("TODO")