"""Qdrant vector database operations."""

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import get_settings

settings = get_settings()
qdrant_client = QdrantClient(url=settings.QDRANT_BASE_URL)
embedding_model = TextEmbedding(model_name=settings.OLLAMA_EMBEDDING_MODEL)


def initialize_collections():
    """Initialize Qdrant collections if they don't exist."""
    for collection in settings.QDRANT_COLLECTIONS:
        try:
            qdrant_client.get_collection(collection)
        except (ValueError, KeyError):
            qdrant_client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )


def embed_text(text: str) -> list[float]:
    """Generate embeddings for text."""
    try:
        embeddings = list(embedding_model.embed([text]))
        return embeddings[0] if embeddings else []
    except (RuntimeError, ValueError, IndexError) as e:
        print(f"Embedding generation failed: {e}")
        return []


async def store_paper(paper: dict, collection: str = "papers"):
    """Store a paper in the vector database."""
    initialize_collections()

    searchable_text = (
        f"{paper['title']} {paper.get('abstract', '')} "
        f"{' '.join(paper.get('authors', []))}"
    )

    embedding = embed_text(searchable_text)

    metadata = {
        "title": paper["title"],
        "authors": paper.get("authors", []),
        "abstract": paper.get("abstract", ""),
        "url": paper.get("url", ""),
        "year": paper.get("year"),
        "source": paper.get("source", "unknown"),
    }

    point_id = hash(paper["title"]) % 2**63

    qdrant_client.upsert(
        collection_name=collection,
        points=[{"id": point_id, "vector": embedding, "payload": metadata}],
    )


async def search_papers_semantic(
    query: str, limit: int = 10, collection: str = "papers"
) -> list[dict]:
    """Perform semantic search for papers."""
    initialize_collections()

    query_embedding = embed_text(query)

    search_results = qdrant_client.search(
        collection_name=collection, query_vector=query_embedding, limit=limit
    )

    results = []
    for hit in search_results:
        payload = hit.payload
        results.append(
            {
                "title": payload.get("title"),
                "authors": payload.get("authors", []),
                "abstract": payload.get("abstract"),
                "url": payload.get("url"),
                "year": payload.get("year"),
                "source": payload.get("source"),
                "score": hit.score,
            }
        )

    return results


async def store_search_history(query: str, results: list[dict]):
    """Store search history for analytics."""
    initialize_collections()

    history_data = {
        "query": query,
        "timestamp": None,  # TODO: Add timestamp
        "result_count": len(results),
        "top_result": results[0]["title"] if results else None,
    }

    embedding = embed_text(query)
    point_id = hash(f"{query}_{len(results)}") % 2**63

    qdrant_client.upsert(
        collection_name="search_history",
        points=[{"id": point_id, "vector": embedding, "payload": history_data}],
    )


async def store_citation(citation: dict):
    """Store citation information."""
    initialize_collections()

    citation_text = f"{citation['formatted']} {citation.get('paper_id', '')}"
    embedding = embed_text(citation_text)

    point_id = hash(citation["formatted"]) % 2**63

    qdrant_client.upsert(
        collection_name="citations",
        points=[{"id": point_id, "vector": embedding, "payload": citation}],
    )
