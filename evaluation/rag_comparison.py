"""
RAG Evaluation - Compare essay quality with and without RAG

EDUCATIONAL NOTE:
- Tests same prompts with RAG ON vs RAG OFF
- Measures quality using objective rubric
- Quantifies the improvement RAG provides
- Helps validate that RAG actually works
"""

import sys
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class RAGEvaluator:
    """
    Evaluates the impact of RAG on essay quality.
    """

    def __init__(self):
        self.rubric = {
            'authenticity': {
                'weight': 0.25,
                'description': 'Unique voice, specific details, genuine emotion'
            },
            'structure': {
                'weight': 0.20,
                'description': 'Clear narrative arc, logical flow, good pacing'
            },
            'insight': {
                'weight': 0.25,
                'description': 'Demonstrates growth, reflection, self-awareness'
            },
            'engagement': {
                'weight': 0.15,
                'description': 'Compelling opening, memorable moments, hooks reader'
            },
            'coherence': {
                'weight': 0.15,
                'description': 'Ideas connect logically, stays focused on theme'
            }
        }

    def score_essay(self, essay_text: str) -> Dict[str, float]:
        """
        Score an essay using rubric.

        Uses heuristic scoring based on textual features.
        In production, this could use an LLM as a judge.

        Returns:
            Dictionary with category scores and total
        """
        scores = {}

        word_count = len(essay_text.split())

        # Authenticity: Check for specific details, personal voice
        i_count = essay_text.lower().count(' i ')
        quote_count = essay_text.count('"')
        specific_details = essay_text.count(',') + quote_count
        # Look for sensory words
        sensory_words = ['saw', 'heard', 'felt', 'smell', 'taste', 'touch', 'sound', 'color']
        sensory_count = sum(essay_text.lower().count(w) for w in sensory_words)
        scores['authenticity'] = min(10, (i_count * 0.3 + specific_details * 0.05 + sensory_count * 0.5 + quote_count * 0.5))

        # Structure: Check paragraph count, length variation
        paragraphs = [p for p in essay_text.split('\n\n') if p.strip()]
        para_count = len(paragraphs)
        # Good structure: 4-7 paragraphs for 650 word essay
        if 4 <= para_count <= 7:
            structure_score = 8.0
        elif 3 <= para_count <= 8:
            structure_score = 6.5
        else:
            structure_score = 5.0
        scores['structure'] = structure_score

        # Insight: Look for reflection words
        reflection_words = ['learned', 'realized', 'understood', 'changed', 'grew',
                          'discovered', 'recognized', 'transformed', 'insight', 'perspective']
        reflection_count = sum(essay_text.lower().count(w) for w in reflection_words)
        scores['insight'] = min(10, reflection_count * 1.5 + 4)

        # Engagement: Check opening strength (first 100 words)
        opening = essay_text[:400]
        has_hook = any(c in opening for c in ['"', '?', '!'])
        has_specific_detail = any(word in opening.lower() for word in
                                  ['morning', 'night', 'day', 'moment', 'time', 'year'])
        engagement_score = 5.0
        if has_hook:
            engagement_score += 2.0
        if has_specific_detail:
            engagement_score += 1.5
        if not opening.lower().startswith(('i have', 'ever since', 'i always', 'throughout my')):
            engagement_score += 1.0
        scores['engagement'] = min(10, engagement_score)

        # Coherence: Lexical diversity and appropriate length
        words = essay_text.lower().split()
        unique_words = len(set(words))
        lexical_diversity = unique_words / word_count if word_count > 0 else 0
        # Good diversity is around 0.4-0.6
        if 0.35 <= lexical_diversity <= 0.65:
            coherence_score = 8.0
        elif 0.3 <= lexical_diversity <= 0.7:
            coherence_score = 6.5
        else:
            coherence_score = 5.0
        # Penalty for too short or too long
        if word_count < 500 or word_count > 800:
            coherence_score -= 1.0
        scores['coherence'] = max(0, coherence_score)

        # Calculate weighted total
        total = sum(
            scores[category] * self.rubric[category]['weight']
            for category in self.rubric
        )

        scores['total'] = round(total, 2)
        scores['word_count'] = word_count

        return scores

    def compare_with_without_rag(
        self,
        test_prompts: List[str],
        student_profile: dict,
        target_university: str = "MIT"
    ) -> Dict:
        """
        Run comparison test.

        Args:
            test_prompts: List of essay prompts to test
            student_profile: Student profile dict
            target_university: Target university

        Returns:
            Comparison results with statistics
        """
        # Import here to avoid circular imports
        from agents.workflow import run_essay_generation, run_essay_generation_without_rag

        print("\n" + "=" * 60)
        print("RAG EVALUATION - Comparing With vs Without Retrieval")
        print("=" * 60 + "\n")

        results = {
            'test_date': datetime.now().isoformat(),
            'target_university': target_university,
            'prompts': [],
            'summary': {}
        }

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i}/{len(test_prompts)} ---")
            print(f"Prompt: {prompt[:80]}...")

            # WITHOUT RAG
            print("\n  Running WITHOUT RAG...")
            try:
                state_without = run_essay_generation_without_rag(
                    prompt=prompt,
                    student_profile=student_profile,
                    target_university=target_university
                )
                essay_without = state_without.get('essay_draft', '')
                scores_without = self.score_essay(essay_without)
            except Exception as e:
                print(f"  Error (without RAG): {e}")
                scores_without = {'total': 0, 'word_count': 0}
                essay_without = ""

            # WITH RAG
            print("\n  Running WITH RAG...")
            try:
                state_with = run_essay_generation(
                    prompt=prompt,
                    student_profile=student_profile,
                    target_university=target_university
                )
                essay_with = state_with.get('essay_draft', '')
                scores_with = self.score_essay(essay_with)
                retrieved_count = len(state_with.get('retrieved_essays', []))
            except Exception as e:
                print(f"  Error (with RAG): {e}")
                scores_with = {'total': 0, 'word_count': 0}
                essay_with = ""
                retrieved_count = 0

            # Calculate improvement
            if scores_without['total'] > 0:
                improvement = scores_with['total'] - scores_without['total']
                percent_improvement = (improvement / scores_without['total']) * 100
            else:
                improvement = scores_with['total']
                percent_improvement = 100

            # Store results
            prompt_result = {
                'prompt': prompt,
                'without_rag': {
                    'scores': scores_without,
                    'essay_preview': essay_without[:200] if essay_without else ''
                },
                'with_rag': {
                    'scores': scores_with,
                    'examples_used': retrieved_count,
                    'essay_preview': essay_with[:200] if essay_with else ''
                },
                'improvement': {
                    'absolute': round(improvement, 2),
                    'percentage': round(percent_improvement, 1)
                }
            }

            results['prompts'].append(prompt_result)

            # Print summary
            print(f"\n  Results:")
            print(f"    Without RAG: {scores_without['total']:.2f}/10 ({scores_without.get('word_count', 0)} words)")
            print(f"    With RAG:    {scores_with['total']:.2f}/10 ({scores_with.get('word_count', 0)} words)")
            print(f"    Retrieved examples: {retrieved_count}")
            print(f"    Improvement: {improvement:+.2f} ({percent_improvement:+.1f}%)")

        # Calculate overall statistics
        valid_prompts = [p for p in results['prompts'] if p['without_rag']['scores']['total'] > 0]

        if valid_prompts:
            avg_without = sum(p['without_rag']['scores']['total'] for p in valid_prompts) / len(valid_prompts)
            avg_with = sum(p['with_rag']['scores']['total'] for p in valid_prompts) / len(valid_prompts)
            avg_improvement = avg_with - avg_without
        else:
            avg_without = avg_with = avg_improvement = 0

        results['summary'] = {
            'total_tests': len(test_prompts),
            'successful_tests': len(valid_prompts),
            'avg_score_without_rag': round(avg_without, 2),
            'avg_score_with_rag': round(avg_with, 2),
            'avg_improvement': round(avg_improvement, 2),
            'percent_improvement': round((avg_improvement / avg_without) * 100, 1) if avg_without > 0 else 0
        }

        # Save results
        output_dir = Path('outputs/evaluation')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'rag_evaluation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 60)
        print("EVALUATION COMPLETE")
        print("=" * 60)
        print(f"\nTests run: {results['summary']['total_tests']}")
        print(f"Successful: {results['summary']['successful_tests']}")
        print(f"\nAverage Score Without RAG: {avg_without:.2f}/10")
        print(f"Average Score With RAG:    {avg_with:.2f}/10")
        print(f"Average Improvement:       {avg_improvement:+.2f} ({results['summary']['percent_improvement']:+.1f}%)")
        print(f"\nDetailed results saved to: {output_file}")

        return results

    def print_category_breakdown(self, results: Dict):
        """Print detailed category breakdown."""
        print("\n" + "=" * 60)
        print("CATEGORY BREAKDOWN")
        print("=" * 60)

        valid_prompts = [p for p in results['prompts']
                        if p['without_rag']['scores']['total'] > 0 and
                        p['with_rag']['scores']['total'] > 0]

        if not valid_prompts:
            print("No valid results to analyze")
            return

        for category in self.rubric:
            without_avg = sum(
                p['without_rag']['scores'].get(category, 0)
                for p in valid_prompts
            ) / len(valid_prompts)

            with_avg = sum(
                p['with_rag']['scores'].get(category, 0)
                for p in valid_prompts
            ) / len(valid_prompts)

            improvement = with_avg - without_avg

            print(f"\n{category.capitalize()} (weight: {self.rubric[category]['weight']}):")
            print(f"  {self.rubric[category]['description']}")
            print(f"  Without RAG: {without_avg:.2f}")
            print(f"  With RAG:    {with_avg:.2f}")
            print(f"  Change:      {improvement:+.2f}")


