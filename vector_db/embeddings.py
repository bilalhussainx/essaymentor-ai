"""
Embeddings Module - Converts text to numerical vectors

EDUCATIONAL NOTE:
- Embeddings are arrays of numbers (usually 384 or 768 dimensions)
- Similar text -> similar numbers
- Example: "coding journey" and "programming experience" have similar embeddings
- We use sentence-transformers (free, local, fast)
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingGenerator:
    """
    Generates embeddings using sentence-transformers.

    Model: 'all-MiniLM-L6-v2'
    - 384 dimensions
    - Fast (runs on CPU fine)
    - Good quality for semantic similarity
    - ~80MB download (one-time)
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding model.

        Args:
            model_name: HuggingFace model name
                       'all-MiniLM-L6-v2' = fast, good quality (RECOMMENDED)
                       'all-mpnet-base-v2' = slower, better quality
        """
        print(f"Loading embedding model: {model_name}")
        print("(First time will download ~80MB model)")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Convert a single text into an embedding.

        Args:
            text: The text to embed (essay, query, etc.)

        Returns:
            List of 384 floats representing the text's meaning

        Example:
            >>> gen = EmbeddingGenerator()
            >>> embedding = gen.generate_embedding("I love coding")
            >>> print(len(embedding))  # 384
            >>> print(embedding[:5])    # [0.234, -0.123, 0.456, ...]
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple texts into embeddings (faster than one-by-one).

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings, same order as input

        Example:
            >>> texts = ["essay 1", "essay 2", "essay 3"]
            >>> embeddings = gen.generate_embeddings_batch(texts)
            >>> len(embeddings)  # 3
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return [emb.tolist() for emb in embeddings]

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate similarity between two embeddings (0 to 1).

        Uses cosine similarity:
        - 1.0 = identical meaning
        - 0.5 = somewhat similar
        - 0.0 = completely different

        Args:
            embedding1, embedding2: The embeddings to compare

        Returns:
            Similarity score (0.0 to 1.0)

        Example:
            >>> emb1 = gen.generate_embedding("I love programming")
            >>> emb2 = gen.generate_embedding("I enjoy coding")
            >>> similarity = gen.compute_similarity(emb1, emb2)
            >>> print(similarity)  # 0.87 (very similar!)
        """
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)

        # Cosine similarity formula
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


def demonstrate_embeddings():
    """
    Run this to understand how embeddings work.

    Usage:
        python -m vector_db.embeddings
    """
    print("\n=== EMBEDDINGS DEMONSTRATION ===\n")

    gen = EmbeddingGenerator()

    # Example texts
    texts = [
        "I learned to code by building a game",
        "My programming journey started with a video game project",
        "I studied mathematics in college",
        "I enjoy playing basketball"
    ]

    print("\nGenerating embeddings for 4 texts...\n")
    embeddings = gen.generate_embeddings_batch(texts)

    print("Comparing similarities:\n")

    # Compare similar texts (1 and 2 are about coding)
    sim_12 = gen.compute_similarity(embeddings[0], embeddings[1])
    print(f"Text 1 vs Text 2 (both about coding): {sim_12:.3f} <- HIGH similarity")

    # Compare different texts (1 and 3)
    sim_13 = gen.compute_similarity(embeddings[0], embeddings[2])
    print(f"Text 1 vs Text 3 (coding vs math):    {sim_13:.3f}")

    # Compare very different texts (1 and 4)
    sim_14 = gen.compute_similarity(embeddings[0], embeddings[3])
    print(f"Text 1 vs Text 4 (coding vs sports):  {sim_14:.3f} <- LOW similarity")

    print("\nThis is how we find 'similar' essays - by embedding similarity!")


if __name__ == "__main__":
    demonstrate_embeddings()
