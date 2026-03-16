# Library of Babel — 바벨 도서관

**외부 지혜의 성소.** Atom·Athena 등 지능체가 필요할 때 **방문**해 고급 정보·추론·지혜를 구하고, 이를 **자기 저장소에 내재화**해 판단 품질을 높이는 **표준화된 지식 수급 인프라**이다.

- **한 줄 정의**: 대도서관은 "항상 붙어 있는 뇌"가 아니라, **필요할 때만 방문하는 외부 고급 지식·추론 공간**이다.
- **역할**: 정보 연결(검색, RAG) + **LLM 대화 연결**(OpenAI, Claude, Gemini, 자체 모델, Stub) — 계약만 맞으면 **바꿔 끼우기** 가능.

---

## 개념

### 바벨 도서관 메타포

보르헤스의 **바벨의 도서관**처럼, 여기서 "도서관"은 **방대한 기호·지식이 있는 공간**이지만, 지능체가 **항상 그 안에 있는 것이 아니라** 필요할 때만 찾아와 질문하고, 얻은 답(insight·digest)을 **자기 것으로 만들어 가는** 구조다.

- **평상시**: Atom/Athena는 **일상 복귀·판단형 AI**로 동작.
- **필요 시**: 대도서관 **방문** → 정보 연결 + LLM 대화 연결 → **고급 정보·고급 추론** 획득.
- **복귀 후**: 개인 저장소에 반영 → **같은 판단 로직**이 더 풍부한 참조 저장소를 쓰게 되어 **판단 품질**이 올라감. (엔진 자체가 학습되는 것이 아니라, **참조하는 저장소가 풍부해지는** 구조.)

```
Atom / Athena
    │  (일상 운영)
    │
    ├── 필요 시 방문 ──▶  Library of Babel
    │                          │
    │                    visit(context)
    │                          │
    │                    { insight, digest, confidence }
    │                          │
    └◀──── 복귀 후 내재화 ──────┘
         개인 저장소 풍부화
         → 판단 품질 향상
```

### LLM과 도서관의 연결

| 연결 유형 | 설명 |
|-----------|------|
| **정보 연결** | 검색, RAG, 외부 지식 소스. "무엇이 있는지" 접근. |
| **LLM 대화 연결** | 개인/상용 LLM·API와의 **대화**를 통한 추론·조언·재구성. "무엇을 할지"에 대한 지혜. |

둘을 함께 **바벨 도서관** 하나의 엔진으로 두고, **`visit(context)`** 한 번으로 결과(`insight`, `digest`, `confidence`)를 받는다.

---

## 수식·계약

### 입출력 계약

**입력** `context` (dict):

```python
context = {
    "perception":       ...,  # 현재 관측 요약 (지각)
    "goal":             ...,  # 목표 요약
    "memory_summary":   ...,  # 기억 요약
    "observer_verdict": ...,  # (선택) 옵저버 판정 — HEALTHY/STABLE/FRAGILE/CRITICAL
    "extra":            ...,  # (선택) 기타
}
```

**출력** (dict):

```python
result = {
    "insight":    str,   # 본문 (지식·추론·지혜). 임시 저장·깊은 이해용.
    "digest":     str,   # 한 줄 요약. 개인 저장(장기 후보)용.
    "confidence": float  # [0,1] 응답 신뢰도. connector 제공 또는 휴리스틱. 판단·저장 시 가중치.
}
```

### 방문 함수

```
visit(context; connector?) → { insight, digest, confidence }
```

- `connector`가 없으면: `OPENAI_API_KEY` 있으면 OpenAI, 없으면 Stub.
- connector는 `LibraryConnectorBase` 계약: `query(system_prompt, user_prompt) -> str` 또는 `query_with_confidence(...) -> (text, confidence)`.

### Connector 신뢰도 체계

| Connector | confidence |
|-----------|-----------|
| `LibraryConnectorStub` | 0.0 (기본) — API 없음 |
| `LibraryConnectorOpenAI` | 0.7 (성공 시) |
| 커스텀 | 구현체가 직접 결정 |

### 검증 원칙

insight를 **무조건 믿지 않고**, 필요 시 검증·요약 후 개인 저장(특히 **장기 저장**)에 반영하는 것을 권장. 설계상 **임시 저장(원문)** 과 **장기 저장 후보(digest/검증 통과 요약)** 두 층을 둔다.

---

## 활용성

### Atom (개인로봇형 AI)

```
Atom state ──▶ context 구성 ──▶ visit(context)
                                      │
                              insight     → library_insight (extension)
                              digest      → library_digest_for_memory
                              confidence  → library_confidence          ← v1.1 신규
                                      │
                              L3 판단 시 참조 → 판단 품질 향상
```

- `LibraryVisitLayer.update(state)` — `library_visit_request=True` 또는 주기(visit_interval) 시 방문
- `observer_verdict` 자동 포함 → 도서관이 현재 건강 상태를 알고 맥락에 맞는 조언 제공
- **confidence** 저장으로 신뢰도 낮은 insight 걸러낼 수 있음

### Athena (군주형 거버넌스 AI)

```
AthenaJudgment ──▶ _judgment_to_context() ──▶ visit(context)
                                                    │
                                         insight          → 거버넌스 전략 보완
                                         digest           → 장기 정책 저장 후보
                                         confidence       → 신뢰도 가중치
                                         enhanced_summary → 아테나 요약 + 도서관 한줄  ← v1.1 신규
```

- `athena_library_visit(judgment, connector=None)` — AthenaJudgment를 context로 자동 변환
- 도시 → 국가 → 지구 → 태양계 스케일 거버넌스 판단 보완

### 기타 AI 객체

