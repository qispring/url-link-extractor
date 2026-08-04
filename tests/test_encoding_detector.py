import pytest

from url_link_extractor.encoding_detector import EncodingDetector


class TestEncodingDetector:
    def setup_method(self):
        self.detector = EncodingDetector()

    def test_utf8_from_content_type(self):
        raw = "什么是码道CLI".encode("utf-8")
        result = self.detector.detect_and_decode(raw, "text/html; charset=utf-8")
        assert result == "什么是码道CLI"

    def test_gbk_from_content_type(self):
        raw = "什么是码道CLI".encode("gbk")
        result = self.detector.detect_and_decode(raw, "text/html; charset=gbk")
        assert result == "什么是码道CLI"

    def test_gb2312_from_content_type(self):
        raw = "测试标题".encode("gb2312")
        result = self.detector.detect_and_decode(raw, "text/html; charset=gb2312")
        assert result == "测试标题"

    def test_auto_detect_utf8(self):
        raw = "什么是码道CLI".encode("utf-8")
        result = self.detector.detect_and_decode(raw, "")
        assert result == "什么是码道CLI"

    def test_auto_detect_gbk(self):
        raw = "什么是码道CLI".encode("gbk")
        result = self.detector.detect_and_decode(raw, "")
        assert result == "什么是码道CLI"

    def test_fallback_utf8(self):
        raw = b"\xff\xfe\x00\x01"
        result = self.detector.detect_and_decode(raw, "")
        assert isinstance(result, str)

    def test_empty_content(self):
        result = self.detector.detect_and_decode(b"", "")
        assert result == ""

    def test_no_content_type(self):
        raw = "Hello World".encode("utf-8")
        result = self.detector.detect_and_decode(raw)
        assert result == "Hello World"