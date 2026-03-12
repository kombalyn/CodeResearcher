"""
StackOverflow source – extract code snippets from top answers.
No authentication required. Uses the public Stack Exchange API v2.3.

API docs: https://api.stackexchange.com/docs
"""

import re
import time
import requests
from typing import Optional
from ..config import ResearcherConfig


def search_stackoverflow(
    query: str,
    config: Optional[ResearcherConfig] = None,
) -> list[dict]:
    """
    Search StackOverflow for questions and extract code blocks from accepted answers.

    Args:
        query:  Search query (e.g. "python google search scraping requests")
        config: ResearcherConfig instance

    Returns:
        List of dicts: {"title", "url", "code", "source": "stackoverflow"}
    """
    if config is None:
        config = ResearcherConfig()

    results = []
    params = {
        "q": query,
        "tagged": "python",
        "site": "stackoverflow",
        "sort": "votes",
        "order": "desc",
        "pagesize": config.max_results * 2,
        "filter": "withbody",
    }

    try:
        resp = requests.get(
            "https://api.stackexchange.com/2.3/search/advanced",
            params=params,
            timeout=config.timeout,
        )
        if resp.status_code != 200:
            print(f"  [StackOverflow] HTTP {resp.status_code}")
            return []

        items = resp.json().get("items", [])
        for item in items[:config.max_results]:
            title = item.get("title", "")
            link = item.get("link", "")
            accepted_id = item.get("accepted_answer_id")

            code_blocks = _extract_code(item.get("body", ""))

            if accepted_id:
                try:
                    ans = requests.get(
                        f"https://api.stackexchange.com/2.3/answers/{accepted_id}",
                        params={"site": "stackoverflow", "filter": "withbody"},
                        timeout=config.timeout,
                    )
                    if ans.status_code == 200:
                        ans_items = ans.json().get("items", [])
                        if ans_items:
                            code_blocks += _extract_code(ans_items[0].get("body", ""))
                except Exception:
                    pass

            if code_blocks:
                combined = "\n\n# ---\n\n".join(code_blocks[:3])
                results.append({
                    "source": "stackoverflow",
                    "title": title,
                    "url": link,
                    "code": combined[:config.max_chars_per_file],
                })
            time.sleep(0.1)

    except requests.RequestException as e:
        print(f"  [StackOverflow] Network error: {e}")

    return results


def _extract_code(html: str) -> list[str]:
    """Extract code blocks from HTML body."""
    blocks = re.findall(r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", html, re.DOTALL)
    # Unescape HTML entities
    cleaned = []
    for b in blocks:
        b = b.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
        b = re.sub(r"<[^>]+>", "", b).strip()
        if b.count("\n") >= 2:
            cleaned.append(b)
    return cleaned