context dict만 구성할 수 있으면 **어떤 스택이든 클라이언트**가 될 수 있다.

```python
from Library import visit, get_connector

context = { "perception": my_state, "goal": my_goal, "memory_summary": my_mem }
result  = visit(context, connector=get_connector())
```

---

## 확장성

### Connector 교체

OpenAI, Claude, Gemini, 자체 모델, RAG only, Stub를 **동일 계약**으로 바꿔 끼우기 가능.
`LibraryConnectorBase`를 상속해 `query`(및 선택 `query_with_confidence`)만 구현하면 된다.

```python
from Library import LibraryConnectorBase

class MyConnector(LibraryConnectorBase):
    def query(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        return "내부 LLM 또는 RAG 결과"

    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs):
        result = self.query(system_prompt, user_prompt, **kwargs)
        return (result, 0.85)  # 커스텀 신뢰도
```

### 패키지 이름

이 패키지는 **`Library`** 로 import. (`from Library import visit`.) 디렉터리명·레포명(Library_of_Babel)과 맞추어 유지.

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
    "perception":       {"food_security": 0.6, "social_tension": 0.4},
    "goal":             {"food_security": 0.8, "social_tension": 0.2},
    "memory_summary":   "최근 3회 grain_release 실행.",
    "observer_verdict": "STABLE",
}
result = visit(context)
# result["insight"]    → 고급 추론 본문
# result["digest"]     → 한 줄 요약
# result["confidence"] → 0.0 (Stub) / 0.7 (OpenAI 성공 시)
```

### Connector 주입 (OpenAI / Stub / 커스텀)

```python
from Library import visit, LibraryConnectorOpenAI, LibraryConnectorStub, LibraryConnectorBase

# OpenAI
conn   = LibraryConnectorOpenAI(model="gpt-4o-mini")
result = visit(context, connector=conn)

# Stub (API 없는 환경·테스트)
result = visit(context, connector=LibraryConnectorStub())

# 커스텀 (Claude, Gemini, 자체 모델, RAG)
class MyConnector(LibraryConnectorBase):
    def query(self, system_prompt: str, user_prompt: str, **kwargs):
        return "내부 LLM 또는 RAG 결과"
    def query_with_confidence(self, system_prompt: str, user_prompt: str, **kwargs):
        return (self.query(system_prompt, user_prompt, **kwargs), 0.6)

result = visit(context, connector=MyConnector())
```

### Atom에서 사용 (LibraryVisitLayer)

```python
from Atom.atom_layers.library_visit import LibraryVisitLayer
from Atom.atom_state import AtomState
import numpy as np

# 10 스텝마다 자동 방문
layer = LibraryVisitLayer(visit_interval=10)

state = AtomState(state_vector=np.zeros(4), step=10)
state.set_extension("perception", {"food_security": 0.6})
state.set_extension("goal", {"target": "stable"})

state = layer.update(state)

print(state.get_extension("library_insight"))            # 고급 추론
print(state.get_extension("library_confidence"))         # 신뢰도 (v1.1 신규)
print(state.get_extension("library_digest_for_memory"))  # 한 줄 요약

# 즉시 방문 (요청 트리거)
state.set_extension("library_visit_request", True)
state = layer.update(state)
```

### Athena에서 사용 (athena_library_visit)

```python
from Athena import quick_judge, athena_library_visit

# 위기 상황 판단
judgment = quick_judge(maat_score=0.45, food_security=0.25, social_tension=0.70)
lib      = athena_library_visit(judgment)

print(lib["insight"])          # 역사적 선례, 위기 대응 전략 조언
print(lib["confidence"])       # 0.7 (OpenAI) / 0.0 (Stub)
print(lib["enhanced_summary"]) # 아테나 요약 + 도서관 한줄 digest
print(lib["digest"])           # 장기 정책 저장 후보
```

---

## 디렉터리

```
Library/
├── __init__.py        — visit, get_connector, LibraryConnectorBase 등 export
├── connector.py       — Base, Stub, OpenAI (query_with_confidence 지원)
├── visit.py           — visit(context) -> { insight, digest, confidence }
├── tests/
│   └── test_library.py — 28개 단위 테스트 (§1 connector / §2 visit / §3 get_connector / §4 통합)
├── README.md          — 본 문서
├── BLOCKCHAIN_INFO.md — PHAM 블록체인 서명
└── requirements.txt   — openai (선택)
```

---

## 테스트

```bash
# Library 단위 테스트 (28개)
cd 00_BRAIN
python -m pytest Library/tests/test_library.py -v

# Atom 연동 테스트 (20개)
python -m pytest Atom/tests/test_atom_library_visit.py -v

# Athena 연동 테스트 (25개)
python -m pytest Athena/tests/test_athena_library_visit.py -v

# 전체 (Library + Atom + Athena)
python -m pytest Library/ Atom/ Athena/ -q
# → 171 passed
```

---

## 버전 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| **v1.1** | 2026-03-16 | `tests/` 추가 (28개 단위 테스트), Atom `library_confidence` 저장, Athena `athena_library_visit` 연동 |
| **v1.0** | 2026-03-16 | 최초 릴리즈 — `visit(context)`, connector 계층, PHAM 서명 |

---

## 라이선스·블록체인

- **라이선스**: MIT License
- **블록체인**: PHAM (Proof of Authorship & Merit) 서명 — [BLOCKCHAIN_INFO.md](BLOCKCHAIN_INFO.md) 참고.

---

**작성**: GNJz (Qquarts)
**저장소**: [github.com/qquartsco-svg/Library_of_Babel](https://github.com/qquartsco-svg/Library_of_Babel)
**버전**: v1.1.0
