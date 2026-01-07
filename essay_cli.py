import typer
import requests
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from datetime import datetime
import time

app = typer.Typer(help="EssayMentor AI - Multi-agent essay generation and critique")
console = Console()

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

def call_ollama(prompt: str, temperature: float = 0.7) -> tuple[str, float]:
    """Call Ollama API and return response + time taken"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": 2000  # Allow longer responses
        }
    }
    
    start = time.time()
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        elapsed = time.time() - start
        return response.json()['response'], elapsed
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error calling Ollama: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running![/yellow]")
        raise typer.Exit(1)

@app.command()
def generate(
    prompt: str = typer.Argument(..., help="College essay prompt"),
    words: int = typer.Option(650, help="Target word count"),
    style: str = typer.Option("balanced", help="Style: vulnerable/technical/creative/balanced"),
    save: bool = typer.Option(True, help="Save to outputs/"),
):
    """
    Generate a college essay from scratch
    
    Example:
        python essay_cli.py generate "Discuss an accomplishment that sparked personal growth"
    """
    
    console.print("\n[bold blue]🎓 EssayMentor AI - Essay Generation[/bold blue]")
    console.print(f"Prompt: [italic]{prompt[:100]}...[/italic]\n")
    
    # Style-specific system prompts
    style_prompts = {
        "vulnerable": """You write college essays showing authentic vulnerability.
Focus on: moments of failure/struggle, emotional honesty, what you learned from difficulty.
Avoid: overcoming clichés, forced inspiration, happy endings without depth.""",
        
        "technical": """You write college essays about technical/academic pursuits.
Focus on: specific technical details, curiosity-driven exploration, intellectual growth.
Avoid: jargon without explanation, showing off knowledge, talking down to reader.""",
        
        "creative": """You write college essays with creative storytelling.
Focus on: vivid scenes, unique metaphors, sensory details, distinctive voice.
Avoid: purple prose, forced creativity, style over substance.""",
        
        "balanced": """You are trained on successful Harvard admissions essays.
Write with: specific details, authentic voice, clear personal growth.
Show, don't tell. Use vivid moments, not abstract statements."""
    }
    
    system_prompt = style_prompts.get(style, style_prompts["balanced"])
    
    full_prompt = f"""{system_prompt}

Essay prompt: {prompt}

Write a compelling {words}-word college admissions essay that:
1. Opens with a specific, vivid moment (not a broad statement)
2. Uses concrete details and sensory descriptions
3. Shows personal growth through actions and experiences
4. Maintains an authentic, natural voice
5. Ends with meaningful reflection

Write the complete essay now:"""
    
    # Generate essay
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Generating {words}-word essay...", total=None)
        essay, time_taken = call_ollama(full_prompt, temperature=0.75)
        progress.update(task, completed=True)
    
    # Display results
    word_count = len(essay.split())
    console.print(Panel(essay, title=f"✨ Generated Essay ({word_count} words)", border_style="green"))
    console.print(f"\n⏱️  Time: {time_taken:.2f}s | Words: {word_count} | Style: {style}")
    
    # Save if requested
    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"essay_{timestamp}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Generated College Essay\n\n")
            f.write(f"**Prompt:** {prompt}\n\n")
            f.write(f"**Style:** {style}\n")
            f.write(f"**Target Words:** {words}\n")
            f.write(f"**Actual Words:** {word_count}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Generation Time:** {time_taken:.2f}s\n\n")
            f.write(f"---\n\n{essay}\n")
        
        console.print(f"\n💾 [green]Saved to: {output_file}[/green]")

