"""Library 엔진 테스트 — test_library.py

테스트 섹션:
  § 1. connector.py — Base, Stub, OpenAI 계약 검증
  § 2. visit.py — visit(context) 계약 검증
  § 3. get_connector — 자동 선택 로직
  § 4. 통합 — __init__ export
"""
from __future__ import annotations

import sys
import os

# Library가 sys.path에 있도록 00_BRAIN 추가
_brain = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _brain not in sys.path:
    sys.path.insert(0, _brain)

import pytest
from Library.connector import (
    LibraryConnectorBase,
    LibraryConnectorStub,
    LibraryConnectorOpenAI,
    get_connector,
)
from Library.visit import visit


# ═══════════════════════════════════════════════════════════════════
# § 1. connector.py
# ═══════════════════════════════════════════════════════════════════

class TestConnectorBase:
    def test_stub_is_concrete(self):
        """Stub은 추상 메서드 구현 확인."""
        s = LibraryConnectorStub()
        assert isinstance(s, LibraryConnectorBase)

    def test_stub_query_returns_str(self):
        s = LibraryConnectorStub()
        result = s.query("sys", "user")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_stub_query_with_confidence_returns_tuple(self):
        s = LibraryConnectorStub()
        result = s.query_with_confidence("sys", "user")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_stub_confidence_type(self):
        s = LibraryConnectorStub()
        _, conf = s.query_with_confidence("sys", "user")
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

    def test_stub_default_confidence_is_zero(self):
        s = LibraryConnectorStub()
        _, conf = s.query_with_confidence("sys", "user")
        assert conf == 0.0

    def test_stub_custom_confidence(self):
        s = LibraryConnectorStub(confidence=0.3)
        _, conf = s.query_with_confidence("sys", "user")
        assert conf == 0.3

    def test_stub_custom_response(self):
        s = LibraryConnectorStub(default_response="테스트 응답")
        assert s.query("sys", "user") == "테스트 응답"

    def test_base_query_with_confidence_default(self):
        """Base의 기본 query_with_confidence는 (query(), 0.5) 반환."""
        class ConcreteConnector(LibraryConnectorBase):
            def query(self, system_prompt, user_prompt, **kwargs):
                return "응답"
        c = ConcreteConnector()
        text, conf = c.query_with_confidence("sys", "user")
        assert text == "응답"
        assert conf == 0.5


# ═══════════════════════════════════════════════════════════════════
# § 2. visit.py
# ═══════════════════════════════════════════════════════════════════

class TestVisitFunction:
    def test_returns_dict(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert "insight" in r
        assert "digest" in r
        assert "confidence" in r

    def test_insight_is_str(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert isinstance(r["insight"], str)

    def test_digest_is_str(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert isinstance(r["digest"], str)

    def test_confidence_range(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert 0.0 <= r["confidence"] <= 1.0

    def test_stub_confidence_is_zero(self):
        r = visit({}, connector=LibraryConnectorStub())
        assert r["confidence"] == 0.0

    def test_perception_included(self):
        """perception 있으면 insight에 뭔가 생성됨."""
        r = visit(
            {"perception": {"food_security": 0.6}},
            connector=LibraryConnectorStub(default_response="식량 안보 중간"),
        )
        assert len(r["insight"]) > 0

    def test_full_context(self):
        ctx = {
            "perception":       {"maat_score": 0.72},
            "goal":             {"target": "stable"},
            "memory_summary":   "최근 3회 grain_release.",
            "observer_verdict": "STABLE",
            "extra":            {"note": "테스트"},
        }
        r = visit(ctx, connector=LibraryConnectorStub(default_response="full ctx 응답"))
        assert r["insight"] == "full ctx 응답"

    def test_max_insight_chars(self):
        """max_insight_chars 제한 적용."""
        long_resp = "A" * 3000
        r = visit(
            {},
            connector=LibraryConnectorStub(default_response=long_resp),
            max_insight_chars=100,
        )
        assert len(r["insight"]) <= 100

    def test_digest_is_first_line(self):
        """digest는 insight 첫 줄."""
        resp = "첫 줄 요약입니다.\n두 번째 줄."
        r = visit({}, connector=LibraryConnectorStub(default_response=resp))
        assert r["digest"] == "첫 줄 요약입니다."

    def test_custom_connector_confidence(self):
        """query_with_confidence 있는 connector → confidence 반영."""
        class CustomConn(LibraryConnectorBase):
            def query(self, sys_p, usr_p, **kw): return "응답"
            def query_with_confidence(self, sys_p, usr_p, **kw): return ("응답", 0.85)

        r = visit({}, connector=CustomConn())
        assert r["confidence"] == 0.85

    def test_error_connector_returns_zero_confidence(self):
        """오류 발생 시 confidence=0.0."""
        class BrokenConn(LibraryConnectorBase):
            def query(self, *a, **kw): raise RuntimeError("broken")
        r = visit({}, connector=BrokenConn())
        assert r["confidence"] == 0.0


# ═══════════════════════════════════════════════════════════════════
# § 3. get_connector
# ═══════════════════════════════════════════════════════════════════

class TestGetConnector:
    def test_returns_base_instance(self):
        conn = get_connector()
        assert isinstance(conn, LibraryConnectorBase)

    def test_passthrough_connector(self):
        stub = LibraryConnectorStub(default_response="직접 주입")
        conn = get_connector(stub)
        assert conn is stub

    def test_stub_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        conn = get_connector()
        assert isinstance(conn, LibraryConnectorStub)


# ═══════════════════════════════════════════════════════════════════
# § 4. 통합 — __init__ export
# ═══════════════════════════════════════════════════════════════════

class TestLibraryInit:
    def test_visit_importable(self):
        from Library import visit
        assert callable(visit)

    def test_get_connector_importable(self):
        from Library import get_connector
        assert callable(get_connector)

    def test_connector_base_importable(self):
        from Library import LibraryConnectorBase
        assert LibraryConnectorBase is not None

    def test_connector_stub_importable(self):
        from Library import LibraryConnectorStub
        assert LibraryConnectorStub is not None

    def test_system_prompt_importable(self):
        from Library import SYSTEM_PROMPT
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0
