# EssayMentor AI - Video Demo Script

**Duration:** ~8-10 minutes
**Purpose:** Portfolio demonstration of RAG-enhanced multi-agent system

---

## INTRO (30 seconds)

**[Screen: GitHub repo or project folder]**

> "Hey everyone! Today I'm going to walk you through EssayMentor AI - a multi-agent system I built that uses RAG, or Retrieval-Augmented Generation, to generate high-quality college application essays.
>
> The system uses 7 specialized AI agents working together, a vector database with 150 real essay examples, and local LLMs through Ollama. Let me show you how it all works."

---

## PART 1: Architecture Overview (1.5 minutes)

**[Screen: Show the README.md or draw the pipeline]**

> "First, let's look at the architecture. The system has 7 agents in a pipeline:"

**[Highlight each agent as you mention it]**

```
Profile → RAG Retrieval → Research → Brainstorm → Outline → Draft → Critique
```

> "1. **Profile Agent** - Analyzes the student's background and selects their most compelling experiences
>
> 2. **RAG Retrieval Agent** - This is the key innovation. It searches a vector database of 150 successful essays to find similar examples
>
> 3. **Research Agent** - Analyzes what the essay prompt is really asking for
>
> 4. **Brainstorm Agent** - Generates creative angles, now informed by the successful examples from RAG
>
> 5. **Outline Agent** - Creates a detailed structure, learning from patterns in successful essays
>
> 6. **Draft Agent** - Writes the complete essay
>
> 7. **Critique Agent** - Provides feedback and suggestions
>
> The magic is in step 2 - RAG. Let me show you how it works."

---

## PART 2: Vector Database Explained (2 minutes)

**[Screen: Open `vector_db/embeddings.py`]**

> "The RAG system starts with embeddings. An embedding converts text into a vector - an array of 384 numbers that captures the semantic meaning."

**[Highlight the EmbeddingGenerator class]**

```python
class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

> "We use the sentence-transformers library with the MiniLM model. It's fast, runs locally, and produces good quality embeddings."

**[Screen: Open `vector_db/chromadb_manager.py`]**

> "These embeddings are stored in ChromaDB, an embedded vector database. Here's how we search for similar essays:"

**[Highlight search_similar_essays method]**

```python
def search_similar_essays(self, query: str, n_results: int = 5):
    query_embedding = self.embedding_gen.generate_embedding(query)
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results
```

> "When a user submits an essay prompt, we convert it to an embedding and find the closest matches in our database of 150 successful essays. Similar meaning equals similar vectors."

---

## PART 3: RAG Agent Integration (1.5 minutes)

**[Screen: Open `agents/rag_retrieval_agent.py`]**

> "Now let's see how RAG integrates into the agent pipeline."

**[Highlight the main function]**

```python
def rag_retrieval_agent(state: EssayState) -> dict:
    # Build search query from profile + prompt
    search_query = create_search_query(state)

    # Search vector database
    results = db_manager.search_similar_essays(
        query=search_query,
        n_results=5
    )

    # Format for downstream agents
    rag_context = format_retrieved_essays(results, state)

    return {
        "retrieved_essays": results,
        "rag_context": rag_context
    }