@app.command()
def critique(
    essay: str = typer.Argument(..., help="Essay text or path to file (.txt, .md)"),
    save: bool = typer.Option(True, help="Save critique to outputs/"),
    detailed: bool = typer.Option(True, help="Include detailed line-by-line suggestions"),
):
    """
    Get expert critique of an existing essay
    
    Examples:
        python essay_cli.py critique "outputs/essay_20260106_183000.md"
        python essay_cli.py critique "I've always loved coding..."
    """
    
    console.print("\n[bold yellow]🔍 EssayMentor AI - Essay Critique[/bold yellow]\n")
    
    # Check if it's a file path
    essay_path = Path(essay)
    if essay_path.exists():
        with open(essay_path, encoding="utf-8") as f:
            essay_text = f.read()
        console.print(f"[dim]Analyzing file: {essay_path}[/dim]\n")
    else:
        essay_text = essay
        console.print(f"[dim]Analyzing text ({len(essay.split())} words)[/dim]\n")
    
    # Create comprehensive critique prompt
    critique_prompt = f"""As a Harvard admissions essay expert with 20 years of experience, provide a comprehensive critique of this college essay:

{essay_text}

Provide your analysis in this exact format:

## OVERALL ASSESSMENT
- Score: [X/10]
- One-sentence summary of the essay's effectiveness

## STRENGTHS (with specific examples from the text)
1. [Strength with quote/example]
2. [Strength with quote/example]
3. [Strength with quote/example]

## WEAKNESSES (with specific examples from the text)
1. [Weakness with quote/example]
2. [Weakness with quote/example]
3. [Weakness with quote/example]

## SPECIFIC IMPROVEMENTS
1. Opening: [Concrete suggestion]
2. Body: [Concrete suggestion]
3. Ending: [Concrete suggestion]
4. Voice/Style: [Concrete suggestion]

## REVISED OPENING PARAGRAPH
[Write an improved version of the first paragraph]

## COLLEGE READINESS
- Would this essay work for: [Top-tier/Competitive/Safety schools]
- Best fit for colleges that value: [specific qualities]

Be honest, specific, and constructive. Reference actual phrases from the essay."""
    
    # Generate critique
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]Analyzing essay quality...", total=None)
        critique_text, time_taken = call_ollama(critique_prompt, temperature=0.4)
        progress.update(task, completed=True)
    
    # Display critique
    console.print(Panel(
        critique_text, 
        title="📊 Expert Critique", 
        border_style="yellow",
        padding=(1, 2)
    ))
    console.print(f"\n⏱️  Analysis time: {time_taken:.2f}s")
    
    # Save if requested
    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"critique_{timestamp}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Essay Critique\n\n")
            f.write(f"**Analyzed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis Time:** {time_taken:.2f}s\n")
            f.write(f"**Essay Word Count:** {len(essay_text.split())}\n\n")
            f.write(f"---\n\n## ORIGINAL ESSAY\n\n{essay_text}\n\n")
            f.write(f"---\n\n## CRITIQUE\n\n{critique_text}\n")
        
        console.print(f"\n💾 [green]Critique saved to: {output_file}[/green]")

