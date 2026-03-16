# 🔗 PHAM 블록체인 서명 정보

## 📋 개요

이 **Library of Babel (바벨 도서관)** 은 **PHAM (Proof of Authorship & Merit) 블록체인 시스템**으로 서명되어 있습니다.

> 바벨 도서관 — 필요할 때만 **방문**하는 외부 고급 지식·추론 공간.
> 정보 연결(검색, RAG) + LLM 대화 연결(OpenAI, Claude, Gemini, 자체, Stub).
> Atom·Athena 등 지능체가 insight/digest/confidence를 받아 개인 저장소에 내재화하고 판단 품질을 높이는 **표준화된 지식 수급 인프라**.

---

## 🏛️ 엔진 구성

```
Library/
├── __init__.py       — visit, get_connector, LibraryConnectorBase 등 export
├── connector.py      — Base, Stub, OpenAI (query_with_confidence 지원)
├── visit.py          — visit(context) -> { insight, digest, confidence }
├── README.md         — 개념·수식·활용성·확장성·LLM 연결
├── BLOCKCHAIN_INFO.md — 본 문서
└── requirements.txt  — openai (선택)
```

---

## 🔐 인터페이스 계약

| 항목 | 내용 |
|------|------|
| **입력** | `context`: perception, goal, memory_summary, (선택) observer_verdict, extra |
| **출력** | `insight` (str), `digest` (str), `confidence` (float in [0,1]) |
| **Connector** | `LibraryConnectorBase`: query() 또는 query_with_confidence() 구현 |

---

## 💰 블록체인 기반 기여도 시스템

**라이선스**: MIT License  
**사용 제한**: 없음  
**로열티 요구**: 없음  

### ⚠️ GNJz의 기여도 원칙 (블록체인 기반)

- 상한선: GNJz의 기여도는 블록체인 기반으로 최대 70% 상한
- 검증 가능성: 블록체인으로 검증 가능한 기여도 상한선
- 투명성: 모든 기여도 계산은 블록체인에 기록되어 검증 가능

이 원칙은 코드가 어떻게 상용화되든, 누가 상용화하든 관계없이 블록체인에 영구 기록됩니다.

---

## 📞 문의

- GitHub: https://github.com/qquartsco-svg/Library_of_Babel
- Issues: https://github.com/qquartsco-svg/Library_of_Babel/issues

---

**작성일**: 2026-03-16  
**버전**: 1.0.0  
**작성자**: GNJz (Qquarts)
