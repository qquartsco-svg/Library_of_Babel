"""
대도서관(Library) 방문 — visit(context) -> insight, digest, confidence

시스템 중립. context dict만 받아 결과 dict 반환.
Atom/Athena는 이 함수를 호출하는 클라이언트.
"""

from __future__ import annotations
from typing import Any, Optional

from .connector import LibraryConnectorBase, get_connector

SYSTEM_PROMPT = """당신은 방대한 정보를 가진 대도서관입니다.
요청자(개인 에이전트)가 현재 상황·목표·기억 요약을 주면, 고급 정보와 추론을 짧고 명확하게 제시하세요.
에이전트는 이 답변을 개인 기억에 정리해 저장합니다. 핵심만 2~5문장으로."""


def _summarize(obj: Any, max_len: int = 400) -> str:
    """context 요소를 프롬프트용 문자열로."""
    if obj is None:
        return "(없음)"
    if isinstance(obj, dict):
        parts = []
        for k, v in list(obj.items())[:15]:
            vstr = str(v)
            if len(vstr) > 80:
                vstr = vstr[:77] + "..."
            parts.append(f"{k}: {vstr}")
        s = "; ".join(parts)
    else:
        s = str(obj)
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return s


def visit(
    context: dict,
    *,
    connector: Optional[LibraryConnectorBase] = None,
    system_prompt: Optional[str] = None,
    max_insight_chars: int = 2000,
) -> dict:
    """
    대도서관 방문. context를 프롬프트로 만들어 LLM에 질의 후 insight, digest, confidence 반환.

    context: {
        "perception": ...,      # 현재 관측 요약
        "goal": ...,            # 목표 요약
        "memory_summary": ...,  # 기억 요약
        "observer_verdict": ..., # (선택) 옵저버 판정
        "extra": ...,           # 기타
    }
    return: {
        "insight": str,    # 본문 (지식·추론·지혜)
        "digest": str,     # 한 줄 요약 (개인 저장용)
        "confidence": float, # [0,1] 신뢰도. 판단·저장 시 참고.
    }
    """
    parts = [
        "[현재 관측(perception)]",
        _summarize(context.get("perception"), 400),
        "[목표(goal)]",
        _summarize(context.get("goal"), 200),
        "[기억 요약(memory_summary)]",
        _summarize(context.get("memory_summary"), 300),
    ]
    if context.get("observer_verdict") is not None:
        parts.append("[옵저버 판정(observer_verdict)]")
        parts.append(_summarize(context.get("observer_verdict"), 200))
    if context.get("extra") is not None:
        parts.append("[기타(extra)]")
        parts.append(_summarize(context.get("extra"), 200))
    user_prompt = "\n".join(parts)

    conn = get_connector(connector)
    sys_prompt = system_prompt if system_prompt is not None else SYSTEM_PROMPT

    try:
        if hasattr(conn, "query_with_confidence"):
            insight, confidence = conn.query_with_confidence(sys_prompt, user_prompt)
        else:
            insight = conn.query(sys_prompt, user_prompt)
            confidence = 0.5
    except Exception as e:
        insight = f"[대도서관 오류] {e!s}"
        confidence = 0.0

    if len(insight) > max_insight_chars:
        insight = insight[: max_insight_chars - 3] + "..."

    digest = insight.strip().split("\n")[0][:300].strip() if insight.strip() else ""

    return {
        "insight": insight,
        "digest": digest,
        "confidence": max(0.0, min(1.0, float(confidence))),
    }
