from agents.workflow import run_essay_generation
from pathlib import Path
from datetime import datetime
import json

# Diverse test prompts (all official Common App prompts)
TEST_PROMPTS = [
    {
        "id": "prompt1",
        "category": "growth",
        "prompt": "Discuss an accomplishment, event, or realization that sparked a period of personal growth and a new understanding of yourself or others."
    },
    {
        "id": "prompt2", 
        "category": "challenge",
        "prompt": "The lessons we take from obstacles we encounter can be fundamental to later success. Recount a time when you faced a challenge, setback, or failure. How did it affect you, and what did you learn from the experience?"
    },
    {
        "id": "prompt3",
        "category": "belief",
        "prompt": "Reflect on a time when you questioned or challenged a belief or idea. What prompted your thinking? What was the outcome?"
    },
    {
        "id": "prompt4",
        "category": "gratitude",
        "prompt": "Reflect on something that someone has done for you that has made you happy or thankful in a surprising way. How has this gratitude affected or motivated you?"
    },
    {
        "id": "prompt5",
        "category": "passion",
        "prompt": "Describe a topic, idea, or concept you find so engaging that it makes you lose all track of time. Why does it captivate you? What or who do you turn to when you want to learn more?"
    }
]

def run_test_suite():
    """Run all test prompts and collect results"""
    
    print("\n" + "="*70)
    print(" COMPREHENSIVE TESTING SUITE")
    print("="*70)
    print(f"\nTesting {len(TEST_PROMPTS)} different prompt types...")
    print("This will take ~8 minutes (90s × 5 prompts)\n")
    
    results = []
    
    for i, test in enumerate(TEST_PROMPTS, 1):
        print(f"\n{'='*70}")
        print(f" TEST {i}/{len(TEST_PROMPTS)}: {test['category'].upper()}")
        print("="*70)
        print(f"Prompt: {test['prompt'][:80]}...\n")
        
        try:
            # Run the workflow
            result = run_essay_generation(test['prompt'])
            
            # Extract key metrics
            word_count = len(result['essay_draft'].split())
            opening = result['essay_draft'][:200]
            
            # Try to extract score from critique (simple regex)
            import re
            score_match = re.search(r'SCORE[:\s]+(\d+)/10', result['essay_critique'], re.IGNORECASE)
            score = score_match.group(1) if score_match else "N/A"
            
            test_result = {
                "id": test['id'],
                "category": test['category'],
                "prompt": test['prompt'],
                "word_count": word_count,
                "opening": opening,
                "score": score,
                "total_time": sum(result['agent_times'].values()),
                "agent_times": result['agent_times'],
                "full_essay": result['essay_draft'],
                "critique": result['essay_critique']
            }
            
            results.append(test_result)
            
            print(f"\n✅ Test {i} complete")
            print(f"   Word count: {word_count}")
            print(f"   Estimated score: {score}/10")
            print(f"   Opening: {opening[:100]}...")
            
        except Exception as e:
            print(f"\n❌ Test {i} failed: {str(e)}")
            results.append({
                "id": test['id'],
                "category": test['category'],
                "error": str(e)
            })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON summary
    summary_file = output_dir / f"test_suite_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # Save detailed markdown report
    report_file = output_dir / f"test_report_{timestamp}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Test Suite Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Tests Run:** {len(TEST_PROMPTS)}\n\n")
        f.write(f"---\n\n")
        
        for i, result in enumerate(results, 1):
            if 'error' in result:
                f.write(f"## Test {i}: {result['category']} - FAILED\n\n")
                f.write(f"**Error:** {result['error']}\n\n")
                continue
                
            f.write(f"## Test {i}: {result['category']}\n\n")
            f.write(f"**Prompt:** {result['prompt']}\n\n")
            f.write(f"**Metrics:**\n")
            f.write(f"- Word count: {result['word_count']}\n")
            f.write(f"- Score: {result['score']}/10\n")
            f.write(f"- Total time: {result['total_time']:.1f}s\n\n")
            f.write(f"**Opening:**\n> {result['opening']}\n\n")
            f.write(f"---\n\n")
            f.write(f"### Full Essay\n\n{result['full_essay']}\n\n")
            f.write(f"### Critique\n\n{result['critique']}\n\n")
            f.write(f"---\n\n")
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUITE COMPLETE - SUMMARY")
    print("="*70)
    
    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]
    
    print(f"\n✅ Successful: {len(successful)}/{len(TEST_PROMPTS)}")
    print(f"❌ Failed: {len(failed)}/{len(TEST_PROMPTS)}")
    
    if successful:
        avg_words = sum(r['word_count'] for r in successful) / len(successful)
        avg_time = sum(r['total_time'] for r in successful) / len(successful)
        
        print(f"\n📊 Average Metrics:")
        print(f"   - Word count: {avg_words:.0f}")
        print(f"   - Generation time: {avg_time:.1f}s")
        
        print(f"\n📝 Opening Styles:")
        for r in successful[:3]:  # Show first 3
            print(f"   - {r['category']}: {r['opening'][:80]}...")
    
    print(f"\n💾 Results saved:")
    print(f"   - Summary: {summary_file}")
    print(f"   - Report: {report_file}")
    
    return results

if __name__ == "__main__":
    run_test_suite()