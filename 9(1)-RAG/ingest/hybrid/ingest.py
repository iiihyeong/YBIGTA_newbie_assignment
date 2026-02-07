"""Ingest corpus into Elasticsearch Hybrid index (wiki-hybrid).

Index mapping: text field + dense_vector(4096, cosine).
Bulk chunk_size=100 (heavier with 4096-dim vectors).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-hybrid"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
        "embedding": {
            "type": "dense_vector",
            "dims": 4096,
            "index": True,
            "similarity": "cosine",
        },
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=120,
    )


def _generate_actions(corpus_path: Path, embeddings: np.ndarray, ids: list[str]):
    id_to_idx = {doc_id: idx for idx, doc_id in enumerate(ids)}

    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc["id"]
            idx = id_to_idx.get(doc_id)
            if idx is None:
                continue
            yield {
                "_index": INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "text": doc["text"],
                    "embedding": embeddings[idx].tolist(),
                },
            }


def ingest(progress_callback=None):
    """Create hybrid index (text + dense_vector) and bulk-ingest corpus.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Use get_es_client(), delete/create index with INDEX_MAPPINGS
        - Use _generate_actions(corpus_path, embeddings, ids) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=100
        - Call es.indices.refresh() after bulk ingest
    """
    es = get_es_client()
    corpus_path = RAW_DIR / "corpus.jsonl"
    
    # 1️⃣ 임베딩 및 ID 로드
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    
    if not embeddings_path.exists() or not ids_path.exists():
        raise FileNotFoundError(
            f"Embeddings not found. Run embed_passages() first.\n"
            f"  embeddings: {embeddings_path}\n"
            f"  ids: {ids_path}"
        )
    
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
    
    print(f"Loading embeddings from {embeddings_path}...")
    embeddings = np.load(embeddings_path)
    ids = json.loads(ids_path.read_text(encoding="utf-8"))
    
    print(f"Loaded {embeddings.shape[0]} embeddings with shape {embeddings.shape}")
    
    # 2️⃣ 기존 인덱스 삭제
    if es.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index: {INDEX_NAME}")
        es.indices.delete(index=INDEX_NAME)
    
    # 3️⃣ 새 인덱스 생성 (text + dense_vector)
    print(f"Creating index: {INDEX_NAME} with hybrid mapping (text + 4096-dim vectors)")
    es.indices.create(
        index=INDEX_NAME,
        mappings=INDEX_MAPPINGS,
    )
    
    # 4️⃣ Bulk ingest (벡터가 무거우므로 chunk_size=100)
    print(f"Bulk ingesting corpus with embeddings...")
    actions = _generate_actions(corpus_path, embeddings, ids)
    
    success_count, error_list = bulk(
        es,
        actions,
        chunk_size=100,
        raise_on_error=False,
    )
    
    # 5️⃣ 인덱스 새로고침
    es.indices.refresh(index=INDEX_NAME)
    
    # 6️⃣ 결과 출력
    print(f"Successfully indexed {success_count} documents into {INDEX_NAME}")
    if error_list:
        print(f"Errors during indexing: {len(error_list)}")
        for error in error_list[:5]:  # 처음 5개 에러만 출력
            print(f"  - {error}")
    
    # 7️⃣ Progress callback 호출
    if progress_callback:
        progress_callback(success_count)
    
    return success_count


if __name__ == "__main__":
    ingest()
