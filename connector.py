"""
대도서관(Library) — LLM 연결 추상 계약 및 구현체

시스템 중립. Atom/Athena에 의존하지 않음.
OpenAI, Claude, Gemini, 자체 모델, RAG only, Stub 를 바꿔 끼우기 쉽게 계약만 준수.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class LibraryConnectorBase(ABC):
    """대도서관(LLM) 쿼리 추상 인터페이스. 구현체는 API 호출."""

    @abstractmethod
    def query(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        """시스템 프롬프트 + 사용자 프롬프트로 대도서관에 질의, 응답 텍스트 반환."""
        pass

    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> tuple[str, float]:
        """선택: (응답 텍스트, 신뢰도 [0,1]) 반환. 기본 구현은 query() + 0.5."""
        text = self.query(system_prompt, user_prompt, **kwargs)
        return (text, 0.5)


class LibraryConnectorStub(LibraryConnectorBase):
    """API 없이 동작하는 스텁. 실제 LLM 호출이 없을 때 사용."""

    def __init__(
        self,
        default_response: str = "[대도서관 미연결] API 키 없음. OPENAI_API_KEY 또는 connector 주입 후 사용.",
        confidence: float = 0.0,
    ):
        self.default_response = default_response
        self.confidence = confidence

    def query(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        return self.default_response

    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> tuple[str, float]:
        return (self.query(system_prompt, user_prompt, **kwargs), self.confidence)


def _try_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    **kwargs: Any,
) -> Optional[tuple[str, float]]:
    """OpenAI 호환 API 호출. 성공 시 (텍스트, 0.7), 실패 시 None."""
    try:
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=kwargs.get("model", model),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=kwargs.get("temperature", 0.5),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        if resp.choices and resp.choices[0].message.content:
            text = resp.choices[0].message.content.strip()
            return (text, 0.7)
    except Exception:
        pass
    return None


class LibraryConnectorOpenAI(LibraryConnectorBase):
    """OpenAI API 호환 대도서관 connector. openai 패키지 필요."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.5,
        max_tokens: int = 1024,
        success_confidence: float = 0.7,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.success_confidence = success_confidence

    def query(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
        out = _try_openai(
            system_prompt,
            user_prompt,
            model=kwargs.get("model", self.model),
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        if out is not None:
            return out[0]
        return "[대도서관 응답 없음]"

    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> tuple[str, float]:
        out = _try_openai(
            system_prompt,
            user_prompt,
            model=kwargs.get("model", self.model),
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        if out is not None:
            return (out[0], self.success_confidence)
        return ("[대도서관 응답 없음]", 0.0)


def get_connector(connector: Optional[LibraryConnectorBase] = None) -> LibraryConnectorBase:
    """connector가 없으면 OPENAI_API_KEY 있으면 OpenAI, 없으면 Stub 반환."""
    if connector is not None:
        return connector
    import os
    if os.environ.get("OPENAI_API_KEY"):
        return LibraryConnectorOpenAI()
    return LibraryConnectorStub()