def main():
    """
    Run the evaluation.

    Usage:
        python -m evaluation.rag_comparison
    """

    # Sample student profile for testing
    test_profile = {
        'name': 'Test Student',
        'background': 'First-generation college student passionate about technology',
        'interests': {'academic': 'Computer Science', 'personal': 'Building apps'},
        'major_experiences': [
            {
                'title': 'Coding Club Founder',
                'description': 'Started coding club at school, taught 30+ students'
            },
            {
                'title': 'App Developer',
                'description': 'Built an app to help local businesses during pandemic'
            }
        ],
        'activities': ['Coding Club', 'Math Team', 'Tutoring'],
        'voice_characteristics': {
            'overall_tone': 'Technical but warm',
            'writing_style': 'Clear and specific'
        },
        'sat_verbal': 750
    }

    # Test prompts covering different topics
    test_prompts = [
        "Write about a time when you faced a significant coding challenge and what it taught you about problem-solving",
        "Describe an experience that shaped your understanding of leadership and community",
        "Discuss a moment when failure led to personal growth and a new perspective"
    ]

    evaluator = RAGEvaluator()
    results = evaluator.compare_with_without_rag(
        test_prompts=test_prompts,
        student_profile=test_profile,
        target_university="MIT"
    )

    # Print category breakdown
    evaluator.print_category_breakdown(results)


if __name__ == "__main__":
    main()
