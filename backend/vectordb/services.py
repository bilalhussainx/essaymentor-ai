"""
Vector database service wrapper.

Wraps the existing vector_db/chromadb_manager.py for Django integration.
"""

import os
import sys
from typing import List, Dict, Optional
from django.conf import settings

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class VectorDBService:
    """
    Singleton service for ChromaDB operations.

    Wraps the existing ChromaDBManager for use in Django views.
    """

    _instance = None
    _manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._manager is None:
            from vector_db.chromadb_manager import ChromaDBManager
            persist_dir = getattr(settings, 'CHROMADB_PATH', './chroma_db')
            self._manager = ChromaDBManager(persist_directory=persist_dir)

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        min_score: float = 7.5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar essays in the vector database.

        Args:
            query: Search query text
            n_results: Number of results to return
            min_score: Minimum essay quality score (0-10)
            filter_metadata: Optional metadata filters

        Returns:
            List of essay dictionaries with text, metadata, and similarity
        """
        # Get more results than needed to filter by score
        results = self._manager.search_similar_essays(
            query=query,
            n_results=n_results * 2,
            filter_metadata=filter_metadata
        )

        # Filter by minimum score
        filtered = [
            r for r in results
            if r.get('metadata', {}).get('score', 0) >= min_score
        ][:n_results]

        return filtered

    def get_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with total_essays, topics, average_score, etc.
        """
        return self._manager.get_stats()

    def add_essay(self, text: str, metadata: Dict) -> str:
        """
        Add a new essay to the database.

        Args:
            text: Essay text content
            metadata: Essay metadata (topic, score, university, etc.)

        Returns:
            Essay ID
        """
        return self._manager.add_essay(text, metadata)

    def get_essay_by_id(self, essay_id: str) -> Optional[Dict]:
        """
        Get an essay by its ID.

        Args:
            essay_id: Essay identifier

        Returns:
            Essay dictionary or None
        """
        return self._manager.get_essay_by_id(essay_id)


# Create singleton instance
vectordb_service = VectorDBService()


def get_vectordb_service() -> VectorDBService:
    """Get the singleton VectorDBService instance."""
    return vectordb_service
