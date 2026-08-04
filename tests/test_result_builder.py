import pytest

from url_link_extractor.models import (
    ErrorReport,
    ExtractResult,
    ExtractStatistics,
    ExtractionStatus,
    LinkTitlePair,
    TargetLink,
    TitleExtractionResult,
)
from url_link_extractor.result_builder import ResultBuilder


class TestResultBuilder:
    def setup_method(self):
        self.builder = ResultBuilder()

    def test_build_basic(self):
        links = [
            TargetLink(url="https://example.com/a.html", order=0),
            TargetLink(url="https://example.com/b.html", order=1),
        ]
        title_results = [
            TitleExtractionResult(url="https://example.com/a.html", title="Title A", status=ExtractionStatus.SUCCESS),
            TitleExtractionResult(url="https://example.com/b.html", title="Title B", status=ExtractionStatus.SUCCESS),
        ]
        result = self.builder.build(links, title_results, 0)

        assert len(result.results) == 2
        assert result.results[0].url == "https://example.com/a.html"
        assert result.results[0].title == "Title A"
        assert result.results[1].url == "https://example.com/b.html"
        assert result.results[1].title == "Title B"

    def test_statistics(self):
        links = [
            TargetLink(url="https://example.com/a.html", order=0),
            TargetLink(url="https://example.com/b.html", order=1),
            TargetLink(url="https://example.com/c.html", order=2),
        ]
        title_results = [
            TitleExtractionResult(url="https://example.com/a.html", title="A", status=ExtractionStatus.SUCCESS),
            TitleExtractionResult(url="https://example.com/b.html", title="", status=ExtractionStatus.FAILED, error="timeout"),
            TitleExtractionResult(url="https://example.com/c.html", title="", status=ExtractionStatus.SKIPPED, error="robots"),
        ]
        result = self.builder.build(links, title_results, 0)

        assert result.statistics.total == 3
        assert result.statistics.success == 1
        assert result.statistics.failed == 1
        assert result.statistics.skipped == 1

    def test_error_report(self):
        links = [
            TargetLink(url="https://example.com/a.html", order=0),
            TargetLink(url="https://example.com/b.html", order=1),
        ]
        title_results = [
            TitleExtractionResult(url="https://example.com/a.html", title="A", status=ExtractionStatus.SUCCESS),
            TitleExtractionResult(url="https://example.com/b.html", title="", status=ExtractionStatus.FAILED, error="timeout"),
        ]
        result = self.builder.build(links, title_results, 0)

        assert len(result.errors) == 1
        assert result.errors[0].url == "https://example.com/b.html"
        assert result.errors[0].error == "timeout"

    def test_order_preserved(self):
        links = [
            TargetLink(url="https://example.com/c.html", order=0),
            TargetLink(url="https://example.com/a.html", order=1),
            TargetLink(url="https://example.com/b.html", order=2),
        ]
        title_results = [
            TitleExtractionResult(url="https://example.com/c.html", title="C", status=ExtractionStatus.SUCCESS),
            TitleExtractionResult(url="https://example.com/a.html", title="A", status=ExtractionStatus.SUCCESS),
            TitleExtractionResult(url="https://example.com/b.html", title="B", status=ExtractionStatus.SUCCESS),
        ]
        result = self.builder.build(links, title_results, 0)

        assert result.results[0].url == "https://example.com/c.html"
        assert result.results[1].url == "https://example.com/a.html"
        assert result.results[2].url == "https://example.com/b.html"

    def test_empty_links(self):
        result = self.builder.build([], [], 0)
        assert result.statistics.total == 0
        assert len(result.results) == 0