from typing import List, Tuple
from app.services.vector_store import VectorStoreData, search
from app.services.chunker import TextChunk
from app.core.config import get_settings

settings = get_settings()


def retrieve(
    store: VectorStoreData,
    query: str,
    top_k: int = None,
) -> List[Tuple[TextChunk, float]]:
    """Récupère les chunks les plus pertinents pour une question dans un vector store."""
    results = search(store, query, top_k)

    MIN_SCORE = 0.3
    filtered = [(chunk, score) for chunk, score in results if score >= MIN_SCORE]

    # Si trop de filtrages, garder au moins 2 résultats
    if len(filtered) < 2:
        filtered = results[:2]

    return filtered


def retrieve_multi(
    stores: List[VectorStoreData],
    query: str,
    top_k: int = None,
) -> List[Tuple[TextChunk, float]]:
    """
    Récupère les chunks les plus pertinents à travers plusieurs vector stores.
    Trie et fusionne les résultats par score de pertinence décroissante.
    """
    k = top_k or settings.retriever_top_k
    all_results = []

    for store in stores:
        try:
            results = search(store, query, top_k=k)
            all_results.extend(results)
        except Exception:
            continue

    # Filtrer par pertinence
    MIN_SCORE = 0.3
    filtered = [(chunk, score) for chunk, score in all_results if score >= MIN_SCORE]

    if len(filtered) < 2:
        filtered = all_results

    # Trier par score décroissant et garder le top_k
    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered[:k]


def format_context(results: List[Tuple[TextChunk, float]]) -> str:
    """
    Formate les chunks récupérés en bloc de contexte.
    Ce contexte sera injecté dans le prompt du LLM.
    Le format indique la provenance du chunk (Fichier + Page) pour la citation.
    """
    parts = []
    for i, (chunk, score) in enumerate(results, 1):
        parts.append(
            f"[EXTRAIT {i} | Fichier: {chunk.source_file} | "
            f"Page: {chunk.page_number} | Pertinence: {score:.2f}]\n"
            f"{chunk.text}"
        )

    return "\n\n---\n\n".join(parts)