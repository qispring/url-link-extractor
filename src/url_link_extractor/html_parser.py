from __future__ import annotations

from typing import List, Optional

from bs4 import BeautifulSoup


class HtmlParser:
    def __init__(self) -> None:
        self._parser = "lxml"

    def extract_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, self._parser)
        links: List[str] = []
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if href:
                links.append(href.strip())
        return links

    def extract_title(self, html: str) -> str:
        soup = BeautifulSoup(html, self._parser)
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        return ""

    def parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, self._parser)