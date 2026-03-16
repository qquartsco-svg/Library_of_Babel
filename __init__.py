"""
대도서관(Library) — 독립 엔진 패키지

외부 고급 정보·추론 서비스. Atom·Athena 등이 방문해 insight/digest/confidence를 받아
각자 개인 저장소에 축적하고 판단 품질을 높이는 클라이언트 구조.

사용:
  from Library import visit, get_connector, LibraryConnectorBase
  result = visit(context, connector=get_connector())
  # result["insight"], result["digest"], result["confidence"]
"""

from __future__ import annotations

from .connector import (
    LibraryConnectorBase,
    LibraryConnectorStub,
    LibraryConnectorOpenAI,
    get_connector,
)
from .visit import visit, SYSTEM_PROMPT

__all__ = [
    "visit",
    "SYSTEM_PROMPT",
    "LibraryConnectorBase",
    "LibraryConnectorStub",
    "LibraryConnectorOpenAI",
    "get_connector",
]
