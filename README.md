# Library of Babel — 바벨 도서관

**외부 지혜의 성소.** Atom·Athena 등 지능체가 필요할 때 **방문**해 고급 정보·추론·지혜를 구하고, 이를 **자기 저장소에 내재화**해 판단 품질을 높이는 **표준화된 지식 수급 인프라**이다.

- **한 줄 정의**: 대도서관은 “항상 붙어 있는 뇌”가 아니라, **필요할 때만 방문하는 외부 고급 지식·추론 공간**이다.
- **역할**: 정보 연결(검색, RAG) + **LLM 대화 연결**(OpenAI, Claude, Gemini, 자체 모델, Stub) — 계약만 맞으면 **바꿔 끼우기** 가능.

---

## 개념

### 바벨 도서관 메타포

보르헤스의 **바벨의 도서관**처럼, 여기서 “도서관”은 **방대한 기호·지식이 있는 공간**이지만, 지능체가 **항상 그 안에 있는 것이 아니라** 필요할 때만 찾아와 질문하고, 얻은 답(insight·digest)을 **자기 것으로 만들어 가는** 구조다.

- **평상시**: Atom/Athena는 **일상 복귀·판단형 AI**로 동작.
- **필요 시**: 대도서관 **방문** → 정보 연결 + LLM 대화 연결 → **고급 정보·고급 추론** 획득.
- **복귀 후**: 개인 저장소에 반영 → **같은 판단 로직**이 더 풍부한 참조 저장소를 쓰게 되어 **판단 품질**이 올라감. (엔진 자체가 학습되는 것이 아니라, **참조하는 저장소가 풍부해지는** 구조.)

### LLM과 도서관의 연결

| 연결 유형 | 설명 |
|-----------|------|
| **정보 연결** | 검색, RAG, 외부 지식 소스. “무엇이 있는지” 접근. |
| **LLM 대화 연결** | 개인/상용 LLM·API와의 **대화**를 통한 추론·조언·재구성. “무엇을 할지”에 대한 지혜. |

둘을 함께 **바벨 도서관** 하나의 엔진으로 두고, **visit(context)** 한 번으로 결과(insight, digest, confidence)를 받는다.

---

## 수식·계약

### 입출력 계약

**입력** `context` (dict):

```
context = {
    "perception": ...,      # 현재 관측 요약 (지각)
    "goal": ...,            # 목표 요약
    "memory_summary": ...,  # 기억 요약
    "observer_verdict": ..., # (선택) 옵저버 판정
    "extra": ...,           # 기타
}
```

**출력** (dict):

```
result = {
    "insight": str,     # 본문 (지식·추론·지혜). 임시 저장·깊은 이해용.
    "digest": str,      # 한 줄 요약. 개인 저장(장기 후보)용.
    "confidence": float # [0,1] 응답 신뢰도. connector 제공 또는 휴리스틱. 판단·저장 시 가중치.
}
```

### 방문 함수

```
visit(context; connector?) → { insight, digest, confidence }
```

- `connector`가 없으면: `OPENAI_API_KEY` 있으면 OpenAI, 없으면 Stub.
- connector는 `LibraryConnectorBase` 계약: `query(system_prompt, user_prompt) -> str` 또는 `query_with_confidence(...) -> (text, confidence)`.

### 검증 원칙

insight를 **무조건 믿지 않고**, 필요 시 검증·요약 후 개인 저장(특히 **장기 저장**)에 반영하는 것을 권장. 설계상 **임시 저장(원문)** 과 **장기 저장 후보(digest/검증 통과 요약)** 두 층을 둔다.

---

## 활용성

- **Atom**: 개인형 인지 스택. state에서 context를 만들고 `visit(context)` 호출 → `library_insight`, `library_digest_for_memory`, `library_confidence` 등에 반영 → L3 판단 시 참조.
- **Athena**: 거시·군주형. 동일 `visit(context)` 호출 후 **정책 지식·거버넌스 참고·전략 지식** 저장 및 판단 체계에 반영.
- **기타 AI 객체**: context dict만 구성할 수 있으면 어떤 스택이든 클라이언트가 될 수 있다.

---

## 확장성

- **Connector 교체**: OpenAI, Claude, Gemini, 자체 모델, RAG only, Stub를 **동일 계약**으로 바꿔 끼우기 가능. `LibraryConnectorBase`를 상속해 `query`( 및 선택 `query_with_confidence`)만 구현하면 된다.
- **패키지 이름**: 이 패키지는 **`Library`** 로 import. (`from Library import visit`.) 디렉터리명·레포명(Library_of_Babel)과 맞추어 유지.

---

## 설치·의존

- Python 3.8+
- **선택**: `openai` — `OPENAI_API_KEY` 설정 시 자동 사용. 없으면 Stub 동작.

```bash
pip install -r requirements.txt   # openai 등 (선택)
```

---

## 사용법

### 방문 한 번 하기

```python
from Library import visit, get_connector

context = {
    "perception": {"food_security": 0.6, "social_tension": 0.4},
    "goal": {"food_security": 0.8, "social_tension": 0.2},
    "memory_summary": "최근 3회 grain_release 실행.",
    "observer_verdict": "STABLE",
}
result = visit(context)
# result["insight"], result["digest"], result["confidence"]
```

### Connector 주입 (OpenAI / Stub / 커스텀)

```python
from Library import visit, LibraryConnectorOpenAI, LibraryConnectorStub, LibraryConnectorBase

# OpenAI
conn = LibraryConnectorOpenAI(model="gpt-4o-mini")
result = visit(context, connector=conn)

# Stub
result = visit(context, connector=LibraryConnectorStub())

# 커스텀 (Claude, Gemini, 자체 모델, RAG)
class MyConnector(LibraryConnectorBase):
    def query(self, system_prompt: str, user_prompt: str, **kwargs):
        return "내부 LLM 또는 RAG 결과"
    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs):
        return (self.query(system_prompt, user_prompt, **kwargs), 0.6)
result = visit(context, connector=MyConnector())
```

---

## 디렉터리

```
Library/
├── __init__.py    # visit, get_connector, LibraryConnectorBase 등 export
├── connector.py   # Base, Stub, OpenAI (query_with_confidence 지원)
├── visit.py       # visit(context) -> { insight, digest, confidence }
├── README.md      # 본 문서
├── BLOCKCHAIN_INFO.md  # PHAM 블록체인 서명
└── requirements.txt   # openai (선택)
```

---

## 라이선스·블록체인

- **라이선스**: MIT License  
- **블록체인**: PHAM (Proof of Authorship & Merit) 서명 — [BLOCKCHAIN_INFO.md](BLOCKCHAIN_INFO.md) 참고.

---

**작성**: GNJz (Qquarts)  
**저장소**: [github.com/qquartsco-svg/Library_of_Babel](https://github.com/qquartsco-svg/Library_of_Babel)
