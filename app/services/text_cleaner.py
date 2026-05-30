import re
from app.services.pdf_parser import DocumentContent, PageContent
from app.core.logger import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """
    Nettoie un bloc de texte.
    Chaque étape est documentée pour que tu comprennes le POURQUOI.
    """
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^\s*[-–]?\s*\d+\s*[-–]?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[Pp]age\s+\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text.strip()
def clean_document(doc: DocumentContent) -> DocumentContent:
    """Nettoie toutes les pages d'un document."""
    logger.info(f"Nettoyage du document : {doc.filename}")

    cleaned_pages = []
    for page in doc.pages:
        cleaned = clean_text(page.text)
        if len(cleaned) > 50:
            cleaned_pages.append(PageContent(
                page_number=page.page_number,
                text=cleaned,
                char_count=len(cleaned),
            ))
    logger.info(
        f"Nettoyage terminé : {len(cleaned_pages)}/{len(doc.pages)} "
        f"pages conservées"
    )
    return DocumentContent(
        filename=doc.filename,
        total_pages=doc.total_pages,
        total_chars=sum(p.char_count for p in cleaned_pages),
        pages=cleaned_pages,
        metadata=doc.metadata,
    )



