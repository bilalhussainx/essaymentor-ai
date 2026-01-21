"""
RAG System Test Script
Tests all components of the RAG system for EssayMentor AI

Run with: python test_rag_system.py
"""

import sys
import time
from pathlib import Path


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_success(msg: str):
    print(f"[OK] {msg}")


def print_error(msg: str):
    print(f"[ERROR] {msg}")


def print_info(msg: str):
    print(f"[INFO] {msg}")


def test_imports():
    """Test that all modules can be imported."""
    print_header("TEST 1: Import Modules")

    try:
        from vector_db.embeddings import EmbeddingGenerator
        print_success("vector_db.embeddings imported")
    except Exception as e:
        print_error(f"Failed to import embeddings: {e}")
        return False

    try:
        from vector_db.chromadb_manager import ChromaDBManager
        print_success("vector_db.chromadb_manager imported")
    except Exception as e:
        print_error(f"Failed to import chromadb_manager: {e}")
        return False

    try:
        from vector_db.sample_loader import SampleEssayLoader
        print_success("vector_db.sample_loader imported")
    except Exception as e:
        print_error(f"Failed to import sample_loader: {e}")
        return False

    try:
        from agents.rag_retrieval_agent import rag_retrieval_agent
        print_success("agents.rag_retrieval_agent imported")
    except Exception as e:
        print_error(f"Failed to import rag_retrieval_agent: {e}")
        return False

    return True


def test_embeddings():
    """Test embedding generation."""
    print_header("TEST 2: Embedding Generation")

    from vector_db.embeddings import EmbeddingGenerator

    print_info("Loading embedding model (first time downloads ~80MB)...")
    start = time.time()
    gen = EmbeddingGenerator()
    load_time = time.time() - start
    print_success(f"Model loaded in {load_time:.2f}s")

    # Test single embedding
    text = "I learned to code by building a video game"
    start = time.time()
    embedding = gen.generate_embedding(text)
    embed_time = time.time() - start

    print_success(f"Generated embedding: {len(embedding)} dimensions in {embed_time:.3f}s")
    print_info(f"First 5 values: {embedding[:5]}")

    # Test similarity
    texts = [
        "I learned programming through game development",  # Similar
        "My coding journey started with making games",     # Similar
        "I enjoy playing basketball with friends",         # Different
    ]

    print_info("\nTesting semantic similarity:")
    base_embedding = embedding

    for t in texts:
        t_embedding = gen.generate_embedding(t)
        similarity = gen.compute_similarity(base_embedding, t_embedding)
        print(f"  '{t[:40]}...' -> {similarity:.3f}")

    return True


def test_chromadb():
    """Test ChromaDB operations."""
    print_header("TEST 3: ChromaDB Operations")

    from vector_db.chromadb_manager import ChromaDBManager

    # Use test directory
    test_dir = "./test_chroma_db"
    print_info(f"Using test database at: {test_dir}")

    manager = ChromaDBManager(persist_directory=test_dir)

    # Clear any existing test data
    manager.clear_all_essays()
    print_success("Database cleared")

    # Add test essays
    test_essays = [
        {
            'text': "I spent three days debugging a single line of code. That frustration taught me perseverance.",
            'metadata': {'topic': 'coding', 'score': 8.5, 'student': 'Test1'}
        },
        {
            'text': "Moving to America at age 12 without speaking English, I found code to be a universal language.",
            'metadata': {'topic': 'immigration', 'score': 9.0, 'student': 'Test2'}
        },
        {
            'text': "Leading the robotics team taught me that great ideas come from collaboration, not competition.",
            'metadata': {'topic': 'leadership', 'score': 8.7, 'student': 'Test3'}
        },
    ]

    print_info("Adding 3 test essays...")
    manager.add_essays_batch(test_essays)
    print_success(f"Added essays. Total count: {manager.collection.count()}")

    # Test search
    print_info("\nSearching for 'programming challenges and learning'...")
    results = manager.search_similar_essays(
        query="programming challenges and learning to code",
        n_results=3
    )

    print_success(f"Found {len(results)} results:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['metadata']['topic']}] Similarity: {r['similarity']:.3f}")
        print(f"     {r['text'][:60]}...")

    # Clean up test database
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print_success("Test database cleaned up")

    return True


