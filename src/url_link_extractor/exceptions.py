from __future__ import annotations


class UrlExtractorError(Exception):
    error_code: str = "URL_EXTRACTOR_ERROR"

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


class InvalidUrlError(UrlExtractorError):
    error_code = "INVALID_URL"


class InvalidPrefixError(UrlExtractorError):
    error_code = "INVALID_PREFIX"


class InvalidConfigError(UrlExtractorError):
    error_code = "INVALID_CONFIG"


class EntryUrlUnreachableError(UrlExtractorError):
    error_code = "ENTRY_URL_UNREACHABLE"


class EntryPageNotHtmlError(UrlExtractorError):
    error_code = "ENTRY_PAGE_NOT_HTML"


class LinkLimitExceededError(UrlExtractorError):
    error_code = "LINK_LIMIT_EXCEEDED"


class ExcelExportError(UrlExtractorError):
    error_code = "EXCEL_EXPORT_ERROR"