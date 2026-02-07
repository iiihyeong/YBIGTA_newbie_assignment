"""Vector retriever using Pinecone (cosine similarity)."""

import os

from dotenv import load_dotenv
from pinecone import Pinecone

from ingest.embedding import embed_query

load_dotenv()


def search(query: str, top_k: int = 10) -> list[dict]:
    """Vector cosine similarity search.

    Args:
        query: Search query string.
        top_k: Number of results to return.

    Returns:
        list[dict], each dict has keys: "id", "text", "score", "method".
        "method" should be "Vector".

    Hints:
        - Use embed_query(query) to get the query embedding vector
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Use index.query(vector=..., top_k=..., include_metadata=True)
        - Text is in match["metadata"]["text"]
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment")

    index_name = os.getenv("PINECONE_INDEX", "wiki-vectors")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # Embed the query
    query_vec = embed_query(query)

    # Query Pinecone index
    try:
        resp = index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    except Exception as e:
        raise

    # Normalize response format: support dict or object with .matches
    matches = None
    if isinstance(resp, dict):
        matches = resp.get("matches") or resp.get("results")
    else:
        matches = getattr(resp, "matches", None) or getattr(resp, "results", None)

    results = []
    if not matches:
        return results

    for m in matches:
        if isinstance(m, dict):
            mid = m.get("id")
            score = m.get("score")
            metadata = m.get("metadata") or {}
        else:
            mid = getattr(m, "id", None)
            score = getattr(m, "score", None)
            metadata = getattr(m, "metadata", {})

        text = ""
        if metadata:
            if isinstance(metadata, dict):
                text = metadata.get("text", "")
            else:
                text = getattr(metadata, "text", "")

        results.append({
            "id": str(mid),
            "text": text,
            "score": float(score) if score is not None else None,
            "method": "Vector",
        })

    return results
