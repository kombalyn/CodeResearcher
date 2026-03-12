# Integration Guide

How to integrate code-researcher into your LLM agent or coding pipeline.

---

## Pattern: Enrich task → pass to LLM

The simplest integration pattern: search for examples before sending a task to the LLM.

```python
from code_researcher import CodeResearcher

researcher = CodeResearcher()

def enrich_prompt(task: str) -> str:
    result = researcher.search(task, language="python")
    if result:
        return task + "\n\n" + result.context_block
    return task

# Before calling your LLM:
enriched = enrich_prompt("Write a web scraper for earnings dates")
llm_response = your_llm.invoke(enriched)
```

---

## Pattern: LangChain Tool

Drop-in tool for any LangChain ReAct agent:

```python
from code_researcher.langchain_tool import CodeResearcherTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

tool = CodeResearcherTool(language="python")
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[tool, ...])
```

The agent will call `search_code_examples("query")` autonomously when it decides context would help.

---

## Pattern: Per-step research in a planner pipeline

In a multi-step planner, research each step before execution:

```python
from code_researcher import CodeResearcher

researcher = CodeResearcher()

for step in plan.steps:
    if not step.is_install_step:
        result = researcher.search(step.controller_task)
        if result:
            step.controller_task += "\n\n" + result.context_block
    execute_step(step)
```

---

## TypeScript integration

```typescript
import { CodeResearcher } from "code-researcher";

const researcher = new CodeResearcher();

async function enrichPrompt(task: string): Promise<string> {
  const result = await researcher.search(task, "typescript");
  if (result.found > 0) {
    return task + "\n\n" + result.contextBlock;
  }
  return task;
}
```

---

## Rust integration

```rust
use code_researcher::{CodeResearcher, ResearcherConfig};

#[tokio::main]
async fn main() {
    let config = ResearcherConfig::from_env();
    let researcher = CodeResearcher::new(config);

    let result = researcher.search("async http client", "rust").await;
    if !result.is_empty() {
        let enriched_prompt = format!("{}\n\n{}", task, result.context_block);
        // pass enriched_prompt to your LLM
    }
}
```

---

## Tips for good search queries

- **Write queries in English** — GitHub code is almost entirely English
- **Be specific**: `"google search stock earnings date python requests beautifulsoup"` > `"web scraping"`
- **Include library names**: `"reqwest async json"` > `"http rust"`
- **Include the problem domain**: `"yfinance earnings date pandas"` > `"finance python"`
- **Avoid Hungarian/non-English** – search results will be empty
