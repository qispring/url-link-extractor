import pytest

from url_link_extractor.html_parser import HtmlParser


class TestHtmlParser:
    def setup_method(self):
        self.parser = HtmlParser()

    def test_extract_links(self):
        html = '<html><body><a href="https://example.com/a.html">A</a><a href="https://example.com/b.html">B</a></body></html>'
        links = self.parser.extract_links(html)
        assert len(links) == 2
        assert "https://example.com/a.html" in links
        assert "https://example.com/b.html" in links

    def test_extract_links_no_href(self):
        html = '<html><body><a name="anchor">No href</a></body></html>'
        links = self.parser.extract_links(html)
        assert len(links) == 0

    def test_extract_links_empty(self):
        html = '<html><body>No links here</body></html>'
        links = self.parser.extract_links(html)
        assert len(links) == 0

    def test_extract_title(self):
        html = '<html><head><title>什么是码道CLI</title></head><body></body></html>'
        title = self.parser.extract_title(html)
        assert title == "什么是码道CLI"

    def test_extract_title_with_whitespace(self):
        html = '<html><head><title>  什么是码道CLI  \n</title></head><body></body></html>'
        title = self.parser.extract_title(html)
        assert title == "什么是码道CLI"

    def test_extract_title_missing(self):
        html = '<html><body>No title</body></html>'
        title = self.parser.extract_title(html)
        assert title == ""

    def test_extract_title_empty(self):
        html = '<html><head><title></title></head><body></body></html>'
        title = self.parser.extract_title(html)
        assert title == ""

    def test_malformed_html(self):
        html = '<html><body><a href="https://example.com/a.html">A</a><div>unclosed'
        links = self.parser.extract_links(html)
        assert len(links) == 1