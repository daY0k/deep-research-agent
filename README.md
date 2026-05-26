# Deep Research Agent

A multi-agent AI system that researches any topic by deploying specialized agents in parallel — built on **Claude claude-sonnet-4-6** and the **Anthropic SDK**.

![Architecture](https://img.shields.io/badge/Claude-claude--sonnet--4--6-blueviolet) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│           Orchestrator Agent            │
│   Decomposes question → 3-5 sub-queries │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
  [Researcher] [Researcher] [Researcher]   ← parallel
        │         │         │
        └─────────┼─────────┘
                  ▼
         ┌────────────────┐
         │  Critic Agent  │
         │ Gaps · Issues  │
         └───────┬────────┘
                 ▼
       ┌──────────────────┐
       │ Synthesizer Agent│
       │   Final Report   │
       └──────────────────┘
```

Each agent is an independent Claude instance with its own system prompt and tool set.

## Features

- **Parallel research** — multiple Researcher agents run simultaneously
- **Self-critique** — Critic agent identifies gaps and contradictions
- **Structured reports** — Markdown output with Executive Summary, Key Findings, Analysis, Sources
- **Web search** — built-in DuckDuckGo search + page fetcher (no API key)
- **Session memory** — tracks all agent steps with timestamps
- **Streamlit UI** — live agent log, tabbed results, Markdown download
- **CLI support** — run headless from terminal

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/deep-research-agent
cd deep-research-agent

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Web UI
streamlit run ui/app.py

# CLI
python -m src.cli "What are the best practices for building AI agents in 2025?"
```

## CLI Usage

```bash
python -m src.cli "Your research question here"
```

Output is saved to `report_<timestamp>.md`.

## Project Structure

```
deep-research-agent/
├── src/
│   ├── agents/
│   │   ├── base.py          # Base agent (Claude + tool loop)
│   │   ├── orchestrator.py  # Decomposes query, runs pipeline
│   │   ├── researcher.py    # Web search + page reading
│   │   ├── critic.py        # Evaluates findings
│   │   └── synthesizer.py   # Writes final report
│   ├── tools/
│   │   └── web_search.py    # DuckDuckGo search + HTTP fetcher
│   └── memory/
│       └── session.py       # In-memory + optional JSON persistence
├── ui/
│   └── app.py               # Streamlit web interface
├── tests/
│   └── test_pipeline.py     # Integration tests
├── requirements.txt
├── .env.example
└── README.md
```

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Claude claude-sonnet-4-6 (Anthropic) |
| Agent framework | Custom (Anthropic SDK) |
| Web search | DuckDuckGo HTML · httpx · BeautifulSoup4 |
| UI | Streamlit |
| Memory | In-memory + JSON persistence |
| Language | Python 3.11+ |

## Why This Project

Demonstrates core AI engineering skills:
- **Agentic design patterns** — orchestrator/worker decomposition
- **Tool use** — Claude tool_use API with real web search
- **Async concurrency** — parallel agent execution with `asyncio.gather`
- **Multi-turn conversations** — proper message history management
- **Production patterns** — error handling, memory, streaming-ready architecture

## License

MIT
