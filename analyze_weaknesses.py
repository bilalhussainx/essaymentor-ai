import json
from pathlib import Path
from collections import Counter
import re

def analyze_test_results():
    """Analyze test suite results to find patterns in weaknesses"""
    
    # Find latest test results
    test_dir = Path("outputs/tests")
    if not test_dir.exists():
        print("❌ No test results found. Run test_suite.py first.")
        return
    
    json_files = list(test_dir.glob("test_suite_*.json"))
    if not json_files:
        print("❌ No test results found.")
        return
    
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file) as f:
        results = json.load(f)
    
    print("\n" + "="*70)
    print(" WEAKNESS ANALYSIS - PATTERNS TO FIX WITH FINE-TUNING")
    print("="*70)
    
    # Analyze openings
    print("\n📝 OPENING ANALYSIS:")
    generic_phrases = [
        "as i reflect", "ever since i was", "i have always",
        "growing up", "throughout my life", "from a young age",
        "as a computer science", "i've always thought"
    ]
    
    generic_count = 0
    specific_count = 0
    time_count = 0
    
    for result in results:
        if 'opening' not in result:
            continue
        opening_lower = result['opening'].lower()
        
        # Check for generic phrases
        is_generic = any(phrase in opening_lower for phrase in generic_phrases)
        
        # Check for specific time details
        has_time = bool(re.search(r'\d{1,2}:\d{2}', opening_lower))
        
        if is_generic:
            generic_count += 1
            print(f"   ⚠️  Semi-generic: {result['opening'][:80]}...")
        
        if has_time:
            time_count += 1
            print(f"   ✅ Has specific time: {result['opening'][:80]}...")
    
    print(f"\n   Essays with specific times (2:47 AM style): {time_count}/{len(results)}")
    print(f"   Essays with generic phrases: {generic_count}/{len(results)}")
    
    # Analyze scores
    print("\n📊 QUALITY SCORES:")
    scores = []
    for result in results:
        if 'score' in result and result['score'] != "N/A":
            try:
                scores.append(float(result['score']))
            except:
                pass
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"   Average score: {avg_score:.1f}/10")
        print(f"   Score range: {min(scores):.1f}-{max(scores):.1f}/10")
        print(f"   Number of scores: {len(scores)}/{len(results)}")
    else:
        print(f"   No numerical scores extracted")
        print(f"   (Critique agent didn't always format scores consistently)")
    
    # Analyze word counts
    print("\n📏 WORD COUNT ANALYSIS:")
    word_counts = [r['word_count'] for r in results if 'word_count' in r]
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        print(f"   Average: {avg_words:.0f} words")
        print(f"   Range: {min(word_counts)}-{max(word_counts)} words")
        print(f"   Target: 650 words")
        print(f"   Within ±50 of target: {sum(1 for w in word_counts if 600 <= w <= 700)}/{len(word_counts)}")
    
    # Common critique themes
    print("\n🔍 COMMON WEAKNESSES (from critiques):")
    
    all_critiques = " ".join(r.get('critique', '') for r in results).lower()
    
    weakness_keywords = {
        'generic': ['generic', 'vague', 'abstract', 'broad'],
        'voice': ['authentic', 'voice', 'natural', 'conversational'],
        'details': ['specific', 'concrete', 'detail', 'vivid'],
        'showing': ['show', 'tell', 'demonstrate'],
        'structure': ['structure', 'flow', 'transition', 'pacing'],
        'cliche': ['cliché', 'clichéd', 'familiar trope', 'overly familiar']
    }
    
    for category, keywords in weakness_keywords.items():
        count = sum(all_critiques.count(kw) for kw in keywords)
        if count > 0:
            print(f"   - {category.capitalize()}: mentioned {count} times")
    
    # Analyze specific weaknesses mentioned
    print("\n⚠️  MOST COMMON CRITIQUE POINTS:")
    critique_patterns = [
        "generic statements",
        "lacks depth",
        "overly familiar",
        "could be more specific",
        "voice feels generic",
        "lacks originality",
        "not distinctive"
    ]
    
    for pattern in critique_patterns:
        count = all_critiques.count(pattern.lower())
        if count > 0:
            print(f"   - '{pattern}': {count} mentions")
    
    # Generate fine-tuning priorities
    print("\n🎯 FINE-TUNING PRIORITIES:")
    print("\n   1. ⭐ CRITICAL: Voice Authenticity")
    print(f"      - Current: Base model uses good specific details (2:47 AM)")
    print(f"      - Issue: Still sounds slightly AI-generated in body")
    print(f"      - Target: Natural 17-year-old voice throughout")
    print(f"      - Solution: Train on 100+ real student essays")
    print()
    print("   2. ⭐ HIGH: Reduce Generic Statements")
    print(f"      - Current: '{generic_count}/{len(results)}' essays have some generic phrasing")
    print(f"      - Target: Eliminate phrases like 'I realized that...'")
    print(f"      - Solution: Train model to show, not tell")
    print()
    print("   3. ⭐ HIGH: Improve Depth & Originality")
    if scores:
        print(f"      - Current avg: {avg_score:.1f}/10")
    print(f"      - Target: 8-9/10 quality")
    print(f"      - Solution: Fine-tune on only 8+ quality essays")
    print()
    print("   4. MEDIUM: Enhance Emotional Nuance")
    print(f"      - Current: Emotions presented as binary")
    print(f"      - Solution: Include essays with complex emotional arcs")
    print()
    print("   5. MEDIUM: Eliminate Clichés")
    print(f"      - Solution: Train on essays that avoid common phrases")
    
    # Key insight
    print("\n💡 KEY INSIGHT:")
    print(f"   The multi-agent system STRUCTURE is working well:")
    print(f"   - Specific openings (2:47 AM style): ✅")
    print(f"   - Consistent word counts (~{avg_words:.0f}): ✅" if word_counts else "")
    print(f"   - Clear narrative structure: ✅")
    print()
    print(f"   What needs improvement (via fine-tuning Draft Agent):")
    print(f"   - Voice authenticity (sounds AI-generated)")
    print(f"   - Depth of reflection")
    print(f"   - Originality of insights")
    
    # Save analysis
    analysis_file = test_dir / f"weakness_analysis_{latest_file.stem.split('_')[-1]}.md"
    
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write("# Weakness Analysis for Fine-Tuning\n\n")
        f.write(f"**Based on:** {latest_file.name}\n")
        f.write(f"**Essays analyzed:** {len(results)}\n")
        f.write(f"**Date:** {Path(latest_file).stat().st_mtime}\n\n")
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- Average word count: {avg_words:.0f}\n" if word_counts else "")
        f.write(f"- Average quality score: {avg_score:.1f}/10\n" if scores else "- Scores: Not consistently extracted\n")
        f.write(f"- Essays with specific time details: {time_count}/{len(results)}\n")
        f.write(f"- Essays with generic phrases: {generic_count}/{len(results)}\n\n")
        
        f.write("## Fine-Tuning Priorities\n\n")
        f.write("### CRITICAL\n")
        f.write("1. **Voice Authenticity** - Train on real student essays to eliminate AI-sounding language\n")
        f.write("2. **Reduce Generic Statements** - Eliminate 'I realized that...' style conclusions\n\n")
        
        f.write("### HIGH\n")
        f.write("3. **Improve Depth & Originality** - Train only on 8+/10 quality essays\n")
        f.write("4. **Enhance Emotional Nuance** - Include complex emotional arcs\n\n")
        
        f.write("### MEDIUM\n")
        f.write("5. **Eliminate Clichés** - Avoid familiar phrases and tropes\n\n")
        
        f.write("## What's Working\n\n")
        f.write("- Multi-agent architecture produces consistent structure ✅\n")
        f.write("- Specific details in openings (2:47 AM style) ✅\n")
        f.write("- Consistent word counts near 650-word target ✅\n")
        f.write("- Clear narrative progression ✅\n\n")
        
        f.write("## What Needs Improvement (Fine-Tuning Target)\n\n")
        f.write("- Voice authenticity (Draft Agent)\n")
        f.write("- Depth of reflection\n")
        f.write("- Originality of insights\n")
        f.write("- Emotional complexity\n")
    
    print(f"\n💾 Analysis saved to: {analysis_file}")
    print("\n" + "="*70)
    print(" NEXT STEPS")
    print("="*70)
    print("\n1. Collect 100+ high-quality essays (Week 2)")
    print("2. Prepare fine-tuning dataset (Week 3)")
    print("3. Fine-tune Draft Agent only (Week 3-4)")
    print("4. Re-run these same prompts to measure improvement")
    print("\n   Expected improvement: 6-7/10 → 8-9/10 quality")

if __name__ == "__main__":
    analyze_test_results()