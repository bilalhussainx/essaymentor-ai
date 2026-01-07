from agents.workflow import run_essay_generation
from pathlib import Path
from datetime import datetime

# Test prompt
test_prompt = """Discuss an accomplishment, event, or realization that sparked 
a period of personal growth and a new understanding of yourself or others."""

# Run the complete workflow
result = run_essay_generation(test_prompt)

# Display results
print("\n" + "="*70)
print(" FINAL ESSAY")
print("="*70)
print(result['essay_draft'])

print("\n" + "="*70)
print(" CRITIQUE")
print("="*70)
print(result['essay_critique'])

# Save everything to file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / f"multi_agent_run_{timestamp}.md"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"# Multi-Agent Essay Generation Result\n\n")
    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Prompt:** {test_prompt}\n\n")
    f.write(f"---\n\n")
    
    f.write(f"## Agent Timings\n\n")
    for agent, time_taken in result['agent_times'].items():
        f.write(f"- {agent.capitalize()}: {time_taken:.1f}s\n")
    f.write(f"\nTotal: {sum(result['agent_times'].values()):.1f}s\n\n")
    
    f.write(f"---\n\n")
    f.write(f"## Research Analysis\n\n{result['research_analysis']}\n\n")
    f.write(f"---\n\n")
    f.write(f"## Brainstorm Ideas\n\n")
    for i, idea in enumerate(result['brainstorm_ideas'], 1):
        f.write(f"### Idea {i}\n{idea}\n\n")
    f.write(f"---\n\n")
    f.write(f"## Essay Outline\n\n{result['essay_outline']}\n\n")
    f.write(f"---\n\n")
    f.write(f"## Final Essay\n\n{result['essay_draft']}\n\n")
    f.write(f"---\n\n")
    f.write(f"## Critique\n\n{result['essay_critique']}\n\n")

print(f"\n💾 Full results saved to: {output_file}")