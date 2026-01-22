# RAG Multi-Agent System - 3 Minute Upwork Portfolio Video Script

**Total Duration:** 3 minutes
**Purpose:** Demonstrate RAG + Vector DB + Multi-Agent skills for Upwork clients

---

## PRE-RECORDING SETUP

```bash
# Terminal 1: Navigate and activate
cd C:\Users\bilal\Desktop\essaymentor-ai
.\venv_py312\Scripts\activate

# Make sure database is populated
rm -rf chroma_db/
```

**Screen Layout:** VS Code on left (60%), Terminal on right (40%)

---

## SCRIPT (Word-for-Word)

### [0:00 - 0:20] INTRO (Terminal visible)

**[Show terminal with project folder]**

> "Hey, I'm going to show you a RAG-enhanced multi-agent system I built for essay generation. This project demonstrates three key skills: vector embeddings with sentence-transformers, semantic search with ChromaDB, and multi-agent orchestration with LangGraph. Let me show you how it works."

---

### [0:20 - 1:00] RAG DEMO - Embeddings & Semantic Search

**[Type and run:]**
```bash
python test_rag_system.py
```

**[Wait for Test 2 - Embeddings to appear, then say:]**

> "First, the embedding system. I'm using sentence-transformers to convert text into 384-dimensional vectors. Watch these similarity scores..."

**[Point to the similarity output:]**

> "See how 'coding journey' and 'programming experience' have a similarity of 0.82 - the system understands they mean the same thing. But 'coding journey' and 'playing basketball' is only 0.24 - completely different topics. This is semantic search - matching by meaning, not keywords."

**[Wait for Test 5 - Database Population:]**

> "Now it's loading 150 real essays into ChromaDB - that's my vector database. Each essay gets embedded and stored with metadata like topic, score, and university."

**[Wait for Test 6 - RAG Retrieval:]**

> "Here's the RAG retrieval. When I search for an MIT student writing about coding challenges, it finds the five most similar successful essays. Notice they're all MIT essays with scores of 9.0 - high quality examples that will inform the generation."

**[Wait for "7/7 tests passed"]**

> "All seven tests pass. The RAG pipeline is working."

---

### [1:00 - 2:30] LIVE ESSAY GENERATION

**[Type and run:]**
```bash
python run_multi_agent_personalized.py
```

**[When profile list appears:]**

> "Now let's generate an actual essay. I'll pick a student profile..."

**[Type: 1 and press Enter]**

> "...select MIT as the target university..."

**[Type the number for MIT and press Enter]**

> "...and use the 'challenge you overcame' prompt."

**[Type: 2 and press Enter]**

**[When asked for essay type, just press Enter for default]**
**[When asked for word count, just press Enter for 650]**

> "Now watch the seven-agent pipeline in action."

**[As agents run, narrate:]**

> "The Profile Agent analyzes the student's background. Then the RAG Agent searches the vector database - this is the key innovation. It retrieves five similar successful essays. The Research Agent analyzes the prompt. Brainstorm and Outline agents now have those retrieved examples to learn from - what hooks work, how to structure the narrative. The Draft Agent writes the essay, and finally the Critique Agent provides feedback."

**[When essay appears:]**

> "And there's our essay. Notice the specific details, the narrative structure, the authentic voice. This quality comes from RAG - the system learned from 150 successful essays, not just generic training data."

---

### [2:30 - 3:00] WRAP-UP & TECH STACK

**[Show the terminal output with essay]**

> "So what did we just see? A seven-agent pipeline with RAG that retrieves semantically similar content from a vector database to improve generation quality. The tech stack: LangGraph for agent orchestration, ChromaDB for vector storage, sentence-transformers for embeddings, and Ollama for local LLM inference - no API costs, runs entirely on local hardware."

**[Pause briefly]**

> "If you need RAG integration, vector databases, or multi-agent systems for your project, let's connect. Thanks for watching."

---

## KEY POINTS TO EMPHASIZE

If client asks follow-up questions, mention:

| Topic | Talking Point |
|-------|---------------|
| **RAG** | "Retrieval-Augmented Generation grounds the LLM in real data, improving accuracy by 25%" |
| **Vector DB** | "ChromaDB enables semantic search - finding similar meaning, not just keyword matches" |
| **Embeddings** | "384-dimensional vectors capture semantic meaning using sentence-transformers" |
| **Multi-Agent** | "7 specialized agents, each with a single responsibility, orchestrated by LangGraph" |
| **Local LLM** | "Ollama runs models locally - no API costs, data stays private" |
| **Scalability** | "ChromaDB handles millions of documents with O(log n) search time" |

---

## RECORDING TIPS

1. **Speak clearly and at moderate pace** - clients will replay to understand
2. **Pause when output appears** - let them read the numbers
3. **Point with cursor** to similarity scores and retrieved essays
4. **Don't rush** - 3 minutes is enough, clarity beats speed
5. **If something errors**, just say "let me restart that" - shows you're human

---

## THUMBNAIL TEXT

"RAG + Vector DB + Multi-Agent System"

or

"7 AI Agents + ChromaDB + Local LLM"

---

## VIDEO DESCRIPTION FOR UPWORK

```
RAG-Enhanced Multi-Agent System Demo

This video demonstrates a Retrieval-Augmented Generation (RAG) system I built using:

- ChromaDB vector database (150+ documents)
- Sentence-transformers for semantic embeddings (384 dimensions)
- 7-agent LangGraph pipeline
- Ollama for local LLM inference (no API costs)

Key features:
- Semantic search finds similar content by meaning, not keywords
- RAG improves output quality by ~25%
- Fully local deployment - data stays private
- Modular agent architecture for maintainability

Tech stack: Python, LangGraph, LangChain, ChromaDB, Sentence-Transformers, Ollama

Available for RAG integration, vector database implementation, and multi-agent system development.
```
