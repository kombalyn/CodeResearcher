# code-researcher · JavaScript / TypeScript

Search GitHub for real code examples and inject them as context into LLM prompts.

## Installation

```bash
npm install
```

## Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**Free mode** (no token needed):
```env
GITHUB_TOKEN=
RESEARCHER_USE_GREP_APP=true
```

**Paid mode** (higher GitHub rate limits):
```env
GITHUB_TOKEN=ghp_your_token_here
RESEARCHER_MAX_RESULTS=10
```

Getting a token: [github.com/settings/tokens](https://github.com/settings/tokens) — check only `public_repo` scope.

## CLI Usage

```bash
# Basic (TypeScript, free mode)
npx ts-node cli.ts "fetch JSON REST API typescript"

# Rust examples
npx ts-node cli.ts "async http reqwest" --language rust

# Python examples, paid mode
npx ts-node cli.ts "google search scraping" --language python --paid

# More results
npx ts-node cli.ts "websocket server" --max 5
```

## Library Usage

```typescript
import { CodeResearcher } from "./src";

// Free mode (auto-detected if no GITHUB_TOKEN in .env)
const researcher = new CodeResearcher();
const result = await researcher.search("fetch JSON API typescript", "typescript");

console.log(`Found ${result.found} examples (mode: ${result.mode})`);
console.log(result.contextBlock);   // inject into LLM prompt

// Paid mode
const researcher2 = new CodeResearcher({ githubToken: "ghp_..." });
const result2 = await researcher2.search("async reqwest", "rust");
```

## Build

```bash
npm run build   # compiles TypeScript to dist/
```
