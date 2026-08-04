import pytest

from url_link_extractor.url_resolver import UrlResolver


class TestUrlResolver:
    def test_to_absolute_relative(self):
        result = UrlResolver.to_absolute("https://example.com/dir/", "page.html")
        assert result == "https://example.com/dir/page.html"

    def test_to_absolute_absolute(self):
        result = UrlResolver.to_absolute("https://example.com/dir/", "https://other.com/page.html")
        assert result == "https://other.com/page.html"

    def test_to_absolute_root(self):
        result = UrlResolver.to_absolute("https://example.com/dir/", "/page.html")
        assert result == "https://example.com/page.html"

    def test_match_prefix_true(self):
        assert UrlResolver.match_prefix("https://example.com/page.html", "https://example.com/") is True

    def test_match_prefix_false(self):
        assert UrlResolver.match_prefix("https://other.com/page.html", "https://example.com/") is False

    def test_match_suffix_true(self):
        assert UrlResolver.match_suffix("https://example.com/page.html", ".html") is True

    def test_match_suffix_false(self):
        assert UrlResolver.match_suffix("https://example.com/page.pdf", ".html") is False

    def test_is_valid_url_https(self):
        assert UrlResolver.is_valid_url("https://example.com/page.html") is True

    def test_is_valid_url_http(self):
        assert UrlResolver.is_valid_url("http://example.com/page.html") is True

    def test_is_valid_url_invalid(self):
        assert UrlResolver.is_valid_url("abc") is False

    def test_is_valid_url_empty(self):
        assert UrlResolver.is_valid_url("") is False

    def test_is_excluded_javascript(self):
        assert UrlResolver.is_excluded_link("javascript:void(0)") is True

    def test_is_excluded_anchor(self):
        assert UrlResolver.is_excluded_link("#section1") is True

    def test_is_excluded_mailto(self):
        assert UrlResolver.is_excluded_link("mailto:test@example.com") is True

    def test_is_excluded_normal(self):
        assert UrlResolver.is_excluded_link("https://example.com/page.html") is False