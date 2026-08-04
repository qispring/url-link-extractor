from __future__ import annotations

from typing import Optional

import chardet


class EncodingDetector:
    _cjk_encodings = frozenset({
        "utf-8", "gb2312", "gbk", "gb18030", "big5",
        "euc-jp", "shift-jis", "shift_jis", "cp932",
        "euc-kr", "cp949", "iso-2022-jp", "iso-2022-kr",
    })

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
                decoded = raw.decode(detected)
                if detected.lower() not in self._cjk_encodings:
                    alt = self._try_cjk_alternatives(raw, decoded)
                    if alt is not None:
                        return alt
                return decoded
            except (UnicodeDecodeError, LookupError):
                pass

        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("utf-8", errors="replace")

    @staticmethod
    def _try_cjk_alternatives(raw: bytes, current: str) -> Optional[str]:
        current_cjk = sum(1 for c in current if "\u4e00" <= c <= "\u9fff")
        for enc in ("gb18030", "gbk", "big5"):
            try:
                decoded = raw.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
            cjk_count = sum(1 for c in decoded if "\u4e00" <= c <= "\u9fff")
            if cjk_count > current_cjk:
                return decoded
        return None

    @staticmethod
    def _extract_encoding(content_type: str) -> Optional[str]:
        if not content_type:
            return None
        for part in content_type.split(";"):
            part = part.strip()
            if part.lower().startswith("charset="):
                return part.split("=", 1)[1].strip().strip('"').strip("'")
        return None