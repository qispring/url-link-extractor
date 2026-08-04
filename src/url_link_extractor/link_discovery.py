from __future__ import annotations

from typing import List, Optional

from .exceptions import EntryPageNotHtmlError, LinkLimitExceededError, UrlExtractorError
from .html_parser import HtmlParser
from .http_client import HttpClient
from .logger import get_logger
from .models import ExtractConfig, TargetLink
from .robots_checker import RobotsChecker
from .url_resolver import UrlResolver

logger = get_logger("url_link_extractor.discovery")


class LinkDiscoveryService:
    def __init__(
        self,
        http_client: HttpClient,
        html_parser: HtmlParser,
        robots_checker: Optional[RobotsChecker] = None,
    ) -> None:
        self._http_client = http_client
        self._html_parser = html_parser
        self._url_resolver = UrlResolver()
        self._robots_checker = robots_checker

    async def discover(
        self,
        entry_url: str,
        prefix: str,
        suffix: Optional[str],
        config: ExtractConfig,
    ) -> List[TargetLink]:
        status_code, content, content_type = await self._http_client.get(entry_url)

        if status_code != 200:
            raise UrlExtractorError(f"Entry URL returned status {status_code}: {entry_url}")

        if "text/html" not in content_type.lower():
            raise EntryPageNotHtmlError(f"Entry page is not HTML: content-type={content_type}")

        html = content.decode("utf-8", errors="replace")
        raw_links = self._html_parser.extract_links(html)
        logger.info("links_extracted", url=entry_url, count=len(raw_links))

        if config.follow_robots_txt and self._robots_checker is not None:
            await self._robots_checker.load_robots_txt(entry_url)

        seen: set[str] = set()
        filtered: List[str] = []

        for href in raw_links:
            if self._url_resolver.is_excluded_link(href):
                continue

            absolute = self._url_resolver.to_absolute(entry_url, href)

            if not self._url_resolver.match_prefix(absolute, prefix):
                continue

            if suffix and not self._url_resolver.match_suffix(absolute, suffix):
                continue

            if config.follow_robots_txt and self._robots_checker is not None:
                if not self._robots_checker.can_fetch(absolute):
                    continue

            if absolute in seen:
                continue

            seen.add(absolute)
            filtered.append(absolute)

        if len(filtered) > config.max_links:
            raise LinkLimitExceededError(
                f"Target links count {len(filtered)} exceeds max_links {config.max_links}"
            )

        logger.info("links_filtered", url=entry_url, total=len(raw_links), filtered=len(filtered))
        return [TargetLink(url=url, order=i) for i, url in enumerate(filtered)]