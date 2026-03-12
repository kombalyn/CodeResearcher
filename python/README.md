# code-researcher · Python

Search GitHub for real code examples and inject them as context into LLM prompts or agentic pipelines.

## Installation

```bash
pip install requests python-dotenv

# Optional: LangChain integration
pip install langchain langchain-core langchain-openai langgraph
```

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**Free mode** (no token needed):
```env
# .env – leave GITHUB_TOKEN empty
GITHUB_TOKEN=
RESEARCHER_USE_GREP_APP=true
```

**Paid mode** (higher GitHub rate limits):
```env
# .env
GITHUB_TOKEN=ghp_your_token_here
RESEARCHER_MAX_RESULTS=10
```

Getting a GitHub token (free, 5 minutes):
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Check only `public_repo` scope
4. Paste the `ghp_...` token into `.env`

## CLI Usage

```bash
# Basic search (free mode)
python cli.py "google search stock earnings date python requests"

# Specify language
python cli.py "async http client reqwest" --language rust
python cli.py "fetch API JSON" --language typescript

# Force paid mode (uses GITHUB_TOKEN from .env)
python cli.py "sqlite orm python" --paid

# More results
python cli.py "beautifulsoup html parsing" --max 5

# Include StackOverflow results
python cli.py "regex date extraction python" --stackoverflow
```

## Library Usage

```python
from code_researcher import CodeResearcher

# Free mode (auto-detected if no GITHUB_TOKEN in .env)
researcher = CodeResearcher()
result = researcher.search("google search stock earnings date python")

print(f"Found {result.found} examples (mode: {result.mode})")
print(result.context_block)   # inject this into your LLM prompt

# Paid mode (explicit token)
researcher = CodeResearcher(github_token="ghp_...")
result = researcher.search("rust async reqwest JSON", language="rust")

# Access individual results
for r in result.results:
    print(f"[{r.source}] {r.repo} – {r.url}")
    print(r.code[:200])
```

## LangChain Integration

```python
from code_researcher.langchain_tool import CodeResearcherTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Create the tool (free mode by default)
research_tool = CodeResearcherTool()

# Add to any LangChain agent
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[research_tool])

# The agent will automatically call search_code_examples() before writing code
result = agent.invoke({"messages": [("user", "Write a Python script to scrape stock earnings dates")]})
```

See [examples/](../examples/) for full working examples.

## Free vs Paid

| | Free | Paid |
|---|---|---|
| GitHub rate limit | 60 req/h | 5,000 req/h |
| grep.app | ✅ Always free | ✅ Always free |
| StackOverflow | ✅ Always free | ✅ Always free |
| Max results | 3 | 10 |
| Token required | ❌ | ✅ GitHub PAT |

See [../docs/free-vs-paid.md](../docs/free-vs-paid.md) for full details.
