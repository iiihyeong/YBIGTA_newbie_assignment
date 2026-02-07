"""Ingest corpus into Elasticsearch BM25 index (wiki-bm25).

Index mapping: text field only (no vectors).
Bulk chunk_size=500 (lightweight without vectors).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

load_dotenv()

INDEX_NAME = "wiki-bm25"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

INDEX_MAPPINGS = {
    "properties": {
        "text": {"type": "text", "analyzer": "standard"},
    }
}


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=60,
    )


def _generate_actions(corpus_path: Path):
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": {
                    "text": doc["text"],
                },
            }


def ingest(progress_callback=None):
    """Create BM25 index and bulk-ingest corpus into Elasticsearch.

    Args:
        progress_callback: Optional callback(count) called after completion.

    Returns:
        int: Number of documents indexed.

    Hints:
        - Use get_es_client() to get ES client
        - Delete existing index if it exists, then create with INDEX_MAPPINGS
        - Corpus is at RAW_DIR / "corpus.jsonl"
        - Use _generate_actions(corpus_path) for bulk data
        - Use elasticsearch.helpers.bulk() with chunk_size=500
        - Call es.indices.refresh() after bulk ingest
    """
    # TODO: Implement BM25 ingest
    es = get_es_client()
    corpus_path = RAW_DIR / "corpus.jsonl"
    
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
    
    # 1️기존 인덱스 삭제
    if es.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index: {INDEX_NAME}")
        es.indices.delete(index=INDEX_NAME)
    
    # 2️새 인덱스 생성 (BM25는 기본 알고리즘)
    print(f"Creating index: {INDEX_NAME} with BM25 mapping")
    es.indices.create(
        index=INDEX_NAME,
        mappings=INDEX_MAPPINGS,
    )
    
    # 3️Bulk ingest
    print(f"Bulk ingesting corpus from {corpus_path}...")
    actions = _generate_actions(corpus_path)
    
    success_count, error_list = bulk(
        es,
        actions,
        chunk_size=500,
        raise_on_error=False,
    )
    
    # 4️인덱스 새로고침
    es.indices.refresh(index=INDEX_NAME)
    
    # 5️결과 출력
    print(f"Successfully indexed {success_count} documents into {INDEX_NAME}")
    if error_list:
        print(f"Errors during indexing: {len(error_list)}")
        for error in error_list[:5]:  # 처음 5개 에러만 출력
            print(f"  - {error}")
    
    # 6️⃣ Progress callback 호출
    if progress_callback:
        progress_callback(success_count)
    
    return success_count


if __name__ == "__main__":
    ingest()
