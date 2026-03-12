# Free vs Paid Mode

code-researcher works in two modes. The difference is only about GitHub API rate limits — **no money is involved in either mode**.

---

## Free Mode

**No token, no account needed.**

| Source | Rate Limit | Notes |
|---|---|---|
| GitHub Code Search | 60 requests/hour (per IP) | Unauthenticated |
| grep.app | No limit | Always free |
| StackOverflow | No limit | Always free |

**When to use free mode:**
- Development and testing
- Occasional searches (a few times per hour)
- CI/CD pipelines on a dedicated IP

**Limitation:** The 60 req/hour GitHub limit is shared across all unauthenticated requests from your IP. In practice, each `search()` call uses 1–3 GitHub API requests, so you can run ~20–60 searches per hour in free mode.

**grep.app** is a reliable fallback that **never has rate limits** and doesn't require any token. It's always enabled and runs automatically if GitHub results are insufficient.

---

## Paid Mode

**Requires a GitHub Personal Access Token (PAT). GitHub accounts are free.**

| Source | Rate Limit | Notes |
|---|---|---|
| GitHub Code Search | 5,000 requests/hour | Authenticated |
| grep.app | No limit | Always free |
| StackOverflow | No limit | Always free |

**When to use paid mode:**
- Production agentic pipelines
- High-frequency searches (e.g. a new search per agent step)
- When free mode rate limit is hit

---

## How to Get a GitHub Token (5 minutes, free)

1. Log in to GitHub (create a free account if needed: [github.com](https://github.com))
2. Go to **Settings → Developer settings → Personal access tokens → Tokens (classic)**
3. Click **"Generate new token (classic)"**
4. Set a name (e.g. `code-researcher`)
5. Set expiration (90 days recommended, or "No expiration")
6. Under **Select scopes**, check only: ✅ `public_repo`
   - This gives read-only access to public repositories
   - No access to private repos, no write access
7. Click **"Generate token"**
8. Copy the `ghp_...` string — **save it now, you won't see it again**

---

## Setting the Token

### Python / TypeScript

Add to your `.env` file:

```env
GITHUB_TOKEN=ghp_your_token_here
```

That's it. The library auto-detects the token and switches to paid mode.

### Rust

Same — add to `.env` in the project root:

```env
GITHUB_TOKEN=ghp_your_token_here
```

### Explicit in code (Python)

```python
from code_researcher import CodeResearcher

# Explicit token
researcher = CodeResearcher(github_token="ghp_...")

# Or from environment (auto-detected)
researcher = CodeResearcher()
```

### Explicit in code (TypeScript)

```typescript
const researcher = new CodeResearcher({ githubToken: "ghp_..." });
// or from .env:
const researcher = new CodeResearcher();
```

---

## Mode Override

You can force a specific mode regardless of token presence:

```env
# .env
RESEARCHER_MODE=free    # always free, even if token is present
RESEARCHER_MODE=paid    # will error if no token
```

---

## Result Count Differences

| Setting | Free | Paid |
|---|---|---|
| Default max results | 3 | 10 |
| Override via env | `RESEARCHER_MAX_RESULTS=5` | `RESEARCHER_MAX_RESULTS=15` |
| Override in code | `CodeResearcher(max_results=5)` | `CodeResearcher(max_results=15)` |
