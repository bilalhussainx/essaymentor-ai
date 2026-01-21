"""
ChromaDB Manager - Vector database operations

EDUCATIONAL NOTE:
- ChromaDB stores documents with their embeddings
- Each document has: text, embedding, and metadata (tags, scores, etc.)
- We can search by semantic similarity (find similar essays)
- Data persists in ./chroma_db folder
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from vector_db.embeddings import EmbeddingGenerator
import os


class ChromaDBManager:
    """
    Manages essay storage and retrieval using ChromaDB.

    Collections in ChromaDB = like tables in SQL
    Documents = individual essays with embeddings
    Metadata = extra info (topic, score, author, etc.)
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Where to store the database on disk
        """
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        print(f"Initializing ChromaDB at: {persist_directory}")

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,  # Don't send usage data
                allow_reset=True
            )
        )

        # Initialize embedding generator
        self.embedding_gen = EmbeddingGenerator()

        # Create or get the essays collection
        self.collection = self.client.get_or_create_collection(
            name="successful_essays",
            metadata={"description": "High-quality college admission essays for RAG"}
        )

        print(f"ChromaDB initialized. Current essay count: {self.collection.count()}")

    def add_essay(
        self,
        essay_text: str,
        metadata: Dict[str, any],
        essay_id: Optional[str] = None
    ) -> str:
        """
        Add a single essay to the database.

        Args:
            essay_text: The full essay content
            metadata: Information about the essay
                     Example: {
                         'topic': 'coding journey',
                         'score': 9.0,
                         'word_count': 650,
                         'themes': ['perseverance', 'growth']
                     }
            essay_id: Optional custom ID (auto-generated if None)

        Returns:
            The essay ID

        Example:
            >>> manager = ChromaDBManager()
            >>> essay_id = manager.add_essay(
                    essay_text="I spent three days debugging...",
                    metadata={'topic': 'coding', 'score': 8.5}
                )
        """
        # Generate embedding
        print(f"Generating embedding for essay...")
        embedding = self.embedding_gen.generate_embedding(essay_text)

        # Auto-generate ID if not provided
        if essay_id is None:
            essay_id = f"essay_{self.collection.count() + 1}"

        # Convert list metadata to strings for ChromaDB compatibility
        processed_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                processed_metadata[key] = ", ".join(str(v) for v in value)
            else:
                processed_metadata[key] = value

        # Add to collection
        self.collection.add(
            documents=[essay_text],
            embeddings=[embedding],
            metadatas=[processed_metadata],
            ids=[essay_id]
        )

        print(f"Added essay: {essay_id}")
        return essay_id

    def add_essays_batch(
        self,
        essays: List[Dict[str, any]]
    ) -> List[str]:
        """
        Add multiple essays at once (faster than one-by-one).

        Args:
            essays: List of essay dictionaries
                    Example: [
                        {
                            'text': 'Essay content...',
                            'metadata': {'topic': 'coding', 'score': 8.5},
                            'id': 'optional_custom_id'
                        },
                        ...
                    ]

        Returns:
            List of essay IDs

        Example:
            >>> essays = [
                    {'text': 'Essay 1...', 'metadata': {'topic': 'coding'}},
                    {'text': 'Essay 2...', 'metadata': {'topic': 'sports'}}
                ]
            >>> ids = manager.add_essays_batch(essays)
        """
        texts = [e['text'] for e in essays]
        metadatas = []

        # Process metadata for ChromaDB compatibility
        for e in essays:
            processed = {}
            for key, value in e['metadata'].items():
                if isinstance(value, list):
                    processed[key] = ", ".join(str(v) for v in value)
                else:
                    processed[key] = value
            metadatas.append(processed)

        # Generate IDs
        ids = []
        for i, essay in enumerate(essays):
            if 'id' in essay and essay['id']:
                ids.append(essay['id'])
            else:
                ids.append(f"essay_{self.collection.count() + i + 1}")

        # Generate embeddings in batch (faster!)
        print(f"Generating embeddings for {len(texts)} essays...")
        embeddings = self.embedding_gen.generate_embeddings_batch(texts)

        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(texts)} essays to database")
        return ids

    def search_similar_essays(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Find essays similar to a query.

        This is the CORE RAG functionality!

        Args:
            query: What to search for
                   Examples:
                   - "coding journey and personal growth"
                   - "overcoming challenges in immigrant family"
                   - User's essay prompt
            n_results: How many similar essays to return
            filter_metadata: Optional filters
                           Example: {'topic': 'coding'}

        Returns:
            List of similar essays with scores
            Example: [
                {
                    'text': 'Essay content...',
                    'metadata': {'topic': 'coding', 'score': 9.0},
                    'similarity': 0.87,
                    'id': 'essay_5'
                },
                ...
            ]

        Example:
            >>> results = manager.search_similar_essays(
                    query="learning to code through challenges",
                    n_results=3
                )
            >>> for r in results:
                    print(f"Similarity: {r['similarity']:.2f}")
                    print(f"Topic: {r['metadata']['topic']}")
        """
        # Generate embedding for the query
        query_embedding = self.embedding_gen.generate_embedding(query)

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                })

        print(f"Found {len(formatted_results)} similar essays")
        return formatted_results

    def get_essay_by_id(self, essay_id: str) -> Optional[Dict]:
        """Get a specific essay by ID."""
        result = self.collection.get(ids=[essay_id])
        if result['ids']:
            return {
                'id': result['ids'][0],
                'text': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        return None

    def get_all_essays(self) -> List[Dict]:
        """Get all essays in the database."""
        result = self.collection.get()
        essays = []
        for i in range(len(result['ids'])):
            essays.append({
                'id': result['ids'][i],
                'text': result['documents'][i],
                'metadata': result['metadatas'][i]
            })
        return essays

    def delete_essay(self, essay_id: str):
        """Delete an essay by ID."""
        self.collection.delete(ids=[essay_id])
        print(f"Deleted essay: {essay_id}")

    def clear_all_essays(self):
        """Delete ALL essays (use with caution!)."""
        count = self.collection.count()
        self.client.delete_collection("successful_essays")
        self.collection = self.client.create_collection(
            name="successful_essays",
            metadata={"description": "High-quality college admission essays for RAG"}
        )
        print(f"Cleared {count} essays from database")

    def get_stats(self) -> Dict:
        """Get database statistics."""
        essays = self.get_all_essays()
        topics = {}
        scores = []

        for essay in essays:
            topic = essay['metadata'].get('topic', 'unknown')
            topics[topic] = topics.get(topic, 0) + 1

            score = essay['metadata'].get('score')
            if score is not None:
                try:
                    scores.append(float(score))
                except (ValueError, TypeError):
                    pass

        return {
            'total_essays': len(essays),
            'topics': topics,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'score_range': (min(scores), max(scores)) if scores else (0, 0)
        }


def demonstrate_chromadb():
    """
    Run this to understand how ChromaDB works.

    Usage:
        python -m vector_db.chromadb_manager
    """
    print("\n=== CHROMADB DEMONSTRATION ===\n")

    # Initialize
    manager = ChromaDBManager(persist_directory="./demo_chroma_db")

    # Add some sample essays
    print("\n1. Adding sample essays...\n")
    essays = [
        {
            'text': "I spent three days debugging a single line of code. That frustration taught me perseverance and systematic thinking that changed how I approach all challenges.",
            'metadata': {'topic': 'coding', 'score': 8.5, 'theme': 'perseverance'}
        },
        {
            'text': "Building an app for my grandmother who spoke only Mandarin showed me how technology can bridge cultural gaps and connect generations.",
            'metadata': {'topic': 'coding', 'score': 9.0, 'theme': 'empathy'}
        },
        {
            'text': "Moving to America at age 12 without speaking English, I learned to code as a universal language that transcended my communication barriers.",
            'metadata': {'topic': 'immigration', 'score': 8.7, 'theme': 'resilience'}
        },
        {
            'text': "My first marathon taught me that success isn't about speed, but about consistent effort and refusing to quit even when every muscle screams stop.",
            'metadata': {'topic': 'sports', 'score': 8.3, 'theme': 'perseverance'}
        }
    ]

    manager.add_essays_batch(essays)

    # Search for similar essays
    print("\n2. Searching for essays about 'learning to code through difficulties'...\n")
    results = manager.search_similar_essays(
        query="learning to code through difficulties",
        n_results=3
    )

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Similarity: {result['similarity']:.3f}")
        print(f"  Topic: {result['metadata']['topic']}")
        print(f"  Theme: {result['metadata']['theme']}")
        print(f"  Score: {result['metadata']['score']}")
        print(f"  Text preview: {result['text'][:100]}...")
        print()

    # Show stats
    print("3. Database statistics:\n")
    stats = manager.get_stats()
    print(f"  Total essays: {stats['total_essays']}")
    print(f"  Topics: {stats['topics']}")
    print(f"  Average score: {stats['average_score']:.2f}")

    print("\nDemonstration complete!")
    print(f"  Database stored at: ./demo_chroma_db")
    print(f"  (You can delete this demo folder after testing)")


if __name__ == "__main__":
    demonstrate_chromadb()
