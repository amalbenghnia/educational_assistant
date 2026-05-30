import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PageContent:
    """Représente le contenu d'une page extraite."""
    page_number: int
    text: str
    char_count: int
@dataclass
class DocumentContent:
    """Représente le contenu complet d'un PDF extrait."""
    filename: str
    total_pages: int
    total_chars: int
    pages: List[PageContent]
    metadata: Dict


def extract_pdf(pdf_path: Path) -> DocumentContent:
    """
    Extrait le texte complet d'un PDF page par page.

    On garde la structure par pages car c'est utile pour :
    - Citer la source ("Réponse trouvée page 12")
    - Détecter les pages vides ou corrompues
    - Le débogage
    """
    logger.info(f"Extraction du PDF : {pdf_path.name}")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF introuvable : {pdf_path}")

    doc = fitz.open(str(pdf_path))
    pages = []
    total_chars = 0

    # Métadonnées du document
    metadata = {
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "total_pages": len(doc),
        "filename": pdf_path.name,
    }

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if len(text.strip()) < 20:
            logger.debug(f"Page {page_num + 1} ignorée (trop peu de texte)")
            continue
        page_content = PageContent(
            page_number=page_num + 1,
            text=text,
            char_count=len(text),
        )
        pages.append(page_content)
        total_chars += len(text)

    total_pages = len(doc)   # ← capture BEFORE close
    doc.close()

    logger.info(
        f"Extraction terminée : {len(pages)} pages utiles, "
        f"{total_chars} caractères"
    )

    return DocumentContent(
        filename=pdf_path.name,
        total_pages=total_pages,
        total_chars=total_chars,
        pages=pages,
        metadata=metadata,
    )