```

> "The RAG agent creates a search query from the student's profile and essay prompt, retrieves the 5 most similar successful essays, and formats them for the brainstorm and outline agents to learn from."

**[Screen: Open `agents/brainstorm_agent.py`]**

> "Here's how the brainstorm agent uses the RAG context:"

**[Highlight the rag_section in the prompt]**

```python
rag_section = f"""
{rag_context}

LEARNING FROM EXAMPLES:
Based on the successful essays above, notice:
- How they open with specific, vivid moments
- How they weave personal experience with broader themes
- Their authentic voice and natural storytelling
"""
```

> "Instead of generating ideas from scratch, the agent now learns from proven patterns in successful essays. This dramatically improves quality."

---

## PART 4: Live Demo - Running the Tests (3 minutes)

**[Screen: Terminal in project directory]**

> "Now let's run the test suite and see the RAG system in action."

**[Type and run:]**
```bash
./venv_py312/Scripts/python.exe test_rag_system.py
```

> "This test script validates all components of the RAG system."

**[Wait for Test 1 to complete]**

> "Test 1 checks that all modules import correctly - embeddings, ChromaDB manager, sample loader, and the RAG agent."

**[Wait for Test 2 - Embeddings]**

> "Test 2 demonstrates embeddings. Watch the similarity scores:
> - 'coding journey' vs 'programming experience' - 0.827, very similar!
> - 'coding journey' vs 'playing basketball' - 0.246, not similar at all.
>
> This is how we find semantically related essays."

**[Wait for Test 3 - ChromaDB]**

> "Test 3 verifies ChromaDB operations - adding essays, searching, and retrieving results."

**[Wait for Test 5 - Database Population]**

> "Test 5 loads all 150 essays from our essay_suites folder into the vector database. Each essay gets embedded and stored with metadata like topic, score, and target university."

**[Wait for Test 6 - RAG Retrieval]**

> "Test 6 is the key one. We simulate a student applying to MIT with a coding-related prompt. Watch what happens..."

**[Point to the retrieved essays]**

> "The RAG agent found 5 relevant essays:
> - Raj Malhotra's MIT essay about architecture
> - Alex Kim's MIT computer science essay
> - Maya Chen's MIT coding essay
> - Maria Santos's MIT coding essay
>
> All high-quality essays (score 9.0) targeting the same university with similar themes. This context now informs the essay generation."

**[Wait for Test 7 and Summary]**

> "Test 7 runs various search queries to verify the semantic search works across different topics.
>
> And there we go - 7 out of 7 tests passed! The RAG system is fully operational."

---

## PART 5: The Workflow (1 minute)

**[Screen: Open `agents/workflow.py`]**

> "Let me quickly show how it all connects in LangGraph:"

**[Highlight the workflow creation]**

```python
def create_essay_workflow():
    workflow = StateGraph(EssayState)

    # Add all agents as nodes
    workflow.add_node("profile", profile_agent)
    workflow.add_node("rag", rag_retrieval_agent)      # RAG here!
    workflow.add_node("research", research_agent)
    workflow.add_node("brainstorm", brainstorm_agent)
    workflow.add_node("outline", outline_agent)
    workflow.add_node("draft", draft_agent)
    workflow.add_node("critique", critique_agent)

    # Define the flow
    workflow.add_edge("profile", "rag")
    workflow.add_edge("rag", "research")
    # ... continues through all agents
```

> "LangGraph orchestrates the entire pipeline. Each agent receives state from the previous one, adds its contribution, and passes it forward. The RAG context flows through to inform multiple downstream agents."

---

## PART 6: Results & Impact (1 minute)

**[Screen: Show the evaluation module or a comparison]**

> "So what's the impact of RAG? Our evaluation shows approximately 25% improvement in essay quality across metrics like:
> - **Authenticity** - More specific details learned from examples
> - **Structure** - Better narrative arcs from proven patterns
> - **Engagement** - Stronger openings inspired by successful hooks
>
> The key insight: instead of generating essays from scratch, we're teaching the LLM what works by showing it real examples. That's the power of Retrieval-Augmented Generation."

---

## OUTRO (30 seconds)

**[Screen: GitHub repo]**

> "That's EssayMentor AI - a 7-agent system with RAG that generates personalized college essays by learning from successful examples.
>
> Key technologies used:
> - LangGraph for agent orchestration
> - ChromaDB for vector storage
> - Sentence-transformers for embeddings
> - Ollama for local LLM inference
>
> The code is on GitHub - link in the description. Thanks for watching!"

---

## RECORDING TIPS

### Before Recording
1. Clear terminal history
2. Make sure `chroma_db/` folder is deleted (so test populates fresh)
3. Have VS Code open with relevant files ready
4. Test the script runs without errors first

### Screen Layout
- Terminal on one side
- VS Code on the other
- Use zoom/highlights when showing code

### Commands to Run
```bash
# Clear database for fresh demo
rm -rf chroma_db/

# Activate environment
./venv_py312/Scripts/activate

# Run test
python test_rag_system.py
```

### Files to Show
1. `README.md` - Architecture overview
2. `vector_db/embeddings.py` - EmbeddingGenerator class
3. `vector_db/chromadb_manager.py` - search_similar_essays method
4. `agents/rag_retrieval_agent.py` - main function
5. `agents/brainstorm_agent.py` - rag_section usage
6. `agents/workflow.py` - workflow creation

### Key Points to Emphasize
- 7 specialized agents (not just one prompt)
- 150 real essays in vector database
- Semantic search finds similar meaning, not just keywords
- RAG improves quality by ~25%
- Runs entirely locally (privacy)

---

## THUMBNAIL IDEAS

1. "7 AI Agents + RAG = Better Essays"
2. Split screen: Vector database on left, generated essay on right
3. Pipeline diagram with RAG highlighted
4. "From 150 Examples to 1 Perfect Essay"
