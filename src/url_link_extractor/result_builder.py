from __future__ import annotations

from typing import List

from .models import (
    ErrorReport,
    ExtractResult,
    ExtractStatistics,
    ExtractionStatus,
    LinkTitlePair,
    TargetLink,
    TitleExtractionResult,
)


class ResultBuilder:
    def build(
        self,
        links: List[TargetLink],
        title_results: List[TitleExtractionResult],
        start_time: float,
    ) -> ExtractResult:
        import time

        duration_ms = int((time.monotonic() - start_time) * 1000)

        result_map: dict[str, TitleExtractionResult] = {r.url: r for r in title_results}

        pairs: List[LinkTitlePair] = []
        for link in links:
            tr = result_map.get(link.url)
            if tr is None:
                pairs.append(LinkTitlePair(
                    url=link.url, title="", status=ExtractionStatus.FAILED, error="No result"
                ))
            else:
                pairs.append(LinkTitlePair(
                    url=tr.url, title=tr.title, status=tr.status, error=tr.error
                ))

        success = sum(1 for p in pairs if p.status == ExtractionStatus.SUCCESS)
        failed = sum(1 for p in pairs if p.status == ExtractionStatus.FAILED)
        skipped = sum(1 for p in pairs if p.status == ExtractionStatus.SKIPPED)

        statistics = ExtractStatistics(
            total=len(pairs), success=success, failed=failed, skipped=skipped, duration=duration_ms
        )

        errors = [ErrorReport(url=p.url, error=p.error) for p in pairs if p.status == ExtractionStatus.FAILED]

        return ExtractResult(results=pairs, statistics=statistics, errors=errors)