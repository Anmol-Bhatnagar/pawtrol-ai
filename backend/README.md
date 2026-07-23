# Backend Agent Service

An enterprise-ready AI Agent microservice template built on top of **FastAPI**, **LangGraph (LangChain)**, and **Pydantic**.

This project provides a clean, modular structure for orchestrating agent cognitive networks using conditional flows, persistent state memory checkpointers, and vector stores, optimized for containerized environments.

---

## Project Structure

```text
backend/
├── .github/workflows/        # CI/CD pipelines (testing, linting, deployment)
│   └── ci.yml
├── docker/                   # Dockerfiles
│   ├── Dockerfile.dev        # Dev build with live reloading
│   └── Dockerfile.prod       # Lean multi-stage prod build
├── src/                      # Application Source
│   ├── config/               # Settings & logging
│   │   ├── settings.py
│   │   └── logging_cfg.py
│   ├── agents/               # Cognitive graph layer
│   │   ├── prompts/          # Version-controlled prompt templates
│   │   │   ├── system_base.txt
│   │   │   └── tool_selector.txt
│   │   ├── tools/            # Custom agent tools
│   │   │   ├── __init__.py
│   │   │   └── search_tool.py
│   │   ├── state.py          # State dictionary schema
│   │   ├── nodes.py          # State transitions & LLM node wrappers
│   │   ├── edges.py          # Routing decisions
│   │   └── graph.py          # Compiled execution flow
│   ├── api/                  # API Transport (FastAPI)
│   │   ├── dependencies/     # Dependency injection (Auth)
│   │   │   └── auth.py
│   │   ├── middlewares/      # Interceptors (Correlation request-id)
│   │   │   └── tracing.py
│   │   ├── routers/          # Endpoints
│   │   │   ├── health.py
│   │   │   └── v1_chat.py
│   │   └── schemas/          # Data schemas (Pydantic models)
│   │       └── chat.py
│   ├── services/             # Integrations (Vector DB & memory checkpoints)
│   │   ├── memory.py
│   │   └── vector_store.py
│   ├── app.py                # FastAPI Application setup
│   └── main.py               # Process launcher
├── tests/                    # Testing Framework (pytest)
│   ├── conftest.py
│   ├── integration/          # API endpoint tests
│   └── unit/                 # Nodes, edges, tools validation
├── .env.example              # Key templates
├── .dockerignore             # Exclude files from containers
├── pyproject.toml            # Poetry configurations
└── README.md
```

---

## Setup & Local Run

### Prerequisites
- Python 3.11+
- Poetry (recommended) or pip + venv

### 1. Configure the Environment
Copy the example environment template:
```bash
cp .env.example .env
```
Fill out the required parameters in `.env`.

### 2. Install Dependencies
```bash
poetry install
```

### 3. Run the Server Locally
To start the development server with live reload:
```bash
poetry run python src/main.py
```
Or run Uvicorn directly:
```bash
poetry run uvicorn src.app:app --reload
```

---

## Docker Execution

### Development Container
```bash
docker build -f docker/Dockerfile.dev -t backend:dev .
docker run -p 8000:8000 -v $(pwd):/app backend:dev
```

### Production Container (Lean Multi-Stage)
```bash
docker build -f docker/Dockerfile.prod -t backend:latest .
docker run -p 8000:8000 backend:latest
```

---

## Testing & Quality

Run the test suite using `pytest`:
```bash
poetry run pytest
```

Execute code linting & formatting checks:
```bash
poetry run ruff check src/ tests/
poetry run ruff format --check src/ tests/
```
