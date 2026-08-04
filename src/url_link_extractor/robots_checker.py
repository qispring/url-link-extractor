from __future__ import annotations

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from .http_client import HttpClient
from .logger import get_logger

logger = get_logger("url_link_extractor.robots")


class RobotsChecker:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self._parsers: dict[str, RobotFileParser] = {}

    async def load_robots_txt(self, base_url: str) -> None:
        parsed = urlparse(base_url)
        root_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{root_url}/robots.txt"

        if root_url in self._parsers:
            return

        parser = RobotFileParser()
        try:
            status_code, content, _ = await self._http_client.get(robots_url)
            if status_code == 200:
                parser.parse(content.decode("utf-8", errors="replace").splitlines())
            logger.info("robots_loaded", url=robots_url, status_code=status_code)
        except Exception as exc:
            logger.warning("robots_fetch_failed", url=robots_url, error=str(exc))

        self._parsers[root_url] = parser

    def can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        root_url = f"{parsed.scheme}://{parsed.netloc}"
        parser = self._parsers.get(root_url)
        if parser is None:
            return True
        return parser.can_fetch("*", url)