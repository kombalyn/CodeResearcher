# 🔍 code-researcher

> Search GitHub for real code examples and inject them as context into your AI coding agents.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](python/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](javascript/)
[![Rust](https://img.shields.io/badge/Rust-1.75+-orange.svg)](rust/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is this?

**code-researcher** is a multi-language library that searches GitHub (and optionally StackOverflow, PyPI/npm) for real-world code examples relevant to a programming task, then formats them as context blocks ready to be injected into LLM prompts or agentic coding pipelines.

Instead of an AI agent starting from scratch, it can **learn from existing open-source code** before writing a single line.

```
Your task description
       ↓
  code-researcher
  → GitHub Code Search
  → Download top N Python/JS/Rust files
  → Format as context block
       ↓
LLM prompt enriched with real code examples
       ↓
Better, more accurate generated code
```

---

## Features

- 🐍 **Python** library + CLI
- 🟨 **JavaScript/TypeScript** library + CLI  
- 🦀 **Rust** library + CLI
- 🆓 **Free mode** – works without any API token (rate limited)
- 💰 **Paid mode** – GitHub token for higher rate limits + more results
- 🤖 **LangChain integration** – drop-in tool for ReAct agents
- 🔌 **Agentic pipeline ready** – works with any LLM framework

---

## Free vs Paid Mode

| Feature | Free Mode | Paid Mode |
|---|---|---|
| GitHub Code Search | ✅ 60 req/hour (unauthenticated) | ✅ 5,000 req/hour (with token) |
| grep.app search | ✅ No token needed | ✅ No token needed |
| StackOverflow API | ✅ No token needed | ✅ No token needed |
| PyPI / npm READMEs | ✅ No token needed | ✅ No token needed |
| Results per search | Up to 3 files | Up to 10 files |
| Concurrent requests | 1 | 5 |

**Free mode** is suitable for occasional use and development. The 60 req/hour GitHub limit resets every hour and is shared across your IP.

**Paid mode** requires a GitHub Personal Access Token (free to create, no credit card needed). It only unlocks GitHub's higher rate limit — all other sources are always free.

> ⚠️ "Paid" here means you need a GitHub account and token, not that you pay money. GitHub tokens are free.

---

## Quick Start

See language-specific READMEs:

- [Python →](python/README.md)
- [JavaScript/TypeScript →](javascript/README.md)
- [Rust →](rust/README.md)

---

## LangChain Integration

See [examples/](examples/) for ready-to-use LangChain tool integrations:

- [General ReAct Agent](examples/langchain_react_agent.py)
- [Planner + Controller Pipeline](examples/langchain_planner_pipeline.py)

---

## Project Structure

```
code-researcher/
├── python/                  # Python library & CLI
│   ├── code_researcher/
│   │   ├── __init__.py
│   │   ├── searcher.py      # Core search logic
│   │   ├── sources/
│   │   │   ├── github.py    # GitHub Code Search
│   │   │   ├── grep_app.py  # grep.app (no token needed)
│   │   │   └── stackoverflow.py
│   │   └── langchain_tool.py  # LangChain Tool wrapper
│   ├── cli.py
│   ├── pyproject.toml
│   └── README.md
├── javascript/              # TypeScript/JavaScript library & CLI
│   ├── src/
│   │   ├── index.ts
│   │   ├── searcher.ts
│   │   └── sources/
│   │       ├── github.ts
│   │       └── grepApp.ts
│   ├── package.json
│   └── README.md
├── rust/                    # Rust library & CLI
│   ├── src/
│   │   ├── main.rs
│   │   ├── lib.rs
│   │   └── sources/
│   │       ├── github.rs
│   │       └── grep_app.rs
│   ├── Cargo.toml
│   └── README.md
├── examples/                # LangChain & agentic examples
│   ├── langchain_react_agent.py
│   └── langchain_planner_pipeline.py
├── docs/
│   ├── free-vs-paid.md
│   └── integration-guide.md
└── README.md
```

---

## License

MIT — use freely in commercial and open-source projects.
