import pytest

from url_link_extractor.input_validator import InputValidator, ValidationResult
from url_link_extractor.models import ExtractConfig, ExtractRequest


class TestInputValidator:
    def setup_method(self):
        self.validator = InputValidator()

    def test_valid_request(self):
        req = ExtractRequest(url="https://support.huaweicloud.com/usermanual-cli/", prefix="https://support.huaweicloud.com/")
        result = self.validator.validate(req)
        assert result.valid is True
        assert result.errors == []

    def test_invalid_url(self):
        req = ExtractRequest(url="abc", prefix="https://support.huaweicloud.com/")
        result = self.validator.validate(req)
        assert result.valid is False
        assert any("Invalid URL" in e for e in result.errors)

    def test_empty_url(self):
        req = ExtractRequest(url="", prefix="https://support.huaweicloud.com/")
        result = self.validator.validate(req)
        assert result.valid is False

    def test_url_too_long(self):
        req = ExtractRequest(url="https://example.com/" + "a" * 2048, prefix="https://example.com/")
        result = self.validator.validate(req)
        assert result.valid is False

    def test_invalid_prefix(self):
        req = ExtractRequest(url="https://example.com", prefix="ftp://example.com/")
        result = self.validator.validate(req)
        assert result.valid is False
        assert any("Prefix" in e for e in result.errors)

    def test_empty_prefix(self):
        req = ExtractRequest(url="https://example.com", prefix="")
        result = self.validator.validate(req)
        assert result.valid is False

    def test_suffix_too_long(self):
        req = ExtractRequest(url="https://example.com", prefix="https://example.com/", suffix="x" * 51)
        result = self.validator.validate(req)
        assert result.valid is False

    def test_invalid_config_concurrency(self):
        with pytest.raises(ValueError):
            ExtractConfig(concurrency=0)

    def test_valid_with_suffix_and_config(self):
        config = ExtractConfig(concurrency=10, timeout=5000)
        req = ExtractRequest(
            url="https://support.huaweicloud.com/usermanual-cli/",
            prefix="https://support.huaweicloud.com/",
            suffix=".html",
            config=config,
        )
        result = self.validator.validate(req)
        assert result.valid is True