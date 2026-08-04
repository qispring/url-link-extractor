from __future__ import annotations

from urllib.parse import urljoin, urlparse


class UrlResolver:
    @staticmethod
    def to_absolute(base_url: str, href: str) -> str:
        return urljoin(base_url, href)

    @staticmethod
    def match_prefix(url: str, prefix: str) -> bool:
        return url.startswith(prefix)

    @staticmethod
    def match_suffix(url: str, suffix: str) -> bool:
        return url.endswith(suffix)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def is_excluded_link(href: str) -> bool:
        lower = href.lower().strip()
        return (
            lower.startswith("javascript:")
            or lower.startswith("#")
            or lower.startswith("mailto:")
        )