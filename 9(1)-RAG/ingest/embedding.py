"""Upstage Solar embedding utility with disk caching and parallel API keys.

Models:
  - solar-embedding-1-large-passage  (document encoding)
  - solar-embedding-1-large-query    (query encoding)

Uses multiple API keys (UPSTAGE_API_KEY1..N) for parallel embedding.
Each key gets its own thread with independent RPM/TPM limits.
Saves progress incrementally so crashes don't lose work.
Cache: data/processed/embeddings.npy (float32) + embedding_ids.json
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

BATCH_SIZE = 100
RPM_LIMIT = 100
MIN_INTERVAL = 60.0 / RPM_LIMIT
DIM = 4096
BASE_URL = "https://api.upstage.ai/v1/solar"
MAX_CHARS = 12000  # ~3000 tokens, safely under 4000 token limit
MAX_RETRIES = 3


def _get_api_keys() -> list[str]:
    """Collect all UPSTAGE_API_KEY* from env."""
    keys = []
    for i in range(1, 100):
        key = os.getenv(f"UPSTAGE_API_KEY{i}")
        if key:
            keys.append(key.strip())
        else:
            break
    if not keys:
        single = os.getenv("UPSTAGE_API_KEY", "")
        if single:
            keys.append(single.strip())
    return keys


def _truncate(text: str) -> str:
    """Truncate text to stay within token limits."""
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS]
    return text


def _embed_batch_safe(client: OpenAI, batch: list[str]) -> list[list[float]]:
    """Embed a batch with retry and fallback to smaller sub-batches."""
    truncated = [_truncate(t) for t in batch]

    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model="solar-embedding-1-large-passage",
                input=truncated,
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            err_msg = str(e)
            if "maximum context length" in err_msg or "4000 tokens" in err_msg:
                # Split batch in half and process separately
                mid = len(truncated) // 2
                if mid == 0:
                    # Single text too long, truncate more aggressively
                    truncated = [t[:MAX_CHARS // 2] for t in truncated]
                    continue
                left = _embed_batch_safe(client, truncated[:mid])
                time.sleep(MIN_INTERVAL)
                right = _embed_batch_safe(client, truncated[mid:])
                return left + right
            elif attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise


def embed_passages(texts: list[str], ids: list[str], progress_callback=None) -> np.ndarray:
    """Embed passages using parallel API keys.

    Args:
        texts: List of passage strings to embed.
        ids: List of document IDs (same length as texts).
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        np.ndarray of shape (N, 4096), dtype float32.

    Hints:
        - Use _get_api_keys() to get API keys, OpenAI(api_key=..., base_url=BASE_URL) to create clients
        - Use _embed_batch_safe(client, batch) to embed a batch of texts
        - Process texts in chunks of BATCH_SIZE
        - Save results to EMBEDDINGS_PATH (.npy) and IDS_PATH (.json)
    """
    # TODO: Implement embedding logic
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True) # [cite: 116, 150]
    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No API keys found.")
    
    clients = [OpenAI(api_key=key, base_url=BASE_URL) for key in api_keys]
    num_clients = len(clients)
    
    batches = [texts[i : i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]
    results = [None] * len(batches)
    total_texts = len(texts)
    
    # 1️⃣ 순서와 결과를 안전하게 관리하기 위한 Lock
    lock = Lock()
    completed_count = 0

    def worker(batch_idx):
        nonlocal completed_count
        client = clients[batch_idx % num_clients]
        # 키별 속도 제한 분산
        time.sleep((batch_idx % num_clients) * MIN_INTERVAL / num_clients)
        
        # 과제 지정 모델: solar-embedding-1-large-passage [cite: 154]
        batch_res = _embed_batch_safe(client, batches[batch_idx])
        
        # 2️⃣ 데이터 저장 및 Progress 업데이트 시에만 Lock 사용
        with lock:
            results[batch_idx] = batch_res
            completed_count += len(batches[batch_idx])
            # UI 블로킹 방지를 위해 progress_callback 호출 최소화 고려 가능하나, 
            # 여기서는 명세에 충실하게 호출
            if progress_callback:
                progress_callback(completed_count, total_texts)

    # 3️⃣ as_completed를 사용하여 완료되는 순서대로 처리하되 results[idx]로 순서 유지
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [executor.submit(worker, i) for i in range(len(batches))]
        # tqdm으로 터미널 진행 상황 시각화
        for _ in tqdm(as_completed(futures), total=len(batches), desc="Embedding"):
            pass

    # 4️⃣ 최종 결과 통합 및 저장 [cite: 150, 156]
    # np.vstack으로 (N, 4096) 형태 생성
    all_embeddings = np.vstack(results).astype(np.float32)
    
    np.save(EMBEDDINGS_PATH, all_embeddings)
    IDS_PATH.write_text(json.dumps(ids, ensure_ascii=False))
    
    return all_embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query using the query model.

    Args:
        query: The search query string.

    Returns:
        list[float] of length 4096 (embedding vector).

    Hints:
        - Use _get_api_keys() to get an API key
        - Model name: "solar-embedding-1-large-query"
        - Use _truncate() to handle long queries
    """
    # TODO: Implement query embedding
    api_keys = _get_api_keys()
    if not api_keys:
        raise ValueError("No API keys found.")
    
    # 질문용 모델: solar-embedding-1-large-query 
    client = OpenAI(api_key=api_keys[0], base_url=BASE_URL)
    truncated_query = _truncate(query) # 토큰 제한 방지
    
    response = client.embeddings.create(
        model="solar-embedding-1-large-query",
        input=truncated_query,
    )
    
    # 4096 차원의 리스트 반환 
    return response.data[0].embedding


def load_cached_embeddings() -> tuple[np.ndarray, list[str]] | None:
    """Load cached embeddings from disk. Returns (embeddings, ids) or None."""
    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        embeddings = np.load(EMBEDDINGS_PATH)
        ids = json.loads(IDS_PATH.read_text())
        return embeddings, ids
    return None


if __name__ == "__main__":
    from data.download import RAW_DIR

    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print("Run data/download.py first.")
        raise SystemExit(1)

    texts, ids = [], []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            ids.append(doc["id"])
            texts.append(doc["text"])

    embed_passages(texts, ids)