from __future__ import annotations

from typing import Optional

import chardet


class EncodingDetector:
    def detect_and_decode(self, raw: bytes, content_type: str = "") -> str:
        encoding = self._extract_encoding(content_type)
        if encoding:
            try:
                return raw.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                pass

        result = chardet.detect(raw)
        detected = result.get("encoding")
        if detected:
            try:
                return raw.decode(detected)
            except (UnicodeDecodeError, LookupError):
                pass

        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("utf-8", errors="replace")

    @staticmethod
    def _extract_encoding(content_type: str) -> Optional[str]:
        if not content_type:
            return None
        for part in content_type.split(";"):
            part = part.strip()
            if part.lower().startswith("charset="):
                return part.split("=", 1)[1].strip().strip('"').strip("'")
        return None