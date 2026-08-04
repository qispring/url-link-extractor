from __future__ import annotations

import asyncio
import time
from typing import Optional, Tuple

import httpx

from .exceptions import UrlExtractorError
from .logger import get_logger

logger = get_logger("url_link_extractor.http")

_USER_AGENT = "url-link-extractor/1.0 (+https://github.com/qispring/url-link-extractor)"


class HttpClient:
    def __init__(
        self,
        timeout: int = 30000,
        retry_count: int = 2,
        interval: int = 500,
    ) -> None:
        self._timeout = timeout / 1000.0
        self._retry_count = retry_count
        self._interval = interval / 1000.0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=True,
                max_redirects=5,
                headers={"User-Agent": _USER_AGENT},
            )
        return self._client

    async def get(self, url: str) -> Tuple[int, bytes, str]:
        if not url.startswith("https://"):
            raise UrlExtractorError(f"Only HTTPS is allowed, got: {url}")

        client = await self._get_client()
        last_error: Optional[Exception] = None
        retry_attempt = 0

        while True:
            start = time.monotonic()
            try:
                resp = await client.get(url)
                duration_ms = int((time.monotonic() - start) * 1000)
                logger.info("http_get", url=url, duration_ms=duration_ms, status_code=resp.status_code)

                if 400 <= resp.status_code < 500:
                    return resp.status_code, resp.content, str(resp.headers.get("content-type", ""))

                if resp.status_code >= 500 and retry_attempt < self._retry_count:
                    wait = 1.0 * (2 ** retry_attempt)
                    logger.warning("http_retry", url=url, status_code=resp.status_code, retry=retry_attempt + 1, wait=f"{wait}s")
                    await asyncio.sleep(wait)
                    retry_attempt += 1
                    continue

                return resp.status_code, resp.content, str(resp.headers.get("content-type", ""))

            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as exc:
                last_error = exc
                duration_ms = int((time.monotonic() - start) * 1000)
                if retry_attempt < self._retry_count:
                    wait = 1.0 * (2 ** retry_attempt)
                    logger.warning("http_retry", url=url, duration_ms=duration_ms, retry=retry_attempt + 1, wait=f"{wait}s", error=str(exc))
                    await asyncio.sleep(wait)
                    retry_attempt += 1
                    continue
                logger.error("http_failed", url=url, duration_ms=duration_ms, error=str(exc))
                raise UrlExtractorError(f"Request failed for {url}: {exc}") from exc

            finally:
                if self._interval > 0:
                    await asyncio.sleep(self._interval)

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()