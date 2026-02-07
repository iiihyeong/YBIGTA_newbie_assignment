"""RAG Playground - Streamlit App

Compare 3 retrieval methods (BM25, Vector, Hybrid) on rag-mini-wikipedia dataset.

Tabs:
  1. Data Management - Download, embed, and ingest data
  2. Search Playground - Compare retrieval methods side-by-side
  3. RAG Test - Compare No RAG vs BM25/Vector/Hybrid RAG answers
"""

import json
import sys
from pathlib import Path

import streamlit as st

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

# --- Page Config ---
st.set_page_config(
    page_title="RAG Playground",
    page_icon="🔍",
    layout="wide",
)

st.title("RAG Playground")
st.caption("Compare BM25, Vector, and Hybrid retrieval on Wikipedia dataset (3,200 passages)")

# --- Paths ---
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CORPUS_PATH = RAW_DIR / "corpus.jsonl"
QA_PATH = RAW_DIR / "qa.jsonl"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in open(path, encoding="utf-8"))


# ============================================================
# Tab 1: Data Management
# ============================================================
tab_data, tab_search, tab_rag = st.tabs(["Data Management", "Search Playground", "RAG Test"])

with tab_data:
    st.header("Data Management")
    st.markdown("Execute each step in order to prepare the data pipeline.")

    # --- Step 1: Download ---
    st.subheader("1. Download Dataset")
    col1, col2 = st.columns([1, 2])
    with col1:
        download_btn = st.button("Download from HuggingFace", use_container_width=True)
    with col2:
        if CORPUS_PATH.exists():
            n = count_lines(CORPUS_PATH)
            st.success(f"Corpus ready: {n:,} passages")
        else:
            st.info("Not yet downloaded")

    if download_btn:
        with st.spinner("Downloading dataset from HuggingFace..."):
            from data.download import download
            n_corpus, n_qa = download()
        st.success(f"Downloaded {n_corpus:,} passages and {n_qa:,} QA pairs")
        st.rerun()

    st.divider()

    # --- Step 2: Embeddings ---
    st.subheader("2. Compute Embeddings (Upstage Solar)")
    col1, col2 = st.columns([1, 2])
    with col1:
        embed_btn = st.button("Compute Embeddings", use_container_width=True,
                              disabled=not CORPUS_PATH.exists())
    with col2:
        if EMBEDDINGS_PATH.exists():
            import numpy as np
            shape = np.load(EMBEDDINGS_PATH, mmap_mode="r").shape
            st.success(f"Embeddings ready: {shape}")
        elif not CORPUS_PATH.exists():
            st.warning("Download data first")
        else:
            st.info("Not yet computed")

    if embed_btn:
        texts, ids = [], []
        with open(CORPUS_PATH, encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                ids.append(doc["id"])
                texts.append(doc["text"])

        progress_bar = st.progress(0, text="Computing embeddings...")
        from ingest.embedding import embed_passages

        def update_progress(current, total):
            progress_bar.progress(current / total, text=f"Batch {current}/{total}")

        embed_passages(texts, ids, progress_callback=update_progress)
        progress_bar.progress(1.0, text="Done!")
        st.success(f"Computed embeddings for {len(ids):,} passages")
        st.rerun()

    st.divider()

    # --- Step 3: ES BM25 ---
    st.subheader("3. Elasticsearch BM25 Index")
    col1, col2 = st.columns([1, 2])
    with col1:
        es_bm25_btn = st.button("Ingest ES BM25", use_container_width=True,
                                disabled=not CORPUS_PATH.exists())
    with col2:
        try:
            from ingest.elastic.ingest import get_es_client, INDEX_NAME as BM25_INDEX
            es = get_es_client()
            if es.indices.exists(index=BM25_INDEX):
                count = es.count(index=BM25_INDEX)["count"]
                st.success(f"Index '{BM25_INDEX}' ready: {count:,} docs")
            else:
                st.info("Index not created yet")
        except Exception:
            st.info("ES not connected or index not ready")

    if es_bm25_btn:
        with st.spinner("Ingesting into Elasticsearch BM25..."):
            from ingest.elastic.ingest import ingest as es_bm25_ingest
            count = es_bm25_ingest()
        st.success(f"Indexed {count:,} documents")
        st.rerun()

    st.divider()

    # --- Step 4: Pinecone ---
    st.subheader("4. Pinecone Vector Index")
    col1, col2 = st.columns([1, 2])
    with col1:
        pinecone_btn = st.button("Ingest Pinecone", use_container_width=True,
                                 disabled=not EMBEDDINGS_PATH.exists())
    with col2:
        try:
            import os
            from pinecone import Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            idx = pc.Index(os.getenv("PINECONE_INDEX", "ragsession"))
            stats = idx.describe_index_stats()
            st.success(f"Pinecone index ready: {stats.total_vector_count:,} vectors")
        except Exception:
            if EMBEDDINGS_PATH.exists():
                st.info("Pinecone not connected or index not ready")
            else:
                st.warning("Compute embeddings first")

    if pinecone_btn:
        progress_bar = st.progress(0, text="Upserting to Pinecone...")
        from ingest.pinecone.ingest import ingest as pinecone_ingest

        def update_pinecone(current, total):
            progress_bar.progress(current / total, text=f"Batch {current}/{total}")

        count = pinecone_ingest(progress_callback=update_pinecone)
        progress_bar.progress(1.0, text="Done!")
        st.success(f"Upserted {count:,} vectors")
        st.rerun()

    st.divider()

    # --- Step 5: ES Hybrid ---
    st.subheader("5. Elasticsearch Hybrid Index")
    col1, col2 = st.columns([1, 2])
    with col1:
        es_hybrid_btn = st.button("Ingest ES Hybrid", use_container_width=True,
                                  disabled=not EMBEDDINGS_PATH.exists())
    with col2:
        try:
            from ingest.hybrid.ingest import get_es_client as get_hybrid_es, INDEX_NAME as HYBRID_INDEX
            es_h = get_hybrid_es()
            if es_h.indices.exists(index=HYBRID_INDEX):
                count = es_h.count(index=HYBRID_INDEX)["count"]
                st.success(f"Index '{HYBRID_INDEX}' ready: {count:,} docs")
            else:
                st.info("Index not created yet")
        except Exception:
            if EMBEDDINGS_PATH.exists():
                st.info("ES not connected or index not ready")
            else:
                st.warning("Compute embeddings first")

    if es_hybrid_btn:
        with st.spinner("Ingesting into Elasticsearch Hybrid..."):
            from ingest.hybrid.ingest import ingest as es_hybrid_ingest
            count = es_hybrid_ingest()
        st.success(f"Indexed {count:,} documents")
        st.rerun()


# ============================================================
# Tab 2: Search Playground
# ============================================================
with tab_search:
    st.header("Search Playground")

    # --- Sidebar controls ---
    with st.sidebar:
        st.header("Search Settings")

        search_mode = st.radio(
            "Retrieval Mode",
            ["BM25", "Vector", "Hybrid", "Compare All"],
            index=3,
        )

        top_k = st.slider("Top-K Results", min_value=1, max_value=50, value=10)

        if search_mode in ("Hybrid", "Compare All"):
            candidate_size = st.slider(
                "Hybrid Candidate Pool",
                min_value=20, max_value=200, value=50,
                help="Number of candidates for kNN before RRF fusion",
            )
        else:
            candidate_size = 50

        st.divider()
        st.markdown("**Sample queries:**")
        sample_queries = [
            "Who suggested Lincoln grow a beard?",
            "What fraternity was Coolidge a member of?",
            "What happened to Avogadro in 1833?",
            "What was the nickname of Theodore Roosevelt's sister Anna?",
            "What suborder of turtles is extinct?",
            "Who did Sir Thomas Stamford Raffles work for?",
            "What is the primary domestic source of water supply in Singapore?",
            "Where was Theodore Roosevelt born?",
            "What resembles that of the similarly-sized cougar in the Americas?",
            "What trail did Lincoln use a Farmers' Almanac in?",
        ]
        for q in sample_queries:
            st.markdown(f"- {q}")

    # --- Query input ---
    query = st.text_input(
        "Enter your query",
        value=st.session_state.get("query_input", ""),
        placeholder="e.g., Was Abraham Lincoln the sixteenth President of the United States?",
        key="query_box",
    )

    if query:
        def render_results(results: list[dict], header: str | None = None):
            if header:
                st.subheader(header)
            if not results:
                st.warning("No results found.")
                return
            for i, r in enumerate(results, 1):
                with st.expander(f"**#{i}** | Score: {r['score']:.4f} | {r['method']}", expanded=(i <= 3)):
                    st.markdown(r["text"])
                    st.caption(f"ID: {r['id']}")

        if search_mode == "Compare All":
            col_bm25, col_vec, col_hyb = st.columns(3)

            with col_bm25:
                st.subheader("BM25")
                try:
                    from retrievers.elastic.retriever import search as bm25_search
                    results = bm25_search(query, top_k=top_k)
                    render_results(results)
                except Exception as e:
                    st.error(f"BM25 error: {e}")

            with col_vec:
                st.subheader("Vector")
                try:
                    from retrievers.pinecone.retriever import search as vec_search
                    results = vec_search(query, top_k=top_k)
                    render_results(results)
                except Exception as e:
                    st.error(f"Vector error: {e}")

            with col_hyb:
                st.subheader("Hybrid (RRF)")
                try:
                    from retrievers.hybrid.retriever import search as hyb_search
                    results = hyb_search(query, top_k=top_k, candidate_size=candidate_size)
                    render_results(results)
                except Exception as e:
                    st.error(f"Hybrid error: {e}")

        else:
            try:
                if search_mode == "BM25":
                    from retrievers.elastic.retriever import search as bm25_search
                    results = bm25_search(query, top_k=top_k)
                elif search_mode == "Vector":
                    from retrievers.pinecone.retriever import search as vec_search
                    results = vec_search(query, top_k=top_k)
                else:  # Hybrid
                    from retrievers.hybrid.retriever import search as hyb_search
                    results = hyb_search(query, top_k=top_k, candidate_size=candidate_size)

                render_results(results, header=f"{search_mode} Results")
            except Exception as e:
                st.error(f"Search error: {e}")
    else:
        st.info("Enter a query above or select a sample query from the sidebar.")


# ============================================================
# Tab 3: RAG Test
# ============================================================
with tab_rag:
    st.header("RAG Test")
    st.markdown("Compare answers: **No RAG** vs **BM25 RAG** vs **Vector RAG** vs **Hybrid RAG**")

    rag_query = st.text_input(
        "Enter your question",
        placeholder="e.g., Who assassinated Lincoln?",
        key="rag_query_box",
    )

    generate_btn = st.button("Generate", type="primary", key="rag_generate")

    if generate_btn and rag_query:
        from app.llm import generate

        col_no, col_bm25, col_vec, col_hyb = st.columns(4)

        # --- No RAG ---
        with col_no:
            st.subheader("No RAG")
            with st.spinner("Generating..."):
                try:
                    no_rag_answer = generate(rag_query)
                    st.markdown(no_rag_answer)
                except Exception as e:
                    st.error(f"Error: {e}")

        # --- BM25 RAG ---
        with col_bm25:
            st.subheader("BM25 RAG")
            with st.spinner("Searching & generating..."):
                try:
                    from retrievers.elastic.retriever import search as bm25_search
                    bm25_results = bm25_search(rag_query, top_k=5)
                    bm25_context = "\n\n".join(r["text"] for r in bm25_results)
                    bm25_answer = generate(rag_query, context=bm25_context)
                    st.markdown(bm25_answer)
                    with st.expander("Context used"):
                        for i, r in enumerate(bm25_results, 1):
                            st.caption(f"**#{i}** (score: {r['score']:.4f})")
                            st.markdown(r["text"])
                except Exception as e:
                    st.error(f"Error: {e}")

        # --- Vector RAG ---
        with col_vec:
            st.subheader("Vector RAG")
            with st.spinner("Searching & generating..."):
                try:
                    from retrievers.pinecone.retriever import search as vec_search
                    vec_results = vec_search(rag_query, top_k=5)
                    vec_context = "\n\n".join(r["text"] for r in vec_results)
                    vec_answer = generate(rag_query, context=vec_context)
                    st.markdown(vec_answer)
                    with st.expander("Context used"):
                        for i, r in enumerate(vec_results, 1):
                            st.caption(f"**#{i}** (score: {r['score']:.4f})")
                            st.markdown(r["text"])
                except Exception as e:
                    st.error(f"Error: {e}")

        # --- Hybrid RAG ---
        with col_hyb:
            st.subheader("Hybrid RAG")
            with st.spinner("Searching & generating..."):
                try:
                    from retrievers.hybrid.retriever import search as hyb_search
                    hyb_results = hyb_search(rag_query, top_k=5)
                    hyb_context = "\n\n".join(r["text"] for r in hyb_results)
                    hyb_answer = generate(rag_query, context=hyb_context)
                    st.markdown(hyb_answer)
                    with st.expander("Context used"):
                        for i, r in enumerate(hyb_results, 1):
                            st.caption(f"**#{i}** (score: {r['score']:.4f})")
                            st.markdown(r["text"])
                except Exception as e:
                    st.error(f"Error: {e}")

    elif generate_btn and not rag_query:
        st.warning("Please enter a question first.")
    else:
        st.info("Enter a question and click **Generate** to compare RAG approaches.")
