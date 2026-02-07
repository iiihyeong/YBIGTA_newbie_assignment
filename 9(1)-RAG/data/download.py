"""Download rag-mini-wikipedia dataset from HuggingFace.

Saves:
  data/raw/corpus.jsonl  - 3,200 passages (id, text)
  data/raw/qa.jsonl      - 918 QA pairs (question, answer)
"""

import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm

RAW_DIR = Path(__file__).resolve().parent / "raw"


def download():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # --- text-corpus split (3,200 passages) ---
    print("Downloading text-corpus split...")
    corpus_ds = load_dataset("rag-datasets/rag-mini-wikipedia", "text-corpus", split="passages")

    corpus_path = RAW_DIR / "corpus.jsonl"
    with open(corpus_path, "w", encoding="utf-8") as f:
        for i, row in enumerate(tqdm(corpus_ds, desc="Writing corpus")):
            doc = {
                "id": str(row["id"]),
                "text": row["passage"],
            }
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Saved {i + 1} passages to {corpus_path}")

    # --- question-answer split (918 QA pairs) ---
    print("Downloading question-answer split...")
    qa_ds = load_dataset("rag-datasets/rag-mini-wikipedia", "question-answer", split="test")

    qa_path = RAW_DIR / "qa.jsonl"
    with open(qa_path, "w", encoding="utf-8") as f:
        for j, row in enumerate(tqdm(qa_ds, desc="Writing QA")):
            doc = {
                "question": row["question"],
                "answer": row["answer"],
            }
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Saved {j + 1} QA pairs to {qa_path}")

    return i + 1, j + 1


if __name__ == "__main__":
    download()
