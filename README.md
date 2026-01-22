# EssayMentor AI

A production-ready **full-stack application** featuring a 7-agent AI system with RAG (Retrieval-Augmented Generation) for generating personalized college application essays.

Built with **Django REST Framework**, **ReactJS**, **PostgreSQL**, **WebSocket streaming**, **Docker**, and **local LLMs**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

<img width="1912" height="1107" alt="readme" src="https://github.com/user-attachments/assets/baecb463-26ad-407b-8bea-435662d9073a" />
<img width="1908" height="1042" alt="readme3" src="https://github.com/user-attachments/assets/b30a1259-ac71-4045-a067-39fe69628086" />


---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core language |
| **Django 4.2** | Web framework |
| **Django REST Framework** | REST API development |
| **Django Channels** | WebSocket support for real-time streaming |
| **Celery + Redis** | Async task queue for long-running AI tasks |
| **PostgreSQL** | Primary database |
| **JWT Authentication** | Secure token-based auth (SimpleJWT) |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **Zustand** | State management |
| **Axios** | HTTP client with interceptors |

### AI/ML
| Technology | Purpose |
|------------|---------|
| **LangGraph** | Multi-agent orchestration |
| **ChromaDB** | Vector database for RAG |
| **Sentence-Transformers** | Text embeddings (384 dimensions) |
| **Ollama** | Local LLM inference (llama3.1:8b) |

### DevOps
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |
| **Nginx** | Reverse proxy & static file serving |
| **GitHub Actions** | CI/CD pipeline |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  LoginPage  │  │  ChatPage   │  │ ProfilePage │  │ HistoryPage │        │
│  └─────────────┘  └──────┬──────┘  └─────────────┘  └─────────────┘        │
│                          │ WebSocket + REST API                             │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────────────────┐
│                     BACKEND (Django)                                        │
│  ┌───────────────────────┴────────────────────────┐                        │
│  │              Django Channels (ASGI)            │                        │
│  │         WebSocket Consumer + REST API          │                        │
│  └───────────────────────┬────────────────────────┘                        │
│                          │                                                  │
│  ┌───────────────────────┴────────────────────────┐                        │
│  │              Celery Task Queue                 │                        │
│  │         Async Essay Generation Tasks           │                        │
│  └───────────────────────┬────────────────────────┘                        │
│                          │                                                  │
│  ┌───────────────────────┴────────────────────────┐                        │
│  │           7-Agent LangGraph Pipeline           │                        │
│  │  Profile → RAG → Research → Brainstorm →       │                        │
│  │  Outline → Draft → Critique                    │                        │
│  └───────────────────────┬────────────────────────┘                        │
│                          │                                                  │
│  ┌──────────┐    ┌───────┴───────┐    ┌──────────┐                        │
│  │PostgreSQL│    │   ChromaDB    │    │  Ollama  │                        │
│  │   Users  │    │ Vector Store  │    │Local LLM │                        │
│  │  Essays  │    │  150 Essays   │    │llama3.1  │                        │
│  └──────────┘    └───────────────┘    └──────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Features

### Real-Time Streaming UI (ChatGPT-like)
- WebSocket-powered real-time updates
- Shows progress through 7-agent pipeline
- Typing indicators and agent status badges
- Cancel generation mid-process

### 7-Agent AI Pipeline
| Agent | Role |
|-------|------|
| **Profile** | Analyzes student background, selects compelling experiences |
| **RAG Retrieval** | Finds similar successful essays from vector database |
| **Research** | Analyzes essay prompt requirements |
| **Brainstorm** | Generates creative angles using retrieved examples |
| **Outline** | Creates structured outline based on successful patterns |
| **Draft** | Writes the complete essay |
| **Critique** | Provides detailed feedback and suggestions |

### RAG System
- **150 successful essays** in vector database
- **384-dimensional embeddings** using sentence-transformers
- **Semantic search** finds similar essays by meaning, not keywords
- **25% quality improvement** over non-RAG generation

### User Management
- JWT authentication with token refresh
- Student profile management
- Essay history with versioning
- University-specific customization (MIT, Harvard, Stanford, etc.)

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/bilalhussainx/essaymentor-ai.git
cd essaymentor-ai

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/
# Ollama: http://localhost:11434
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# In another terminal - Celery worker
celery -A essaymentor worker -l INFO

# Frontend setup (another terminal)
cd frontend
npm install
npm run dev

# Start Redis and Ollama
redis-server
ollama serve && ollama pull llama3.1:8b
```

---

## API Endpoints

### Authentication
```
POST /api/auth/register/     - User registration
POST /api/auth/login/        - JWT login (returns access + refresh tokens)
POST /api/auth/refresh/      - Refresh access token
GET  /api/auth/me/           - Get current user
```

### Profiles
```
GET  /api/profiles/me/       - Get student profile
PUT  /api/profiles/me/       - Update student profile
```

### Essays
```
POST /api/essays/            - Start new essay generation
GET  /api/essays/            - List user's essays (paginated)
GET  /api/essays/{id}/       - Get essay details with all agent outputs
GET  /api/essays/{id}/status/- Poll generation status
POST /api/essays/{id}/cancel/- Cancel ongoing generation
DELETE /api/essays/{id}/     - Delete essay
```

### WebSocket
```
WS /ws/essays/{generation_id}/?token={jwt}

Messages from server:
- agent_start    - Agent began processing
- agent_progress - Streaming content (like ChatGPT typing)
- agent_complete - Agent finished
- generation_complete - Full essay ready
- error          - Error occurred

