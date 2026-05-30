from typing import List
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.pdf_parser import DocumentContent
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


@dataclass
class TextChunk:
    """
    Un chunk = unité atomique du RAG.
    Les métadonnées sont CRUCIALES : elles permettent de citer
    la source exacte dans la réponse finale.
    """
    chunk_id: str           # Identifiant unique
    text: str               # Contenu textuel
    source_file: str        # Nom du PDF d'origine
    page_number: int        # Page d'origine (pour citations)
    chunk_index: int        # Index dans la séquence
    total_chunks: int       # Total de chunks du document
    char_count: int         # Taille en caractères


def chunk_document(doc: DocumentContent) -> List[TextChunk]:
    """
    Découpe un document en chunks avec leurs métadonnées.

    ON DÉCOUPE PAR PAGE, pas le document entier d'un coup.
    Avantage : on conserve le numéro de page pour les citations.
    """
    logger.info(f"Découpage du document : {doc.filename}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )

    all_chunks: List[TextChunk] = []
    chunk_index = 0

    for page in doc.pages:
        # Découpage de la page en sous-chunks
        sub_chunks = splitter.split_text(page.text)

        for sub_text in sub_chunks:
            if len(sub_text.strip()) < 30:
                # Ignorer les micro-chunks sans valeur
                continue

            chunk = TextChunk(
                chunk_id=f"{doc.filename}_{chunk_index:04d}",
                text=sub_text.strip(),
                source_file=doc.filename,
                page_number=page.page_number,
                chunk_index=chunk_index,
                total_chunks=0,  # mis à jour après
                char_count=len(sub_text),
            )
            all_chunks.append(chunk)
            chunk_index += 1

    # Mise à jour du total_chunks maintenant qu'on connaît le total
    for chunk in all_chunks:
        chunk.total_chunks = len(all_chunks)

    logger.info(
        f"Découpage terminé : {len(all_chunks)} chunks créés "
        f"(taille moyenne : {sum(c.char_count for c in all_chunks) // max(len(all_chunks), 1)} chars)"
    )

    return all_chunks