from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .exceptions import (
    InvalidConfigError,
    InvalidPrefixError,
    InvalidUrlError,
)
from .models import ExtractRequest
from .url_resolver import UrlResolver


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]


class InputValidator:
    def validate(self, request: ExtractRequest) -> ValidationResult:
        errors: List[str] = []

        try:
            self._validate_url(request.url)
        except InvalidUrlError as exc:
            errors.append(str(exc))

        try:
            self._validate_prefix(request.prefix)
        except InvalidPrefixError as exc:
            errors.append(str(exc))

        if request.suffix is not None:
            self._validate_suffix(request.suffix, errors)

        if request.config is not None:
            try:
                self._validate_config(request.config)
            except InvalidConfigError as exc:
                errors.append(str(exc))

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    @staticmethod
    def _validate_url(url: str) -> None:
        if not url:
            raise InvalidUrlError("URL is required")
        if len(url) > 2048:
            raise InvalidUrlError(f"URL exceeds 2048 characters: {len(url)}")
        if not UrlResolver.is_valid_url(url):
            raise InvalidUrlError(f"Invalid URL: {url}")

    @staticmethod
    def _validate_prefix(prefix: str) -> None:
        if not prefix:
            raise InvalidPrefixError("Prefix is required")
        if len(prefix) > 2048:
            raise InvalidPrefixError(f"Prefix exceeds 2048 characters: {len(prefix)}")
        if not prefix.startswith("http://") and not prefix.startswith("https://"):
            raise InvalidPrefixError(f"Prefix must start with http:// or https://: {prefix}")

    @staticmethod
    def _validate_suffix(suffix: str, errors: List[str]) -> None:
        if len(suffix) > 50:
            errors.append(f"Suffix exceeds 50 characters: {len(suffix)}")

    @staticmethod
    def _validate_config(config: object) -> None:
        if not (1 <= config.concurrency <= 20):
            raise InvalidConfigError(f"concurrency must be in [1, 20], got {config.concurrency}")
        if not (1000 <= config.timeout <= 60000):
            raise InvalidConfigError(f"timeout must be in [1000, 60000], got {config.timeout}")
        if not (0 <= config.interval <= 10000):
            raise InvalidConfigError(f"interval must be in [0, 10000], got {config.interval}")
        if not (0 <= config.retry_count <= 5):
            raise InvalidConfigError(f"retry_count must be in [0, 5], got {config.retry_count}")
        if not (1 <= config.max_links <= 10000):
            raise InvalidConfigError(f"max_links must be in [1, 10000], got {config.max_links}")