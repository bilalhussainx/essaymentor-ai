# EssayMentor AI

A multi-agent AI system for generating personalized college application essays using local LLMs. Built with LangGraph and Ollama.

## Overview

EssayMentor AI uses a 6-agent pipeline to generate high-quality, personalized college essays:

```
Profile → Research → Brainstorm → Outline → Draft → Critique
```

Each agent specializes in a specific part of the essay writing process:

| Agent | Role |
|-------|------|
| **Profile** | Analyzes student background, selects compelling experiences, aligns with target university values |
| **Research** | Analyzes the essay prompt type and requirements |
| **Brainstorm** | Generates creative angles and approaches |
| **Outline** | Creates structured essay outline |
| **Draft** | Writes the complete essay |
| **Critique** | Provides detailed feedback and suggestions |

## Features

- **Multi-Agent Architecture**: 6 specialized agents working in sequence via LangGraph
- **University Personalization**: Tailored essays for specific universities (MIT, Harvard, Stanford, etc.)
- **Student Profile Matching**: Uses student experiences, background, and achievements
- **Local LLM Support**: Runs entirely on local hardware via Ollama
- **CLI Tool**: Command-line interface for quick essay generation and critique
- **Multiple Writing Styles**: Vulnerable, technical, creative, or balanced approaches

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- llama3.1:8b model (or another compatible model)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bilalhussainx/essaymentor-ai.git
cd essaymentor-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Ollama and pull the model:
```bash
ollama serve
ollama pull llama3.1:8b
```

## Usage

### Multi-Agent Essay Generation

Run the complete 6-agent workflow:

```python
from agents.workflow import run_essay_generation

result = run_essay_generation(
    prompt="Discuss an accomplishment that sparked personal growth",
    student_profile={
        "name": "Alex",
        "background": "First-generation college student",
        "major_experiences": [...],
        "activities": ["Robotics Club", "Debate Team"],
        "interests": {"academic": "Computer Science", "personal": "Music"}
    },
    target_university="MIT",
    essay_type="common_app",
    word_count=650
)

print(result['essay_draft'])
print(result['critique'])
```

### CLI Commands

**Generate an essay:**
```bash
python essay_cli.py generate "Describe a challenge you overcame" --words 650 --style balanced
```

**Critique an existing essay:**
```bash
python essay_cli.py critique "path/to/essay.txt"
```

**Compare writing strategies:**
```bash
python essay_cli.py compare "Describe a challenge you overcame"
```

**Improve an essay:**
```bash
python essay_cli.py improve outputs/essay_20260106.md
```

**Check system status:**
```bash
python essay_cli.py status
```

### Writing Styles

- `vulnerable` - Authentic vulnerability, emotional honesty
- `technical` - Technical/academic focus with intellectual depth
- `creative` - Vivid storytelling, unique metaphors
- `balanced` - Well-rounded approach (default)

## Project Structure

```
essaymentor-ai/
├── agents/
│   ├── workflow.py          # LangGraph workflow orchestration
│   ├── state.py             # State definitions
│   ├── profile_agent.py     # Student profile analysis
│   ├── research_agent.py    # Prompt analysis
│   ├── brainstorm_agent.py  # Idea generation
│   ├── outline_agent.py     # Essay structure
│   ├── draft_agent.py       # Essay writing
│   ├── critique_agent.py    # Essay feedback
│   └── ollama_helper.py     # LLM interface
├── essay_cli.py             # CLI application
├── university_profiles.json # University-specific preferences
├── outputs/                 # Generated essays
└── requirements.txt
```

## Configuration

Create a `.env` file for environment variables:
```
OLLAMA_URL=http://localhost:11434
MODEL=llama3.1:8b
```

## Tech Stack

- **LangGraph** - Agent orchestration and workflow management
- **LangChain** - LLM integration framework
- **Ollama** - Local LLM inference
- **Typer** - CLI framework
- **Rich** - Terminal formatting

## License

MIT License
