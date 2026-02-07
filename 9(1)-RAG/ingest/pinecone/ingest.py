"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    # 1️ 임베딩 및 ID 로드
    embeddings_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    corpus_path = RAW_DIR / "corpus.jsonl"
    
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
    
    # 2 텍스트 로드 (ID → text 매핑)
    print(f"Loading corpus from {corpus_path}...")
    id_to_text = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            id_to_text[doc["id"]] = doc["text"]
    
    print(f"Loaded {embeddings.shape[0]} embeddings and {len(id_to_text)} texts")
    
    # 3 Pinecone 연결
    print(f"Connecting to Pinecone...")
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "wiki-vectors")
    
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment")
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # 4 배치 단위로 upsert
    total = len(ids)
    upserted_count = 0
    
    for batch_start in tqdm(range(0, len(ids), BATCH_SIZE), desc="Upserting to Pinecone"):
        batch_end = min(batch_start + BATCH_SIZE, len(ids))
        batch_ids = ids[batch_start:batch_end]
        batch_embeddings = embeddings[batch_start:batch_end]
        
        # 벡터-메타데이터 쌍 생성
        vectors = []
        for i, doc_id in enumerate(batch_ids):
            # 텍스트를 메타데이터로 포함 (1000자 제한)
            text = id_to_text.get(doc_id, "")[:TEXT_LIMIT]
            
            vectors.append({
                "id": doc_id,
                "values": batch_embeddings[i].tolist(),
                "metadata": {"text": text},
            })
        
        # Pinecone에 upsert
        try:
            index.upsert(vectors=vectors)
            upserted_count += len(vectors)
            
            # Progress callback 호출
            if progress_callback:
                progress_callback(upserted_count, total)
        except Exception as e:
            print(f"Error upserting batch [{batch_start}:{batch_end}]: {e}")
            raise
    
    print(f"Successfully upserted {upserted_count} vectors to {index_name}")
    return upserted_count


if __name__ == "__main__":
    ingest()
