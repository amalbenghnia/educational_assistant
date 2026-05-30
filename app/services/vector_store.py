import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
from app.services.chunker import TextChunk
from app.services.embedder import embed_texts
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


@dataclass
class VectorStoreData:
    """
    Structure stockée sur disque pour persister l'index.
    On sauvegarde l'index FAISS ET les chunks originaux,
    car FAISS ne stocke que les vecteurs, pas le texte.
    """
    index: faiss.Index           # Index des vecteurs
    chunks: List[TextChunk]      # Textes originaux associés
    doc_id: str


def build_and_save(chunks: List[TextChunk], doc_id: str) -> VectorStoreData:
    """
    Vectorise tous les chunks et construit l'index FAISS.
    Sauvegarde l'index sur disque pour réutilisation.
    """
    logger.info(f"Construction du vectorstore pour doc_id={doc_id}")

    # Extraire les textes
    texts = [chunk.text for chunk in chunks]

    # Générer les embeddings (peut prendre quelques secondes)
    logger.info(f"Génération des embeddings pour {len(texts)} chunks...")
    embeddings = embed_texts(texts)

    # Dimension des vecteurs (384 pour MiniLM)
    dim = embeddings.shape[1]

    # Création de l'index FAISS
    # IndexFlatIP = recherche exacte par produit scalaire
    index = faiss.IndexFlatIP(dim)

    # Ajout des vecteurs dans l'index
    # IMPORTANT : les vecteurs doivent être float32
    index.add(embeddings.astype(np.float32))

    store = VectorStoreData(index=index, chunks=chunks, doc_id=doc_id)

    # Persistance sur disque
    save_path = settings.vectorstore_dir / doc_id
    save_path.mkdir(parents=True, exist_ok=True)

    # FAISS sauvegarde l'index dans son format binaire
    faiss.write_index(index, str(save_path / "index.faiss"))

    # Les chunks sont sauvegardés avec pickle
    # SÉCURITÉ : ne jamais charger des pickles de sources inconnues
    with open(save_path / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"Vectorstore sauvegardé : {save_path}")

    return store


def load_store(doc_id: str) -> VectorStoreData:
    """Charge un vectorstore existant depuis le disque."""
    load_path = settings.vectorstore_dir / doc_id

    if not load_path.exists():
        raise FileNotFoundError(f"Aucun vectorstore trouvé pour doc_id={doc_id}")

    index = faiss.read_index(str(load_path / "index.faiss"))

    with open(load_path / "chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    logger.info(f"Vectorstore chargé : {len(chunks)} chunks, doc_id={doc_id}")

    return VectorStoreData(index=index, chunks=chunks, doc_id=doc_id)


def search(
    store: VectorStoreData,
    query: str,
    top_k: int = None,
) -> List[Tuple[TextChunk, float]]:
    """
    Recherche sémantique : trouve les chunks les plus pertinents
    pour une question.

    ÉTAPES :
    1. Vectoriser la question (même modèle que les chunks)
    2. Comparer avec tous les vecteurs dans l'index FAISS
    3. Retourner les top_k plus proches avec leurs scores

    RETOUR : liste de (chunk, score) triée par pertinence décroissante
    Score entre 0 et 1 (cosine similarity normalisée)
    """
    k = top_k or settings.retriever_top_k

    # Vectoriser la question
    query_embedding = embed_texts([query])

    # Recherche FAISS
    # scores : similarités (plus grand = plus pertinent)
    # indices : position dans l'index
    scores, indices = store.index.search(
        query_embedding.astype(np.float32), k
    )

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:  # FAISS retourne -1 si pas assez de vecteurs
            continue
        results.append((store.chunks[idx], float(score)))

    return results