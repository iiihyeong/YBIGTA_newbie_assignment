"""Solar Pro3 LLM utility for RAG answer generation.

Uses Upstage Solar API (OpenAI-compatible) with solar-pro3 model.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://api.upstage.ai/v1/solar"
MODEL = "solar-mini"

NO_RAG_PROMPT = "Answer the following question concisely.\n\nQuestion: {question}"

RAG_PROMPT = """\
Answer the question based ONLY on the provided context.
If the answer is not found in the context, reply exactly: "The provided context does not contain this information."
Do NOT use any outside knowledge.

Context:
{context}

Question: {question}"""


def _get_api_key() -> str:
    """Get the first available Upstage API key."""
    key = os.getenv("UPSTAGE_API_KEY1") or os.getenv("UPSTAGE_API_KEY", "")
    return key.strip()


def generate(question: str, context: str | None = None) -> str:
    """Generate an answer using Solar LLM.

    Args:
        question: The user question.
        context: Retrieved context for RAG. None for no-RAG generation.

    Returns:
        str: The model's answer text.

    Hints:
        - Use _get_api_key() and OpenAI(api_key=..., base_url=BASE_URL)
        - If context is provided, use RAG_PROMPT; otherwise use NO_RAG_PROMPT
        - Use client.chat.completions.create(model=MODEL, messages=[...])
        - Set temperature=0 for deterministic output, max_tokens=1024
    """
    # API 키 가져오기
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY not found in environment")
    
    # OpenAI 클라이언트 초기화 (Solar API는 OpenAI 호환)
    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    
    # Prompt 선택 (RAG vs No-RAG)
    if context is not None:
        # RAG 모드: 검색된 문서를 Context로 포함
        prompt = RAG_PROMPT.format(context=context, question=question)
    else:
        # No-RAG 모드: 일반 질답
        prompt = NO_RAG_PROMPT.format(question=question)
    
    # LLM 호출 (solar-mini 모델)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,  # 결정적 출력
        max_tokens=1024,
    )
    
    # 응답 추출 및 반환
    answer = response.choices[0].message.content.strip()
    
    return answer
