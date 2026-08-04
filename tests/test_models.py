import pytest

from url_link_extractor.models import (
    ExtractionStatus,
    ExtractConfig,
    ExtractRequest,
    TargetLink,
    TitleExtractionResult,
    LinkTitlePair,
    ExtractStatistics,
    ErrorReport,
    ExtractResult,
    ProgressInfo,
)


class TestExtractionStatus:
    def test_values(self):
        assert ExtractionStatus.SUCCESS.value == "success"
        assert ExtractionStatus.FAILED.value == "failed"
        assert ExtractionStatus.SKIPPED.value == "skipped"


class TestExtractConfig:
    def test_defaults(self):
        config = ExtractConfig()
        assert config.concurrency == 5
        assert config.timeout == 30000
        assert config.interval == 500
        assert config.retry_count == 2
        assert config.follow_robots_txt is False
        assert config.max_links == 1000
        assert config.output_excel is True
        assert config.output_path == "result.xlsx"

    def test_invalid_concurrency(self):
        with pytest.raises(ValueError):
            ExtractConfig(concurrency=0)
        with pytest.raises(ValueError):
            ExtractConfig(concurrency=21)

    def test_invalid_timeout(self):
        with pytest.raises(ValueError):
            ExtractConfig(timeout=999)
        with pytest.raises(ValueError):
            ExtractConfig(timeout=60001)

    def test_invalid_max_links(self):
        with pytest.raises(ValueError):
            ExtractConfig(max_links=0)
        with pytest.raises(ValueError):
            ExtractConfig(max_links=10001)


class TestFrozenDataclasses:
    def test_link_title_pair_frozen(self):
        pair = LinkTitlePair(url="https://example.com", title="Test", status=ExtractionStatus.SUCCESS)
        with pytest.raises(AttributeError):
            pair.url = "changed"

    def test_extract_statistics_frozen(self):
        stats = ExtractStatistics(total=10, success=8, failed=1, skipped=1, duration=5000)
        with pytest.raises(AttributeError):
            stats.total = 100

    def test_error_report_frozen(self):
        report = ErrorReport(url="https://example.com", error="timeout")
        with pytest.raises(AttributeError):
            report.url = "changed"

    def test_extract_result_frozen(self):
        result = ExtractResult(results=[], statistics=ExtractStatistics(0, 0, 0, 0, 0), errors=[])
        with pytest.raises(AttributeError):
            result.results = ["changed"]


class TestExtractRequest:
    def test_creation(self):
        req = ExtractRequest(url="https://example.com", prefix="https://example.com/")
        assert req.url == "https://example.com"
        assert req.suffix is None
        assert req.config is None

    def test_with_config(self):
        config = ExtractConfig(concurrency=10)
        req = ExtractRequest(url="https://example.com", prefix="https://example.com/", config=config)
        assert req.config.concurrency == 10


class TestProgressInfo:
    def test_creation(self):
        info = ProgressInfo(completed=5, total=10, last_url="https://example.com", last_status=ExtractionStatus.SUCCESS)
        assert info.completed == 5
        assert info.total == 10