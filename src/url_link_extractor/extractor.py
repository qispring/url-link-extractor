from __future__ import annotations

import asyncio
import time
from typing import Callable, Optional

from .encoding_detector import EncodingDetector
from .excel_exporter import ExcelExporter
from .exceptions import (
    EntryUrlUnreachableError,
    UrlExtractorError,
)
from .html_parser import HtmlParser
from .http_client import HttpClient
from .input_validator import InputValidator
from .link_discovery import LinkDiscoveryService
from .logger import get_logger
from .models import ExtractConfig, ExtractRequest, ExtractResult, ProgressInfo
from .result_builder import ResultBuilder
from .robots_checker import RobotsChecker
from .title_extraction import TitleExtractionService

logger = get_logger("url_link_extractor.extractor")

ProgressCallback = Optional[Callable[[ProgressInfo], None]]


class Extractor:
    def __init__(self) -> None:
        self._validator = InputValidator()
        self._html_parser = HtmlParser()
        self._encoding_detector = EncodingDetector()
        self._result_builder = ResultBuilder()
        self._excel_exporter = ExcelExporter()

    async def _run_async(
        self,
        request: ExtractRequest,
        on_progress: ProgressCallback = None,
    ) -> ExtractResult:
        config = request.config or ExtractConfig()

        validation = self._validator.validate(request)
        if not validation.valid:
            raise UrlExtractorError(f"Validation failed: {'; '.join(validation.errors)}")

        http_client = HttpClient(
            timeout=config.timeout,
            retry_count=config.retry_count,
            interval=config.interval,
        )

        robots_checker = RobotsChecker(http_client) if config.follow_robots_txt else None

        link_discovery = LinkDiscoveryService(
            http_client=http_client,
            html_parser=self._html_parser,
            robots_checker=robots_checker,
        )

        title_extraction = TitleExtractionService(
            http_client=http_client,
            html_parser=self._html_parser,
            encoding_detector=self._encoding_detector,
            robots_checker=robots_checker,
        )

        start_time = time.monotonic()

        try:
            logger.info("extract_start", url=request.url, prefix=request.prefix)

            links = await link_discovery.discover(
                entry_url=request.url,
                prefix=request.prefix,
                suffix=request.suffix,
                config=config,
            )

            if not links:
                logger.info("no_links_found", url=request.url)
                return self._result_builder.build(links, [], start_time)

            title_results = await title_extraction.extract_titles(
                links=links,
                config=config,
                on_progress=on_progress,
            )

            result = self._result_builder.build(links, title_results, start_time)

            if config.output_excel:
                try:
                    self._excel_exporter.export(result, config.output_path)
                except Exception as exc:
                    logger.error("excel_export_failed", error=str(exc))

            logger.info(
                "extract_complete",
                url=request.url,
                total=result.statistics.total,
                success=result.statistics.success,
                failed=result.statistics.failed,
                duration=result.statistics.duration,
            )

            return result

        finally:
            await http_client.close()


_extractor: Optional[Extractor] = None


def _get_extractor() -> Extractor:
    global _extractor
    if _extractor is None:
        _extractor = Extractor()
    return _extractor


def extract(request: ExtractRequest, on_progress: ProgressCallback = None) -> ExtractResult:
    return asyncio.run(_get_extractor()._run_async(request, on_progress))