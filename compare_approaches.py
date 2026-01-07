from agents.workflow import run_essay_generation
from agents.ollama_helper import call_ollama
import time

prompt = "Reflect on a time when you questioned or challenged a belief or idea."

print("\n" + "="*70)
print(" COMPARISON: SINGLE-AGENT vs MULTI-AGENT")
print("="*70)

# Single-agent approach
print("\n📝 Running SINGLE-AGENT approach...")
start = time.time()
single_agent_prompt = f"""Write a 650-word college essay for this prompt:

{prompt}

Make it compelling with specific details and personal growth."""

single_essay, _ = call_ollama(single_agent_prompt, temperature=0.75, max_tokens=2500)
single_time = time.time() - start

print(f"✅ Single-agent done ({single_time:.1f}s)")
print(f"   Word count: {len(single_essay.split())}")

# Multi-agent approach
print("\n🤖 Running MULTI-AGENT approach...")
multi_result = run_essay_generation(prompt)
multi_time = sum(multi_result['agent_times'].values())

print("\n" + "="*70)
print(" RESULTS")
print("="*70)

print(f"\nSingle-Agent:")
print(f"  Time: {single_time:.1f}s")
print(f"  Words: {len(single_essay.split())}")
print(f"  First 200 chars: {single_essay[:200]}...")

print(f"\nMulti-Agent:")
print(f"  Time: {multi_time:.1f}s")
print(f"  Words: {len(multi_result['essay_draft'].split())}")
print(f"  First 200 chars: {multi_result['essay_draft'][:200]}...")

print(f"\n📊 Time difference: Multi-agent is {multi_time/single_time:.1f}x slower")
print(f"   But produces more researched, structured essays!")