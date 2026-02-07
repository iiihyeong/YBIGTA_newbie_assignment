# RAG Playground

Wikipedia 3,200개 passage를 활용한 RAG(Retrieval-Augmented Generation) 실습 프로젝트입니다.
BM25, Vector, Hybrid 세 가지 검색 방식을 직접 구현하고, LLM 답변 생성까지 완성합니다.

## 학습 목표

1. **임베딩 이해** - 텍스트를 벡터로 변환하는 Embedding API 호출 방법 학습
2. **DB 적재 경험** - Elasticsearch(BM25/Hybrid)와 Pinecone(Vector)에 데이터를 인덱싱
3. **검색 구현** - BM25, Vector(cosine similarity), Hybrid(RRF) 세 가지 Retriever 작성
4. **RAG 파이프라인 완성** - 검색된 컨텍스트를 LLM에 전달하여 답변을 생성하는 전체 흐름 구현
5. **비교 실험** - No RAG vs BM25 RAG vs Vector RAG vs Hybrid RAG 답변 품질 비교

## 폴더 구조

```
Rag-session/
├── app/
│   ├── streamlit_app.py          # Streamlit UI (수정 불필요)
│   └── llm.py                    # [TODO] Solar LLM 답변 생성
│
├── data/
│   ├── download.py               # HuggingFace 데이터 다운로드 (완성됨)
│   ├── raw/                      # corpus.jsonl, qa.jsonl (다운로드 후 생성)
│   └── processed/                # embeddings.npy, embedding_ids.json (임베딩 후 생성)
│
├── ingest/
│   ├── embedding.py              # [TODO] 임베딩 계산 (embed_passages, embed_query)
│   ├── elastic/
│   │   └── ingest.py             # [TODO] Elasticsearch BM25 인덱스 적재
│   ├── pinecone/
│   │   └── ingest.py             # [TODO] Pinecone 벡터 적재
│   └── hybrid/
│       └── ingest.py             # [TODO] Elasticsearch Hybrid 인덱스 적재
│
├── retrievers/
│   ├── elastic/
│   │   └── retriever.py          # [TODO] BM25 검색
│   ├── pinecone/
│   │   └── retriever.py          # [TODO] Vector 검색
│   └── hybrid/
│       └── retriever.py          # [TODO] Hybrid (RRF) 검색
│
├── .env                          # API 키 설정 (gitignore 대상)
├── .env.example                  # .env 템플릿
└── requirements.txt              # 패키지 의존성
```

## 구현해야 할 함수 (총 9개)

### Step 1. 임베딩

| 파일 | 함수 | 설명 |
|------|------|------|
| `ingest/embedding.py` | `embed_passages(texts, ids)` | 텍스트 리스트를 배치로 임베딩하여 `(N, 4096)` numpy 배열 반환 및 저장 |
| `ingest/embedding.py` | `embed_query(query)` | 단일 쿼리를 임베딩하여 `list[float]` 반환 |

- Passage 모델: `solar-embedding-1-large-passage`
- Query 모델: `solar-embedding-1-large-query`
- 벡터 차원: 4096

### Step 2. DB 적재

| 파일 | 함수 | 설명 |
|------|------|------|
| `ingest/elastic/ingest.py` | `ingest()` | corpus.jsonl을 Elasticsearch BM25 인덱스(`wiki-bm25`)에 적재 |
| `ingest/pinecone/ingest.py` | `ingest()` | 임베딩 벡터를 Pinecone 인덱스에 upsert |
| `ingest/hybrid/ingest.py` | `ingest()` | corpus + 임베딩을 Elasticsearch Hybrid 인덱스(`wiki-hybrid`)에 적재 |

### Step 3. 검색 (Retriever)

| 파일 | 함수 | 설명 |
|------|------|------|
| `retrievers/elastic/retriever.py` | `search(query, top_k)` | BM25 텍스트 매칭 검색 |
| `retrievers/pinecone/retriever.py` | `search(query, top_k)` | 벡터 코사인 유사도 검색 |
| `retrievers/hybrid/retriever.py` | `search(query, top_k, candidate_size)` | RRF(Reciprocal Rank Fusion) 하이브리드 검색 |

- 반환 형식: `list[dict]` - 각 dict는 `{"id", "text", "score", "method"}` 키를 포함

### Step 4. LLM 답변 생성

| 파일 | 함수 | 설명 |
|------|------|------|
| `app/llm.py` | `generate(question, context)` | Solar LLM으로 답변 생성. context가 None이면 No RAG, 있으면 RAG 프롬프트 사용 |

- API: OpenAI 호환 (`https://api.upstage.ai/v1/solar`)
- temperature=0, max_tokens=1024

## 실행 방법

```bash
# 1. 가상환경 활성화
source .venv/bin/activate

# 2. Streamlit 실행
streamlit run app/streamlit_app.py
```

## 검증 방법

1. **Data Management 탭** - Download → Embedding → ES BM25 → Pinecone → ES Hybrid 순서로 적재
2. **Search Playground 탭** - 쿼리 입력 후 BM25/Vector/Hybrid 검색 결과 확인
3. **RAG Test 탭** - "Who suggested Lincoln grow a beard?" 입력 후 No RAG vs RAG 답변 비교
   - No RAG: 정확한 답을 모를 가능성 높음
   - RAG: "11-year-old Grace Bedell" 답변 확인
