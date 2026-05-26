# Deep Research Agent

Multi-agent AI system that researches any topic: decomposes the question, runs parallel web searches, critiques findings, and synthesizes a structured report.

Built on **Claude claude-sonnet-4-6** + **Anthropic SDK**. No LangChain, no LlamaIndex — just the raw API.

[![Stars](https://img.shields.io/github/stars/daY0k/deep-research-agent?style=flat-square&color=171717)](https://github.com/daY0k/deep-research-agent/stargazers)
[![Python](https://img.shields.io/badge/Python-3.11+-171717?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-171717?style=flat-square)](LICENSE)

---

## How it works

```
User query
    │
    ▼
Orchestrator          decomposes into 3-5 sub-queries
    │
    ├── Researcher ─┐
    ├── Researcher  ├─ run in parallel, each does web_search + fetch_page
    └── Researcher ─┘
    │
    ▼
Critic                finds gaps, contradictions, weak sources
    │
    ▼
Synthesizer           writes the final Markdown report
```

Each agent is an independent Claude instance with its own system prompt and tool access. The Orchestrator just coordinates — it doesn't do the research itself.

---

## Features

- **Parallel agents** — researchers run concurrently via `asyncio.gather`, not one-by-one
- **Real web search** — DuckDuckGo HTML scraper + httpx page fetcher, zero API keys needed
- **Tool use** — proper Claude `tool_use` loop, not prompt stuffing
- **Self-critique** — dedicated Critic agent flags issues before the final report
- **Streamlit UI** — live agent log, tabbed output, one-click Markdown download
- **CLI** — headless mode, saves `report_TIMESTAMP.md`
- **Custom endpoints** — supports `ANTHROPIC_BASE_URL` for proxies

---

## Stack

| Layer | Tech |
|---|---|
| LLM | Claude claude-sonnet-4-6 |
| SDK | `anthropic` (official) |
| Concurrency | `asyncio` + `asyncio.gather` |
| Web | `httpx` + `beautifulsoup4` |
| UI | Streamlit |
| Language | Python 3.11+ |

---

## Quick start

```bash
git clone https://github.com/daY0k/deep-research-agent
cd deep-research-agent

python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

**Web UI:**
```bash
streamlit run ui/app.py
```

**CLI:**
```bash
python3 -m src.cli "What are the best practices for building production AI agents?"
```

---

## Project layout

```
deep-research-agent/
├── src/
│   ├── agents/
│   │   ├── base.py          # Claude API wrapper with tool loop
│   │   ├── orchestrator.py  # Query decomposition + pipeline coordinator
│   │   ├── researcher.py    # Web search + page reading
│   │   ├── critic.py        # Findings evaluation
│   │   └── synthesizer.py   # Final report writer
│   ├── tools/
│   │   └── web_search.py    # DuckDuckGo + httpx fetcher + tool definitions
│   └── memory/
│       └── session.py       # Step logging with optional JSON persistence
├── ui/
│   └── app.py               # Streamlit interface
├── tests/
│   └── test_pipeline.py     # Unit tests (mocked API)
└── requirements.txt
```

---

## Why no LangChain

LangChain adds abstraction over things that don't need abstracting. The Anthropic SDK's `tool_use` loop is ~20 lines. Adding a framework on top would make the code harder to read and harder to interview about. Everything here is explicit.

---

## License

MIT
