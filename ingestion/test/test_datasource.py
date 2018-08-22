from unittest import TestCase
import ingestion.datasource as datasource


class TestDataSource(TestCase):
    def test_parse_text(self):
        class TextDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/html", response_format="text")

            def parse(self, data):
                return data

        ds = TextDataSource()
        data = ds.get()
        self.assertTrue(data.startswith("<!DOCTYPE html>"))

    def test_parse_json(self):
        class JsonDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/get")

            def parse(self, data):
                return data["url"]

        ds = JsonDataSource()
        data = ds.get()
        self.assertEqual(data, "https://nghttp2.org/httpbin/get")

    def test_parse_xml(self):
        class XmlDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/xml", response_format="xml")

            def parse(self, xml):
                el = xml.getElementsByTagName("slide")
                return el[0].getAttribute("type")

        ds = XmlDataSource()
        data = ds.get()
        self.assertEqual(data, "all")

    def test_parse_soup(self):
        class SoupDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/html", response_format="soup")

            def parse(self, html):
                heading = html.find("h1")
                return heading.text

        ds = SoupDataSource()
        data = ds.get()
        self.assertEqual(data, "Herman Melville - Moby-Dick")

    def test_invalid_format_error(self):
        class InvalidFormatDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/html", response_format="binary")

        ds = InvalidFormatDataSource()
        with self.assertRaises(ValueError):
            ds.get()

    def test_validation_error(self):
        class ValidationErrorDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/get")

            def parse(self, data):
                return data

            def validate(self, data):
                return "error: invalid format"

        ds = ValidationErrorDataSource()
        with self.assertRaises(datasource.ValidationError):
            ds.get()

    def test_parse_error(self):
        class ParseErrorDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/get")

            def parse(self, data):
                return data["invalid_attribute"]

        ds = ParseErrorDataSource()
        with self.assertRaises(datasource.ParseError):
            ds.get()

    def test_parse_notimpl_error(self):
        class NoParseDatasource(datasource.DataSource):
            def __init__(self):
                super().__init__("https://nghttp2.org/httpbin/html", response_format="text")

        ds = NoParseDatasource()
        with self.assertRaises(datasource.ParseError):
            ds.get()

    def test_http_error(self):
        class HttpErrorDataSource(datasource.DataSource):
            def __init__(self):
                super().__init__("http://doesnotexist239393932399320.com")

        ds = HttpErrorDataSource()
        with self.assertRaises(datasource.HTTPError):
            ds.get()
