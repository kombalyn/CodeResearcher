# code-researcher · Rust

Search GitHub for real code examples and inject them as context into LLM prompts.

## Build & Run

```bash
cargo build --release

# CLI
cargo run -- "async http client reqwest"
cargo run -- "google search scraping" --language python
cargo run -- "websocket server tokio" --paid
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

**Paid mode**:
```env
GITHUB_TOKEN=ghp_your_token_here
```

Getting a token: [github.com/settings/tokens](https://github.com/settings/tokens) — `public_repo` scope only.

## Library Usage

```rust
use code_researcher::{CodeResearcher, ResearcherConfig};

#[tokio::main]
async fn main() {
    // Auto-loads from .env
    let config = ResearcherConfig::from_env();
    let researcher = CodeResearcher::new(config);

    let result = researcher.search("async http json reqwest", "rust").await;

    println!("Found {} examples (mode: {})", result.found, result.mode);
    println!("{}", result.context_block);  // inject into LLM prompt
}
```

## CLI Options

```
USAGE:
    code-researcher [OPTIONS] <QUERY>

ARGS:
    <QUERY>    Search query (English works best)

OPTIONS:
    -l, --language <LANGUAGE>    rust | python | typescript | javascript | go [default: rust]
        --paid                   Force paid mode (requires GITHUB_TOKEN in .env)
        --free                   Force free mode
        --max <MAX>              Max number of results
        --no-grep-app            Skip grep.app source
    -h, --help                   Print help
```