def test_sample_loader():
    """Test loading essays from data/essay_suites."""
    print_header("TEST 4: Sample Essay Loader")

    from vector_db.sample_loader import SampleEssayLoader, parse_essay_file
    from pathlib import Path

    essay_dir = Path("./data/essay_suites")

    if not essay_dir.exists():
        print_error(f"Essay directory not found: {essay_dir}")
        return False

    # Count available essays
    suite_dirs = [d for d in essay_dir.iterdir() if d.is_dir()]
    print_success(f"Found {len(suite_dirs)} essay suites")

    # Test parsing one essay
    sample_suite = suite_dirs[0]
    essay_files = list(sample_suite.glob("*.md"))

    if essay_files:
        print_info(f"\nParsing sample essay: {essay_files[0].name}")
        parsed = parse_essay_file(essay_files[0])
        if parsed:
            print_success(f"Parsed successfully")
            print_info(f"  Metadata: {parsed['metadata']}")
            print_info(f"  Text length: {len(parsed['text'])} chars")
        else:
            print_error("Failed to parse essay")

    return True


def test_database_population():
    """Populate the main database with essays."""
    print_header("TEST 5: Populate Main Database")

    from vector_db.sample_loader import SampleEssayLoader

    print_info("Loading essays into main database...")
    print_info("(This may take a few minutes on first run)")

    loader = SampleEssayLoader()

    # Check current count
    current_count = loader.db_manager.collection.count()
    print_info(f"Current essays in database: {current_count}")

    if current_count == 0:
        print_info("Database empty, populating...")
        loader.populate_database(clear_existing=False)
    else:
        print_success(f"Database already has {current_count} essays")

    # Show stats
    stats = loader.db_manager.get_stats()
    print_success(f"\nDatabase Statistics:")
    print(f"  Total essays: {stats['total_essays']}")
    print(f"  Topics: {stats['topics']}")
    print(f"  Average score: {stats['average_score']:.2f}")

    return True


def test_rag_retrieval():
    """Test the RAG retrieval agent."""
    print_header("TEST 6: RAG Retrieval Agent")

    from agents.rag_retrieval_agent import (
        rag_retrieval_agent,
        create_search_query,
        format_retrieved_essays
    )

    # Create test state
    test_state = {
        'prompt': "Write about how learning to code changed your perspective on problem-solving",
        'student_profile': {
            'name': 'Test Student',
            'background': 'First-generation college student passionate about technology',
            'interests': {'academic': 'Computer Science', 'personal': 'Building apps'}
        },
        'target_university': 'MIT',
        'profile_analysis': 'Student has strong technical background with focus on coding',
        'current_agent': 'rag'
    }

    # Test query creation
    query = create_search_query(test_state)
    print_info(f"Generated search query: {query[:100]}...")

    # Run retrieval
    print_info("\nRunning RAG retrieval...")
    result = rag_retrieval_agent(test_state)

    retrieved = result.get('retrieved_essays', [])
    print_success(f"Retrieved {len(retrieved)} essays")

    if retrieved:
        print_info("\nRetrieved essays:")
        for i, essay in enumerate(retrieved, 1):
            meta = essay.get('metadata', {})
            print(f"  {i}. {meta.get('student', 'Unknown')} - {meta.get('university', 'N/A')}")
            print(f"     Topic: {meta.get('topic', 'N/A')}, Score: {meta.get('score', 'N/A')}")
            print(f"     Similarity: {essay.get('similarity', 0):.3f}")
            print(f"     Preview: {essay['text'][:80]}...")
            print()

    # Check RAG context was generated
    rag_context = result.get('rag_context', '')
    if rag_context:
        print_success(f"RAG context generated: {len(rag_context)} chars")
        print_info(f"Context preview:\n{rag_context[:300]}...")

    return True


def test_search_queries():
    """Test various search queries."""
    print_header("TEST 7: Search Query Variations")

    from vector_db.chromadb_manager import ChromaDBManager

    manager = ChromaDBManager()

    queries = [
        "coding journey and debugging challenges",
        "immigrant experience adapting to new culture",
        "leadership and team collaboration",
        "overcoming failure and personal growth",
        "passion for science and research",
    ]

    print_info(f"Testing {len(queries)} different queries:\n")

    for query in queries:
        print(f"Query: '{query}'")
        results = manager.search_similar_essays(query, n_results=2)

        if results:
            for r in results:
                meta = r.get('metadata', {})
                print(f"  -> [{meta.get('topic', 'N/A')}] {meta.get('student', 'Unknown')}: {r['similarity']:.3f}")
        else:
            print("  -> No results found")
        print()

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" RAG SYSTEM TEST SUITE")
    print(" EssayMentor AI")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Embeddings", test_embeddings),
        ("ChromaDB", test_chromadb),
        ("Sample Loader", test_sample_loader),
        ("Database Population", test_database_population),
        ("RAG Retrieval", test_rag_retrieval),
        ("Search Queries", test_search_queries),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, s in results if s)
    total = len(results)

    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  All tests passed! RAG system is ready.")
    else:
        print("\n  Some tests failed. Check the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
