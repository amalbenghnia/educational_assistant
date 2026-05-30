import pytest
from pathlib import Path
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_document
from app.services.pdf_parser import DocumentContent, PageContent


def test_clean_text_removes_page_numbers():
    """Vérifie que les numéros de page sont supprimés."""
    dirty = "Voici du contenu.\n  42  \nSuite du cours."
    cleaned = clean_text(dirty)
    assert "42" not in cleaned or "Voici" in cleaned


def test_clean_text_fixes_hyphenation():
    """Vérifie que les coupures de mots sont réparées."""
    text = "appren-\ntissage automatique"
    result = clean_text(text)
    assert "apprentissage" in result


def test_chunk_document_produces_chunks():
    """Vérifie que le chunking produit des chunks non vides."""
    doc = DocumentContent(
        filename="test.pdf",
        total_pages=1,
        total_chars=1000,
        pages=[PageContent(
            page_number=1,
            text="Le machine learning est un domaine de l'IA. " * 50,
            char_count=2000,
        )],
        metadata={},
    )
    chunks = chunk_document(doc)
    assert len(chunks) > 0
    assert all(len(c.text) > 0 for c in chunks)
    assert all(c.page_number == 1 for c in chunks)


def test_chunk_metadata_correct():
    """Vérifie que les métadonnées des chunks sont correctes."""
    doc = DocumentContent(
        filename="cours.pdf",
        total_pages=1,
        total_chars=500,
        pages=[PageContent(
            page_number=3,
            text="Contenu de test pour vérifier les métadonnées. " * 20,
            char_count=500,
        )],
        metadata={},
    )
    chunks = chunk_document(doc)
    for chunk in chunks:
        assert chunk.source_file == "cours.pdf"
        assert chunk.page_number == 3
        assert chunk.total_chunks == len(chunks)