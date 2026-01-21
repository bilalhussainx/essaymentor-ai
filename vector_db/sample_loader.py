"""
Sample Essay Loader - Populate ChromaDB with essays from data/essay_suites

EDUCATIONAL NOTE:
- This script loads essays from data/essay_suites/ folder
- Each essay gets embedded and stored in ChromaDB
- Metadata from YAML frontmatter and profile.json helps with searching
- Run once to populate the database, then it persists
"""

import os
import json
import re
from pathlib import Path
from vector_db.chromadb_manager import ChromaDBManager
from typing import List, Dict, Optional


def parse_essay_file(file_path: Path) -> Optional[Dict]:
    """
    Parse an essay markdown file with YAML frontmatter.

    Expected format:
    ---
    student: Maya Chen
    sat_verbal: 800
    university: MIT
    type: common_app
    words: 639
    ---

    **Title**

    Essay content...
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)

    if not frontmatter_match:
        return None

    frontmatter_text = frontmatter_match.group(1)
    essay_text = frontmatter_match.group(2).strip()

    # Parse frontmatter manually (simple key: value format)
    metadata = {}
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Try to convert to int
            try:
                value = int(value)
            except ValueError:
                pass
            metadata[key] = value

    return {
        'metadata': metadata,
        'text': essay_text
    }


class SampleEssayLoader:
    """
    Loads essays from data/essay_suites/ into the vector database.
    """

    def __init__(self, essay_suites_dir: str = "./data/essay_suites"):
        self.essay_suites_dir = Path(essay_suites_dir)
        self.db_manager = ChromaDBManager()

    def load_profile(self, suite_dir: Path) -> Dict:
        """Load the profile.json from an essay suite directory."""
        profile_path = suite_dir / "profile.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def extract_themes_from_profile(self, profile: Dict) -> List[str]:
        """Extract themes from profile for metadata."""
        themes = []

        # From experiences
        for exp in profile.get('experiences', []):
            themes.extend(exp.get('skills_developed', []))

        # From voice characteristics
        voice = profile.get('voice_characteristics', {})
        if 'distinguishing_elements' in voice:
            themes.extend(voice['distinguishing_elements'][:2])

        # Limit to top themes
        return list(set(themes))[:5]

    def load_essay_with_metadata(self, essay_path: Path, profile: Dict) -> Optional[Dict]:
        """
        Load an essay and combine with profile metadata.

        Returns:
            Dictionary with 'text', 'metadata', 'id'
        """
        parsed = parse_essay_file(essay_path)
        if not parsed:
            return None

        essay_text = parsed['text']
        frontmatter = parsed['metadata']

        # Build comprehensive metadata
        metadata = {
            'student': frontmatter.get('student', 'Unknown'),
            'university': frontmatter.get('university', 'Generic'),
            'essay_type': frontmatter.get('type', 'common_app'),
            'word_count': frontmatter.get('words', len(essay_text.split())),
            'sat_verbal': frontmatter.get('sat_verbal', 0),
            'filename': essay_path.name,
            'suite_id': essay_path.parent.name,
        }

        # Add profile info (flatten nested dicts to strings)
        background = profile.get('background', {})
        if isinstance(background, dict):
            metadata['demographics'] = str(background.get('demographics', ''))
            metadata['location'] = str(background.get('location', ''))
        else:
            metadata['demographics'] = ''
            metadata['location'] = ''

        # Add themes
        themes = self.extract_themes_from_profile(profile)
        metadata['themes'] = ', '.join(themes) if themes else 'general'

        # Determine topic from essay type and content
        essay_type = frontmatter.get('type', 'common_app')
        if 'tech' in essay_text.lower() or 'code' in essay_text.lower() or 'program' in essay_text.lower():
            metadata['topic'] = 'coding'
        elif 'immigra' in essay_text.lower() or 'parents' in essay_text.lower():
            metadata['topic'] = 'immigration'
        elif 'leader' in essay_text.lower() or 'team' in essay_text.lower():
            metadata['topic'] = 'leadership'
        else:
            metadata['topic'] = 'personal_growth'

        # Score based on SAT verbal (proxy for essay quality in this dataset)
        sat = metadata.get('sat_verbal', 700)
        if sat >= 780:
            metadata['score'] = 9.0
        elif sat >= 750:
            metadata['score'] = 8.5
        elif sat >= 700:
            metadata['score'] = 8.0
        else:
            metadata['score'] = 7.5

        # Create unique ID
        essay_id = f"{essay_path.parent.name}_{essay_path.stem}"

        return {
            'text': essay_text,
            'metadata': metadata,
            'id': essay_id
        }

    def load_all_essays(self) -> List[Dict]:
        """
        Load all essays from data/essay_suites/ directory.

        Returns:
            List of essay dictionaries
        """
        print(f"\nLoading essays from: {self.essay_suites_dir}\n")

        if not self.essay_suites_dir.exists():
            print(f"Directory not found: {self.essay_suites_dir}")
            return []

        essays = []
        suite_dirs = [d for d in self.essay_suites_dir.iterdir() if d.is_dir()]

        print(f"Found {len(suite_dirs)} essay suites\n")

        for suite_dir in suite_dirs:
            # Load profile for this suite
            profile = self.load_profile(suite_dir)

            # Find all essay files
            essay_files = list(suite_dir.glob("*.md"))

            for essay_file in essay_files:
                essay_data = self.load_essay_with_metadata(essay_file, profile)
                if essay_data:
                    essays.append(essay_data)
                    print(f"  Loaded: {essay_data['id']}")

        print(f"\nLoaded {len(essays)} essays successfully")
        return essays

    def populate_database(self, clear_existing: bool = False):
        """
        Load all essays from essay_suites into ChromaDB.

        Args:
            clear_existing: If True, clear database before loading
        """
        print("\n=== POPULATING VECTOR DATABASE ===\n")

        # Clear if requested
        if clear_existing:
            print("Clearing existing essays...")
            self.db_manager.clear_all_essays()

        # Load essays
        essays = self.load_all_essays()

        if not essays:
            print("\nNo essays to load. Exiting.")
            return

        # Add to database in batches
        batch_size = 20
        print(f"\nAdding {len(essays)} essays to ChromaDB (in batches of {batch_size})...")

        for i in range(0, len(essays), batch_size):
            batch = essays[i:i + batch_size]
            self.db_manager.add_essays_batch(batch)
            print(f"  Added batch {i // batch_size + 1}/{(len(essays) - 1) // batch_size + 1}")

        # Show stats
        print("\n=== DATABASE STATISTICS ===\n")
        stats = self.db_manager.get_stats()
        print(f"Total essays: {stats['total_essays']}")
        print(f"Topics: {stats['topics']}")
        print(f"Average score: {stats['average_score']:.2f}")
        print(f"Score range: {stats['score_range']}")

        print("\nDatabase populated successfully!")

    def test_search(self):
        """
        Test the search functionality with example queries.
        """
        print("\n=== TESTING SEARCH FUNCTIONALITY ===\n")

        test_queries = [
            "coding journey and debugging challenges",
            "immigrant experience and family sacrifice",
            "leadership and community impact",
            "overcoming obstacles through determination",
            "technology and social equity"
        ]

        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 60)

            results = self.db_manager.search_similar_essays(
                query=query,
                n_results=3
            )

            for i, result in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"    Similarity: {result['similarity']:.3f}")
                print(f"    Student: {result['metadata'].get('student', 'N/A')}")
                print(f"    University: {result['metadata'].get('university', 'N/A')}")
                print(f"    Topic: {result['metadata'].get('topic', 'N/A')}")
                print(f"    Score: {result['metadata'].get('score', 'N/A')}")
                print(f"    Preview: {result['text'][:100]}...")

        print("\nSearch test complete!")


def main():
    """
    Main function - loads essays from essay_suites and tests search.

    Usage:
        # Load all essays into database
        python -m vector_db.sample_loader

        # Clear existing and reload
        python -m vector_db.sample_loader --clear
    """
    import sys

    clear_existing = '--clear' in sys.argv

    loader = SampleEssayLoader()
    loader.populate_database(clear_existing=clear_existing)
    loader.test_search()

    print("\n" + "=" * 60)
    print("DATABASE READY FOR RAG!")
    print("=" * 60)
    print("\nYou can now use the vector database in your agents.")
    print("The database persists at: ./chroma_db")


if __name__ == "__main__":
    main()
