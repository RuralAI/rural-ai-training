# AI Training Catalog

An agent-based system that **discovers free and open-source AI training content** across the web, ingests and rationalises it, and **generates best-practices training curricula** covering both technical and business AI skills — contextualized for **rural communities**.

## Live Pages

- **[AI Resource Catalog](https://ruralai.github.io/rural-ai-training/catalog.html)** — Searchable catalog of 269+ free AI training resources
- **[ML Basics — Rural Edition](https://ruralai.github.io/rural-ai-training/rural_course.html)** — Machine learning course adapted for rural contexts
- **[Home Page](https://ruralai.github.io/rural-ai-training/)** — Landing page with links to all resources

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          CLI (cli.py)                       │
│              discover  │  ingest  │  generate               │
├──────────────┬─────────┴──────────┴──────────┬──────────────┤
│ Discovery    │     Ingestion Pipeline        │  Curriculum  │
│ Agent        │                               │  Generator   │
│  ├ Google    │  ├ HTML Scraper               │  ├ Learning  │
│  ├ GitHub    │  ├ Deduplicator               │  │  Paths    │
│  ├ arXiv     │  └ Categoriser                │  └ Best      │
│  └ Evaluator │                               │   Practices  │
├──────────────┴───────────────────────────────┴──────────────┤
│                    Resource Catalog                          │
│              JSON Storage  │  Repository Layer               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Discovery Agent

Searches multiple sources for free AI training content:

- **Google Custom Search** — broad web search with AI-training-focused queries
- **GitHub** — repositories tagged with ML/AI tutorial topics, sorted by stars
- **arXiv** — survey and tutorial papers in AI/ML categories

Each result is scored on a 0–1 quality scale based on provider reputation, keyword relevance, content type, community signals, freshness, and description quality.

### 2. Ingestion & Rationalisation Pipeline

- **HTML Scraper** — extracts main content, headings, code blocks, and links
- **Deduplicator** — detects near-duplicate content using trigram Jaccard similarity
- **Categoriser** — refines domain/tag assignments using full-text keyword analysis against the skill taxonomy

### 3. Curriculum Generator

- Groups resources by skill domain and difficulty level
- Builds sequenced **learning paths** (beginner → intermediate → advanced)
- Enforces **best-practice rules**:
  - Hands-on content in every path
  - Beginner paths capped at 20 hours
  - Advanced paths include research papers
  - Business paths include case studies
  - Provider diversity (no single provider > 40%)
  - All paths declare prerequisites

## Skill Domains

**Technical:** ML Basics, Deep Learning, NLP, Computer Vision, MLOps, Generative AI, Reinforcement Learning, Data Engineering

**Business:** AI Strategy, AI Ethics, AI Project Management, AI ROI, AI Governance

## Installation

```bash
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ATC_GOOGLE_API_KEY` | For Google search | Google Custom Search API key |
| `ATC_GOOGLE_CSE_ID` | For Google search | Custom Search Engine ID |
| `ATC_GITHUB_TOKEN` | Recommended | GitHub PAT for higher rate limits |

## Usage

### Discover AI training resources

```bash
# Search all domains
ai-catalog discover

# Search specific domains
ai-catalog discover --domains ml_basics,deep_learning,ai_strategy

# Limit results per query
ai-catalog discover --domains nlp --max-results 5
```

### Ingest and rationalise content

```bash
# Ingest all resources above quality threshold
ai-catalog ingest --min-score 0.4

# Ingest a specific resource
ai-catalog ingest --resource-id abc123
```

### Generate a curriculum

```bash
# Generate a full curriculum
ai-catalog generate

# Generate for specific domains
ai-catalog generate --domains ml_basics,deep_learning --title "ML Fundamentals"

# Write to a specific file
ai-catalog generate --output my_curriculum.json
```

### Manage the catalog

```bash
# View statistics
ai-catalog catalog stats

# List resources
ai-catalog catalog list --domain ml_basics --min-score 0.5

# Export full catalog
ai-catalog catalog export --output catalog.json
```

## Project Structure

```
src/ai_training_catalog/
├── cli.py                 # CLI entry point
├── config.py              # Central configuration (env vars)
├── models/                # Pydantic data models
│   ├── resource.py        # Resource, SkillDomain, enums
│   ├── curriculum.py      # Curriculum, LearningPath, ModuleUnit
│   └── taxonomy.py        # Skill taxonomy with keywords
├── discovery/             # Component 1: Content Discovery
│   ├── agent.py           # Discovery orchestrator
│   ├── evaluator.py       # Quality scoring engine
│   ├── catalog.py         # In-memory catalog wrapper
│   └── searchers/         # Search backends
│       ├── google_search.py
│       ├── github_search.py
│       └── arxiv_search.py
├── ingestion/             # Component 2: Content Ingestion
│   ├── pipeline.py        # Ingestion orchestrator
│   ├── deduplicator.py    # Near-duplicate detection
│   ├── categorizer.py     # Full-text categorisation
│   └── scrapers/          # Content extraction
│       └── html_scraper.py
├── curriculum/            # Component 3: Curriculum Generation
│   ├── generator.py       # Curriculum orchestrator
│   ├── learning_path.py   # Path builder with sequencing
│   └── best_practices.py  # Validation rules engine
├── storage/               # Persistence layer
│   ├── json_store.py      # Atomic JSON file ops
│   └── repository.py      # Resource & Curriculum repos
└── utils/                 # Shared utilities
    ├── http_client.py     # Async HTTP with retry
    ├── rate_limiter.py    # Per-domain rate limiting
    ├── text_processing.py # Normalisation & similarity
    └── logging.py         # Structured logging
```

## How It Works

1. **`discover`** generates search queries from the skill taxonomy, fans them out to all searchers concurrently, deduplicates by URL, scores each result, and stores qualifying resources in the catalog.

2. **`ingest`** scrapes full content from catalogued resources, detects and flags near-duplicates, refines domain assignments using full-text analysis, and estimates study hours.

3. **`generate`** groups resources by domain and difficulty, builds sequenced learning paths, validates against best-practice rules, and outputs a structured curriculum JSON.
