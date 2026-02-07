"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support with rank_constant=60.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN.

    Args:
        query: Search query string.
        top_k: Number of results to return.
        candidate_size: Number of kNN candidates before RRF fusion.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Hybrid (RRF)".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Use get_es_client() and es.search() with "retriever" parameter
        - RRF retriever combines "standard" (BM25 match) + "knn" retrievers
        - kNN field: "embedding", rank_constant: 60
        - num_candidates = candidate_size * 2
    """
    # TODO: Implement hybrid RRF search
    # 1. 질문을 벡터로 변환 (Solar 모델 호출)
    query_vector = embed_query(query)
    
    # 2. ES 클라이언트 초기화
    es = get_es_client()

    # 3. RRF 기반 하이브리드 검색 쿼리 구성
    # ES 8.14+의 'retriever' 기능을 사용하여 BM25와 kNN을 결합합니다.
    search_body = {
        "retriever": {
            "rrf": {
                "retrievers": [
                    {
                        "standard": {  # BM25 키워드 검색
                            "query": {
                                "match": {
                                    "text": query
                                }
                            }
                        }
                    },
                    {
                        "knn": {  # 벡터 검색
                            "field": "embedding",
                            "query_vector": query_vector,
                            "k": candidate_size,
                            "num_candidates": candidate_size * 2
                        }
                    }
                ],
                "rank_constant": 60,  # RRF 공식의 k값
                "rank_window_size": top_k
            }
        },
        "size": top_k  # 최종 반환할 결과 개수
    }

    # 4. 검색 수행
    response = es.search(index=INDEX_NAME, body=search_body)

    # 5. 결과 포맷팅
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            "text": hit["_source"]["text"],
            "score": hit["_score"],
            "method": "Hybrid (RRF)"
        })

    return results
