"""
Vector Database Module for EssayMentor AI RAG System

This module provides:
- EmbeddingGenerator: Convert text to numerical vectors
- ChromaDBManager: Store and search essays by semantic similarity
- SampleEssayLoader: Load sample essays into the database

Usage:
    from vector_db import ChromaDBManager, EmbeddingGenerator

    # Initialize
    db = ChromaDBManager()

    # Add essays
    db.add_essay("Essay text...", metadata={'topic': 'coding', 'score': 8.5})

    # Search similar
    results = db.search_similar_essays("coding journey", n_results=5)
"""

from vector_db.embeddings import EmbeddingGenerator
from vector_db.chromadb_manager import ChromaDBManager
from vector_db.sample_loader import SampleEssayLoader

__all__ = ['EmbeddingGenerator', 'ChromaDBManager', 'SampleEssayLoader']
