# 🎯 Implementation Plan: Research Paper Agent with Email Delivery

## Architecture Overview

**Core Components:**
- **LangGraph** - Multi-agent orchestration framework for stateful workflows
- **Ollama** - Local LLM (recommend llama3 or mistral)
- **Qdrant** - Vector database for semantic search & memory
- **FastAPI** - Backend REST API
- **Gradio** - User interface
- **SMTP** - Email delivery system

---

## Phase 1: Foundation Setup (Week 1)

### 1.1 Dependencies & Environment

#### Core
- langgraph + langchain + langchain-community
- langchain-ollama (Ollama integration)
- ollama
- qdrant-client
- fastembed

#### Backend
- fastapi
- uvicorn
- pydantic
- python-dotenv

#### Email & Document
- aiosmtplib (async email)
- python-docx
- markdown
- jinja2 (email templates)

#### Search & Tools
- duckduckgo-search (open-source alternative)
- arxiv (for academic papers)
- scholarly (Google Scholar scraper)
- beautifulsoup4

### 1.2 Project Structure

```
Research-Paper-Agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── graph.py               # LangGraph workflow orchestration
│   │   ├── interface.py           # Gradio UI
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── literature_search.py
│   │   │   ├── paper_analysis.py
│   │   │   ├── data_synthesis.py
│   │   │   ├── writer.py
│   │   │   └── citation_manager.py
│   │   ├── edges/
│   │   │   ├── __init__.py
│   │   │   ├── routing.py          # Conditional routing logic
│   │   │   └── validation.py       # Edge validation functions
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── research_state.py   # State schema for the graph
│   │   │   └── models.py           # Pydantic models for state
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── research.py        # Research endpoints
│   │       ├── papers.py          # Paper search endpoints
│   │       └── config.py          # Configuration endpoints
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py              # Academic search tools
│   │   ├── database.py            # Qdrant vector DB operations
│   │   └── analysis.py            # Paper analysis tools
│   ├── utilities/
│   │   ├── __init__.py
│   │   ├── email.py               # Email sending service
│   │   ├── document.py            # Document generation
│   │   └── embeddings.py          # Embedding utilities
│   ├── server.py                  # FastAPI application
│   ├── pyproject.toml             # Poetry/project metadata
│   ├── ruff.toml                  # Ruff linter config
│   └── Dockerfile                 # Backend container
├── ollama/
│   ├── Dockerfile                 # Ollama LLM container
│   ├── README.md                  # Ollama documentation
│   └── start.sh                   # Ollama startup script
├── qdrant/
│   ├── Dockerfile                 # Qdrant vector DB container
│   ├── README.md                  # Qdrant documentation
│   ├── start.sh                   # Qdrant startup script
│   ├── init_collections.py        # Collection initialization
│   └── storage/                   # Persistent storage
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py              # Node unit tests
│   ├── test_edges.py              # Edge logic tests
│   ├── test_graph.py              # Graph workflow tests
│   ├── test_tools.py              # Tool unit tests
│   ├── test_email.py              # Email service tests
│   └── test_integration.py        # Integration tests
├── storage/
│   └── documents/                 # Generated research papers
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Multi-container orchestration
├── requirements.txt               # Python dependencies
├── Makefile                       # Build and run commands
├── README.md                      # Project documentation
├── SIMILAR.md                     # Reference documentation
├── IMPLEMENTATION_PLAN.md         # This file
└── LICENSE                        # Project license
```

---

## Phase 2: Core Graph System (Week 2-3)

### 2.1 Five Node Architecture

#### 1. Literature Search Node
- **Tools:** ArXiv API, Scholarly (Google Scholar), DuckDuckGo
- **State Updates:** Adds search results to research state
- **Output:** List of relevant papers with metadata

#### 2. Paper Analysis Node
- **Tools:** PDF parser, text extraction
- **State Updates:** Adds analyzed content to state
- **Output:** Structured summaries + key findings

#### 3. Data Synthesis Node
- **Tools:** Statistical analysis, trend detection
- **State Updates:** Adds insights and patterns to state
- **Output:** Research gaps, trends, synthesis

#### 4. Writer Node
- **Tools:** Template engine, markdown formatter
- **State Updates:** Generates paper sections in state
- **Output:** Structured research paper content

#### 5. Citation Manager Node
- **Tools:** Citation parser, formatter (APA/MLA/Chicago)
- **State Updates:** Adds formatted citations to state
- **Output:** Complete bibliography and references

### 2.2 State Management

#### Research State Schema
```python
class ResearchState(TypedDict):
    topic: str
    search_results: List[Paper]
    analyzed_papers: List[Analysis]
    synthesis: Synthesis
    paper_sections: Dict[str, str]
    citations: List[Citation]
    status: str
    current_node: str
```

#### Graph Flow
```
Start → Literature Search → Paper Analysis → Data Synthesis → Writer → Citation Manager → End
```

#### Conditional Edges
- Quality checks between nodes
- Retry logic for failed analyses
- Branching based on research complexity

---

## Phase 3: Email Delivery System (Week 3)

