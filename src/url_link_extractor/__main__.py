from __future__ import annotations

import argparse
import sys
from typing import Optional

from .extractor import extract
from .models import ExtractConfig, ExtractRequest


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Extract URLs and page titles from an entry page")
    parser.add_argument("url", help="Entry URL to extract links from")
    parser.add_argument("--prefix", required=True, help="URL prefix to filter links")
    parser.add_argument("--suffix", default=None, help="URL suffix to filter links (e.g. .html)")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent request count (1-20)")
    parser.add_argument("--timeout", type=int, default=30000, help="Request timeout in ms (1000-60000)")
    parser.add_argument("--interval", type=int, default=500, help="Request interval in ms (0-10000)")
    parser.add_argument("--retry", type=int, default=2, help="Max retry count (0-5)")
    parser.add_argument("--max-links", type=int, default=1000, help="Max target links (1-10000)")
    parser.add_argument("--no-excel", action="store_true", help="Disable Excel output")
    parser.add_argument("--output", default="result.xlsx", help="Output Excel file path")

    args = parser.parse_args(argv)

    config = ExtractConfig(
        concurrency=args.concurrency,
        timeout=args.timeout,
        interval=args.interval,
        retry_count=args.retry,
        max_links=args.max_links,
        output_excel=not args.no_excel,
        output_path=args.output,
    )

    request = ExtractRequest(
        url=args.url,
        prefix=args.prefix,
        suffix=args.suffix,
        config=config,
    )

    def on_progress(progress):
        percent = (progress.completed / progress.total * 100) if progress.total > 0 else 0
        print(f"[{percent:.1f}%] {progress.completed}/{progress.total} - {progress.last_url} [{progress.last_status.value}]")

    result = extract(request, on_progress)
    print(f"\n统计: total={result.statistics.total}, success={result.statistics.success}, "
          f"failed={result.statistics.failed}, skipped={result.statistics.skipped}, "
          f"duration={result.statistics.duration}ms")

    for item in result.results:
        print(f"  {item.url} -> {item.title} [{item.status.value}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())