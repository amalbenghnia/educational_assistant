from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)
_embedding_model: SentenceTransformer = None


def get_embedding_model() -> SentenceTransformer:
    """
    Pattern Singleton : charge le modèle une seule fois.

    Premier appel : télécharge (~80MB) et charge en mémoire.
    Appels suivants : retourne l'instance déjà en mémoire.
    ALTERNATIVES À TESTER (changer dans .env) :
    - "BAAI/bge-small-en-v1.5"              → meilleur anglais
    - "intfloat/multilingual-e5-small"       → FR/AR/EN gratuit
    - "paraphrase-multilingual-MiniLM-L12-v2" → multilingue
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Chargement du modèle d'embedding : {settings.embedding_model}")
        _embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info("Modèle d'embedding chargé")
    return _embedding_model
def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Transforme une liste de textes en matrice de vecteurs.

    Entrée  : ["texte1", "texte2", ...] de longueur N
    Sortie  : matrice numpy de forme (N, 384)

    PARAMÈTRE batch_size :
    Traite les textes par lots de 32 pour ne pas saturer la RAM.
    EXPÉRIMENTE : augmente à 64 ou 128 si tu as plus de RAM.

    PARAMÈTRE show_progress_bar :
    Utile pour des milliers de chunks, désactivé ici pour l'API.
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,  # Normalise pour cosine similarity
    )
    return embeddings