### 3.1 Email Service Architecture

#### Components
1. **SMTP Configuration** (support Gmail, Outlook, custom SMTP)
2. **Template System** (Jinja2 HTML emails)
3. **Attachment Handler** (DOCX, PDF, Markdown)
4. **Queue System** (async email sending)

#### Features
- HTML formatted emails with embedded summary
- Multiple attachment formats
- Delivery confirmation
- Retry logic for failures
- Email validation

### 3.2 Document Generation Pipeline

```
Research Complete → Generate DOCX/PDF → Create Email → Send → Log
```

#### Output Formats
- `.docx` - Formatted research paper
- `.pdf` - PDF version (via docx2pdf)
- `.md` - Markdown source
- Email body - Executive summary

---

## Phase 4: API & Integration (Week 4)

### 4.1 FastAPI Endpoints

```python
POST /api/research/start
  - Input: topic, citation_style, email
  - Returns: job_id
  
GET /api/research/status/{job_id}
  - Returns: progress, current_stage
  
POST /api/research/email
  - Input: job_id, email_address
  - Sends generated docs

GET /api/research/history
  - Returns: past research topics

POST /api/papers/search
  - Semantic search via Qdrant
  
POST /api/config/email
  - Configure SMTP settings
```

### 4.2 Gradio Interface

#### Tabs
1. **New Research** - Topic input, preferences
2. **Progress** - Real-time graph execution status
3. **Results** - Preview generated paper
4. **Email Setup** - SMTP configuration
5. **History** - Past research papers

---

## Phase 5: Open-Source Tool Integration (Week 5)

### 5.1 Ollama Configuration

#### Recommended Models

```yaml
Primary: llama3:70b or qwen2.5:32b
  - For main agent reasoning
  
Secondary: mistral:7b
  - For faster citation formatting
  
Embeddings: nomic-embed-text
  - For Qdrant vector search
```

#### Multi-Model Strategy
- Literature Review Node → llama3:70b
- Analysis/Writing → llama3:70b  
- Citation Node → mistral:7b (faster)

### 5.2 Qdrant Setup

```python
# Local deployment
docker run -p 6333:6333 qdrant/qdrant

# Or in your docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

#### Embedding Pipeline
- Use `fastembed` with `BAAI/bge-small-en-v1.5`
- Dimension: 384
- Distance: Cosine similarity

---

## Phase 6: Enhanced Features (Week 6)

### 6.1 Advanced Capabilities

#### 1. Human-in-the-Loop Review
- Approval step before email sending
- Edit generated sections
- Add custom notes

#### 2. Batch Processing
- Multiple topics in one session
- Scheduled research runs

#### 3. Citation Graph Visualization
- Network of paper relationships
- Most cited sources

#### 4. Custom Templates
- User-defined paper structures
- Institution-specific formatting

### 6.2 Email Advanced Features

#### 1. Rich HTML Emails
- Embedded charts/tables
- Branded templates
- Interactive table of contents

#### 2. Distribution Lists
- Send to multiple recipients
- CC/BCC support

#### 3. Scheduling
- Delayed sending
- Recurring research updates

---

## Key Configuration Files

### `.env` File

```ini
# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:70b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=research-agent@yourdomain.com

# App
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

---

## Development Workflow

- **Week 1:** Environment + basic structure
- **Week 2:** Node implementation + state management
- **Week 3:** Graph construction + Qdrant integration
- **Week 4:** Document generation + email service
- **Week 5:** API endpoints + Gradio UI
- **Week 6:** Ollama optimization + testing
- **Week 7:** Advanced features + deployment

---

## Testing Strategy

1. **Unit Tests** - Individual nodes & tools
2. **Graph Tests** - State transitions and routing logic
3. **Integration Tests** - Full research workflow
4. **Email Tests** - SMTP with test accounts
5. **Load Tests** - Multiple concurrent requests
6. **Vector Search Tests** - Qdrant performance

---

## Deployment Options

### Local Development

```bash
docker-compose up  # Ollama + Qdrant + Backend
```

### Production
- Docker Swarm or Kubernetes
- Nginx reverse proxy
- PostgreSQL for job metadata
- Redis for task queue

---

## Cost Analysis

### ✅ 100% Open Source Stack

- **Ollama:** Free (local compute)
- **Qdrant:** Free (self-hosted)
- **LangGraph:** Free (MIT license)
- **All libraries:** Free

### Only Costs
- Server compute (your hardware/VPS)
- Optional: Email service if using SendGrid/AWS SES

---

## Next Steps

1. Set up dependencies and project structure
2. Implement core graph system with LangGraph
3. Integrate Qdrant for semantic search and memory
4. Build email delivery service
5. Create FastAPI endpoints and Gradio UI
6. Test and optimize with Ollama models
7. Deploy and monitor

---

## Notes

This plan provides a production-ready research paper agent that's:
- ✅ 100% open-source
- ✅ Uses existing Ollama setup
- ✅ Integrates Qdrant for semantic search/memory
- ✅ Delivers formatted papers via email
- ✅ Scalable and maintainable architecture with LangGraph state management
