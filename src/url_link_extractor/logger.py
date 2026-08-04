from __future__ import annotations

import logging
from typing import Optional


class Logger:
    _instances: dict[str, Logger] = {}

    def __init__(self, name: str = "url_link_extractor", level: int = logging.INFO) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, operation: str, url: str = "", duration_ms: int = 0, status_code: int = 0, **kwargs: object) -> None:
        msg = self._format(operation, url, duration_ms, status_code, kwargs)
        self._logger.info(msg)

    def warning(self, operation: str, url: str = "", duration_ms: int = 0, status_code: int = 0, **kwargs: object) -> None:
        msg = self._format(operation, url, duration_ms, status_code, kwargs)
        self._logger.warning(msg)

    def error(self, operation: str, url: str = "", duration_ms: int = 0, status_code: int = 0, **kwargs: object) -> None:
        msg = self._format(operation, url, duration_ms, status_code, kwargs)
        self._logger.error(msg)

    def debug(self, operation: str, url: str = "", duration_ms: int = 0, status_code: int = 0, **kwargs: object) -> None:
        msg = self._format(operation, url, duration_ms, status_code, kwargs)
        self._logger.debug(msg)

    @staticmethod
    def _format(operation: str, url: str, duration_ms: int, status_code: int, kwargs: dict) -> str:
        parts = [f"op={operation}"]
        if url:
            parts.append(f"url={url}")
        if duration_ms:
            parts.append(f"duration={duration_ms}ms")
        if status_code:
            parts.append(f"status={status_code}")
        for k, v in kwargs.items():
            parts.append(f"{k}={v}")
        return " | ".join(parts)


def get_logger(name: str = "url_link_extractor", level: int = logging.INFO) -> Logger:
    if name not in Logger._instances:
        Logger._instances[name] = Logger(name, level)
    return Logger._instances[name]