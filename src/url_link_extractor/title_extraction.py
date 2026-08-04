from __future__ import annotations

import asyncio
import time
from typing import Callable, List, Optional

from .encoding_detector import EncodingDetector
from .html_parser import HtmlParser
from .http_client import HttpClient
from .logger import get_logger
from .models import ExtractConfig, ExtractionStatus, ProgressInfo, TargetLink, TitleExtractionResult
from .robots_checker import RobotsChecker

logger = get_logger("url_link_extractor.title")

ProgressCallback = Optional[Callable[[ProgressInfo], None]]


class TitleExtractionService:
    def __init__(
        self,
        http_client: HttpClient,
        html_parser: HtmlParser,
        encoding_detector: EncodingDetector,
        robots_checker: Optional[RobotsChecker] = None,
    ) -> None:
        self._http_client = http_client
        self._html_parser = html_parser
        self._encoding_detector = encoding_detector
        self._robots_checker = robots_checker

    async def extract_titles(
        self,
        links: List[TargetLink],
        config: ExtractConfig,
        on_progress: ProgressCallback = None,
    ) -> List[TitleExtractionResult]:
        semaphore = asyncio.Semaphore(config.concurrency)
        total = len(links)
        completed = 0
        results: List[TitleExtractionResult] = [None] * total  # type: ignore[list-item]

        async def process_one(idx: int, link: TargetLink) -> None:
            nonlocal completed
            async with semaphore:
                result = await self._extract_single(link, config)
                results[idx] = result
                completed += 1
                if on_progress is not None:
                    on_progress(ProgressInfo(
                        completed=completed,
                        total=total,
                        last_url=link.url,
                        last_status=result.status,
                    ))

        tasks = [process_one(i, link) for i, link in enumerate(links)]
        await asyncio.gather(*tasks)
        return results

    async def _extract_single(
        self,
        link: TargetLink,
        config: ExtractConfig,
    ) -> TitleExtractionResult:
        if config.follow_robots_txt and self._robots_checker is not None:
            if not self._robots_checker.can_fetch(link.url):
                logger.info("title_skipped", url=link.url, reason="robots.txt")
                return TitleExtractionResult(
                    url=link.url, title="", status=ExtractionStatus.SKIPPED, error="Blocked by robots.txt"
                )

        start = time.monotonic()
        try:
            status_code, content, content_type = await self._http_client.get(link.url)
            duration_ms = int((time.monotonic() - start) * 1000)

            if status_code != 200:
                logger.warning("title_failed", url=link.url, status_code=status_code, duration_ms=duration_ms)
                return TitleExtractionResult(
                    url=link.url,
                    title="",
                    status=ExtractionStatus.FAILED,
                    error=f"HTTP状态码：{status_code}",
                )

            html = self._encoding_detector.detect_and_decode(content, content_type)
            title = self._html_parser.extract_title(html)
            logger.info("title_extracted", url=link.url, duration_ms=duration_ms, title=title)
            return TitleExtractionResult(
                url=link.url, title=title, status=ExtractionStatus.SUCCESS
            )

        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.error("title_error", url=link.url, duration_ms=duration_ms, error=str(exc))
            return TitleExtractionResult(
                url=link.url,
                title="",
                status=ExtractionStatus.FAILED,
                error=str(exc),
            )