from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ExtractionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExtractConfig:
    concurrency: int = 5
    timeout: int = 30000
    interval: int = 500
    retry_count: int = 2
    follow_robots_txt: bool = False
    max_links: int = 1000
    output_excel: bool = True
    output_path: str = "result.xlsx"

    def __post_init__(self) -> None:
        if not (1 <= self.concurrency <= 20):
            raise ValueError(f"concurrency must be in [1, 20], got {self.concurrency}")
        if not (1000 <= self.timeout <= 60000):
            raise ValueError(f"timeout must be in [1000, 60000], got {self.timeout}")
        if not (0 <= self.interval <= 10000):
            raise ValueError(f"interval must be in [0, 10000], got {self.interval}")
        if not (0 <= self.retry_count <= 5):
            raise ValueError(f"retry_count must be in [0, 5], got {self.retry_count}")
        if not (1 <= self.max_links <= 10000):
            raise ValueError(f"max_links must be in [1, 10000], got {self.max_links}")


@dataclass
class ExtractRequest:
    url: str
    prefix: str
    suffix: Optional[str] = None
    config: Optional[ExtractConfig] = None


@dataclass
class TargetLink:
    url: str
    order: int


@dataclass
class TitleExtractionResult:
    url: str
    title: str
    status: ExtractionStatus
    error: str = ""


@dataclass(frozen=True)
class LinkTitlePair:
    url: str
    title: str
    status: ExtractionStatus
    error: str = ""


@dataclass(frozen=True)
class ExtractStatistics:
    total: int
    success: int
    failed: int
    skipped: int
    duration: int


@dataclass(frozen=True)
class ErrorReport:
    url: str
    error: str


@dataclass(frozen=True)
class ExtractResult:
    results: List[LinkTitlePair]
    statistics: ExtractStatistics
    errors: List[ErrorReport]


@dataclass
class ProgressInfo:
    completed: int
    total: int
    last_url: str
    last_status: ExtractionStatus