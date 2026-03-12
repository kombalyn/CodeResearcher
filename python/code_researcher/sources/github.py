"""
GitHub Code Search source.

Free mode  : Unauthenticated API, 60 requests/hour limit.
Paid mode  : Authenticated with GitHub token, 5,000 requests/hour.

GitHub Code Search docs:
https://docs.github.com/en/rest/search/search#search-code
"""

import time
import requests
from typing import Optional
from ..config import ResearcherConfig


def search_github(
    query: str,
    language: str = "python",
    config: Optional[ResearcherConfig] = None,
) -> list[dict]:
    """
    Search GitHub for code files matching the query.

    Args:
        query:    Natural language or code search query
        language: Programming language filter (python, javascript, typescript, rust, ...)
        config:   ResearcherConfig instance

    Returns:
        List of dicts: {"repo", "file", "url", "code"}
    """
    if config is None:
        config = ResearcherConfig()

    results = []
    params = {
        "q": f"{query} language:{language}",
        "per_page": min(config.max_results * 3, 30),
        "sort": "indexed",
    }

    try:
        resp = requests.get(
            "https://api.github.com/search/code",
            headers=config.auth_headers,
            params=params,
            timeout=config.timeout,
        )

        if resp.status_code == 401:
            print("  [GitHub] Authentication failed. Check your GITHUB_TOKEN in .env")
            return []
        if resp.status_code == 403:
            remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            reset = resp.headers.get("X-RateLimit-Reset", "?")
            print(f"  [GitHub] Rate limit hit (remaining: {remaining}, resets: {reset})")
            if not config.is_paid:
                print("  [GitHub] Tip: Set GITHUB_TOKEN in .env to increase limit to 5,000 req/h")
            return []
        if resp.status_code == 422:
            print(f"  [GitHub] Invalid query: '{query}' – try a shorter, simpler query")
            return []
        if resp.status_code != 200:
            print(f"  [GitHub] API error: {resp.status_code}")
            return []

        items = resp.json().get("items", [])
        for item in items:
            if len(results) >= config.max_results:
                break

            repo = item.get("repository", {}).get("full_name", "")
            file_path = item.get("path", "")
            html_url = item.get("html_url", "")
            raw_url = html_url \
                .replace("https://github.com", "https://raw.githubusercontent.com") \
                .replace("/blob/", "/")

            code = _fetch_raw(raw_url, config)
            if not code:
                continue

            lines = code.splitlines()
            if len(lines) < 5 or len(lines) > 600:
                continue  # skip trivially short or huge files

            results.append({
                "source": "github",
                "repo": repo,
                "file": file_path,
                "url": html_url,
                "code": code[:config.max_chars_per_file],
            })
            time.sleep(0.1)

    except requests.RequestException as e:
        print(f"  [GitHub] Network error: {e}")

    return results


def _fetch_raw(url: str, config: ResearcherConfig) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=config.timeout)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        pass
    return None