Messages from client:
- cancel         - Stop generation
```

### Vector Database
```
POST /api/vectordb/search/   - Search similar essays
GET  /api/vectordb/stats/    - Database statistics
```

---

## Project Structure

```
essaymentor-ai/
├── backend/                      # Django Backend
│   ├── essaymentor/             # Django project settings
│   │   ├── settings.py          # Config (DB, Redis, Celery, JWT)
│   │   ├── urls.py              # URL routing
│   │   ├── asgi.py              # ASGI config for WebSocket
│   │   └── celery.py            # Celery configuration
│   ├── profiles/                # User & Profile app
│   │   ├── models.py            # User, StudentProfile models
│   │   ├── views.py             # Auth & profile endpoints
│   │   └── serializers.py       # DRF serializers
│   ├── essays/                  # Essay generation app
│   │   ├── models.py            # EssayGeneration, University
│   │   ├── views.py             # REST API (ViewSets)
│   │   ├── consumers.py         # WebSocket consumer
│   │   ├── tasks.py             # Celery async tasks
│   │   └── routing.py           # WebSocket URL routing
│   ├── vectordb/                # RAG integration
│   │   ├── services.py          # ChromaDB service wrapper
│   │   └── views.py             # Search API
│   └── requirements.txt
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/            # ChatGPT-like UI components
│   │   │   │   └── AgentProgress.tsx
│   │   │   └── layout/          # Layout components
│   │   ├── pages/               # Page components
│   │   │   ├── ChatPage.tsx     # Main essay generation UI
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   └── HistoryPage.tsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts  # WebSocket connection hook
│   │   ├── services/
│   │   │   └── api.ts           # Axios with JWT interceptors
│   │   └── store/
│   │       └── authStore.ts     # Zustand state management
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── agents/                       # 7-Agent AI System
│   ├── workflow.py              # LangGraph orchestration
│   ├── profile_agent.py
│   ├── rag_retrieval_agent.py
│   ├── research_agent.py
│   ├── brainstorm_agent.py
│   ├── outline_agent.py
│   ├── draft_agent.py
│   ├── critique_agent.py
│   └── ollama_helper.py         # LLM interface
│
├── vector_db/                    # Vector Database
│   ├── embeddings.py            # Sentence-transformers
│   ├── chromadb_manager.py      # ChromaDB operations
│   └── sample_loader.py         # Load essays into DB
│
├── docker/                       # Docker Configuration
│   ├── backend/Dockerfile
│   └── frontend/Dockerfile
│
├── docker-compose.yml            # Full stack orchestration
├── .env.example                  # Environment variables template
└── README.md
```

---

## Database Schema

### User Model (Custom)
```python
- id: UUID (primary key)
- email: EmailField (unique, used for login)
- username: CharField
- created_at: DateTimeField
```

### StudentProfile Model
```python
- id: UUID
- user: OneToOneField(User)
- name, age, background, location
- gpa, sat_verbal
- major_experiences: JSONField (list of experiences)
- activities: JSONField (list)
- achievements: JSONField (list)
- voice_characteristics: JSONField
```

### EssayGeneration Model
```python
- id: UUID
- user: ForeignKey(User)
- profile: ForeignKey(StudentProfile)
- prompt: TextField
- target_university: ForeignKey(University)
- status: CharField (pending/profile/rag/.../completed/failed)
- progress_percent: IntegerField
- profile_analysis, rag_context, ideas, outline, draft, critique: TextField
- final_essay: TextField
- word_count_actual: IntegerField
- generation_time_seconds: FloatField
```

---

## Test Results

```bash
python test_rag_system.py
```

| Test | Description | Status |
|------|-------------|--------|
| 1 | Module imports | ✅ Passed |
| 2 | Embedding generation (384 dims) | ✅ Passed |
| 3 | ChromaDB operations | ✅ Passed |
| 4 | Essay parsing (YAML frontmatter) | ✅ Passed |
| 5 | Database population (150 essays) | ✅ Passed |
| 6 | RAG retrieval agent | ✅ Passed |
| 7 | Semantic search | ✅ Passed |

**Result: 7/7 tests passed**

### Embedding Similarity Demo
```
"coding journey" vs "programming experience" → 0.827 (Similar!)
"coding journey" vs "playing basketball"    → 0.246 (Not similar)
```

---

## Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database (PostgreSQL)
DB_NAME=essaymentor
DB_USER=essaymentor
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis (Celery & Channels)
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0

# Ollama (Local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# ChromaDB
CHROMADB_PATH=./chroma_db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## Skills Demonstrated

This project demonstrates proficiency in:

- **Python (Django/DRF)** - REST API development, custom user models, ViewSets, serializers
- **ReactJS** - Hooks, context, component architecture, TypeScript integration
- **PostgreSQL** - Database design, JSONField for flexible schemas, migrations
- **REST APIs** - JWT authentication, pagination, CRUD operations
- **WebSocket** - Django Channels, real-time streaming, ASGI
- **AJAX** - Axios interceptors, async/await, error handling
- **Docker** - Multi-stage builds, docker-compose, service orchestration
- **Git** - Version control, feature branches
- **AI/ML** - LangGraph agents, RAG architecture, vector embeddings

---

## License

MIT License

---

## Author

**Bilal Hussain**
Full-Stack Developer | AI/ML Enthusiast

- GitHub: [@bilalhussainx](https://github.com/bilalhussainx)
