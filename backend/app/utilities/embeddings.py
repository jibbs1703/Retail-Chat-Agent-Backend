"""Embedding utilities for text processing."""

import numpy as np
from fastembed import TextEmbedding

from app.core.config import get_settings

settings = get_settings()
embedding_model = TextEmbedding(model_name=settings.OLLAMA_EMBEDDING_MODEL)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    try:
        embeddings = list(embedding_model.embed(texts))
        return embeddings
    except (RuntimeError, ValueError, IndexError) as e:
        print(f"Embedding generation failed: {e}")
        return [[] for _ in texts]


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text."""
    embeddings = generate_embeddings([text])
    return embeddings[0] if embeddings else []


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


def find_similar_texts(
    query_embedding: list[float], text_embeddings: list[list[float]], top_k: int = 5
) -> list[tuple]:
    """Find most similar texts based on embeddings."""
    similarities = []

    for i, emb in enumerate(text_embeddings):
        if emb:
            sim = cosine_similarity(query_embedding, emb)
            similarities.append((i, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > chunk_size // 2:
                end = start + last_space
                chunk = text[start:end]

        chunks.append(chunk)
        start = end - overlap

        if start >= len(text):
            break

    return chunks