@app.command()
def compare(
    prompt: str = typer.Argument(..., help="Essay prompt to test with multiple strategies"),
    save: bool = typer.Option(True, help="Save comparison results"),
):
    """
    Compare different writing strategies for the same prompt
    
    Example:
        python essay_cli.py compare "Describe a challenge you overcame"
    """
    
    console.print("\n[bold magenta]⚡ EssayMentor AI - Strategy Comparison[/bold magenta]")
    console.print(f"Prompt: [italic]{prompt[:80]}...[/italic]\n")
    
    strategies = {
        "Harvard-Trained": """You are trained on successful Harvard essays. 
Use specific details, authentic voice, show vulnerability and growth.""",
        
        "Show-Don't-Tell": """Write using show-don't-tell principle:
Replace statements with scenes, use sensory details, demonstrate through actions.""",
        
        "Storytelling Arc": """Structure as: Hook (specific moment) → Context (brief) → Challenge → Growth → Reflection.
Focus on one story told deeply, not multiple surface-level anecdotes.""",
        
        "Authentic Voice": """Write in a natural, conversational tone like the student is talking to a trusted mentor.
Avoid essay-speak, flowery language, or trying to sound smart. Be genuine.""",
    }
    
    results = {}
    
    # Create comparison table
    table = Table(title="Strategy Comparison Results", show_header=True, header_style="bold magenta")
    table.add_column("Strategy", style="cyan", width=20)
    table.add_column("Time", justify="right", style="green", width=10)
    table.add_column("Words", justify="right", style="yellow", width=10)
    table.add_column("Preview", style="white", width=50)
    
    for name, system_prompt in strategies.items():
        console.print(f"\n[cyan]Testing: {name}[/cyan]")
        
        full_prompt = f"{system_prompt}\n\nEssay prompt: {prompt}\n\nWrite a compelling 200-word opening section:"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Generating with {name}...", total=None)
            essay, time_taken = call_ollama(full_prompt, temperature=0.75)
            progress.update(task, completed=True)
        
        word_count = len(essay.split())
        preview = essay[:150].replace("\n", " ") + "..."
        
        results[name] = {
            "essay": essay,
            "time": time_taken,
            "words": word_count,
            "system_prompt": system_prompt
        }
        
        table.add_row(name, f"{time_taken:.1f}s", str(word_count), preview)
    
    console.print("\n")
    console.print(table)
    
    # Save comparison
    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path("outputs") / f"comparison_{timestamp}.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Strategy Comparison Results\n\n")
            f.write(f"**Prompt:** {prompt}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"---\n\n")
            
            for name, data in results.items():
                f.write(f"## {name}\n\n")
                f.write(f"**Time:** {data['time']:.2f}s | **Words:** {data['words']}\n\n")
                f.write(f"**System Prompt:**\n{data['system_prompt']}\n\n")
                f.write(f"**Generated Essay:**\n\n{data['essay']}\n\n")
                f.write(f"---\n\n")
        
        console.print(f"\n💾 [green]Full comparison saved to: {output_file}[/green]")

@app.command()
def improve(
    essay_file: str = typer.Argument(..., help="Path to essay file to improve"),
):
    """
    Get specific improvement suggestions and a revised version
    
    Example:
        python essay_cli.py improve outputs/essay_20260106_183000.md
    """
    
    console.print("\n[bold cyan]🚀 EssayMentor AI - Essay Improvement[/bold cyan]\n")
    
    # Read essay
    essay_path = Path(essay_file)
    if not essay_path.exists():
        console.print(f"[red]Error: File not found: {essay_file}[/red]")
        raise typer.Exit(1)
    
    with open(essay_path, encoding="utf-8") as f:
        essay_text = f.read()
    
    console.print(f"[dim]Improving: {essay_path}[/dim]\n")
    
    # Generate improvements
    improve_prompt = f"""You are a college essay coach. Take this essay and improve it significantly.

ORIGINAL ESSAY:
{essay_text}

Provide:
1. Three specific problems with the current essay (with examples)
2. Three concrete changes to make (with before/after examples)
3. A COMPLETE REVISED VERSION that fixes all issues

The revised version should:
- Keep the same general story/topic
- Fix weak openings, generic statements, telling vs showing
- Add specific details and vivid moments
- Improve pacing and structure
- Strengthen the voice

Format your response as:

## PROBLEMS IDENTIFIED
1. [Problem with specific quote]
2. [Problem with specific quote]
3. [Problem with specific quote]

## IMPROVEMENTS TO MAKE
1. [Change with before/after example]
2. [Change with before/after example]
3. [Change with before/after example]

## REVISED ESSAY (COMPLETE)
[Full improved essay here]"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating improved version...", total=None)
        improvements, time_taken = call_ollama(improve_prompt, temperature=0.6)
        progress.update(task, completed=True)
    
    console.print(Panel(
        improvements,
        title="✨ Improvements & Revised Essay",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print(f"\n⏱️  Processing time: {time_taken:.2f}s")
    
    # Save improved version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path("outputs") / f"improved_{timestamp}.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Essay Improvement Report\n\n")
        f.write(f"**Original File:** {essay_path}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"---\n\n## ORIGINAL ESSAY\n\n{essay_text}\n\n")
        f.write(f"---\n\n{improvements}\n")
    
    console.print(f"\n💾 [green]Improved version saved to: {output_file}[/green]")

@app.command()
def status():
    """Check if Ollama is running and model is available"""
    console.print("\n[bold blue]🔧 System Status Check[/bold blue]\n")
    
    # Check Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            console.print("✅ [green]Ollama is running[/green]")
            
            # Check if our model is available
            model_names = [m['name'] for m in models]
            if MODEL in model_names:
                console.print(f"✅ [green]Model '{MODEL}' is available[/green]")
            else:
                console.print(f"❌ [red]Model '{MODEL}' not found[/red]")
                console.print(f"   Available models: {', '.join(model_names)}")
        else:
            console.print("❌ [red]Ollama responded but with error[/red]")
    except requests.exceptions.RequestException:
        console.print("❌ [red]Ollama is not running[/red]")
        console.print("   Start it with: ollama serve")
    
    console.print()

if __name__ == "__main__":
    app()