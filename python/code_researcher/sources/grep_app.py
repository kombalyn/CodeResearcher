"""
grep.app source – search GitHub code without any token.

grep.app is a free code search engine indexing GitHub.
No authentication required, works in both free and paid modes.

Website: https://grep.app
"""

import re
import time
import requests
import urllib.parse
from typing import Optional
from ..config import ResearcherConfig


def search_grep_app(
    query: str,
    language: str = "python",
    config: Optional[ResearcherConfig] = None,
) -> list[dict]:
    """
    Search grep.app for code matching the query.
    No API token required.

    Args:
        query:    Code search query
        language: Language filter (Python, JavaScript, TypeScript, Rust, ...)
        config:   ResearcherConfig instance

    Returns:
        List of dicts: {"repo", "file", "url", "code", "source": "grep.app"}
    """
    if config is None:
        config = ResearcherConfig()

    results = []
    lang_map = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "rust": "Rust",
        "go": "Go",
        "java": "Java",
    }
    lang_param = lang_map.get(language.lower(), language.title())

    search_url = (
        f"https://grep.app/search?"
        f"q={urllib.parse.quote(query)}"
        f"&filter[lang][0]={urllib.parse.quote(lang_param)}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; code-researcher/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        resp = requests.get(search_url, headers=headers, timeout=config.timeout)
        if resp.status_code != 200:
            print(f"  [grep.app] HTTP {resp.status_code}")
            return []

        # Extract GitHub file paths from HTML
        # Pattern: /user/repo/blob/hash/path/file.ext
        blob_paths = re.findall(
            r'href="(https://github\.com/[^"]+/blob/[^"]+\.[a-zA-Z]+)"',
            resp.text,
        )

        seen = set()
        unique = []
        for p in blob_paths:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        for html_url in unique[:config.max_results * 2]:
            if len(results) >= config.max_results:
                break

            raw_url = html_url \
                .replace("https://github.com", "https://raw.githubusercontent.com") \
                .replace("/blob/", "/")

            parts = html_url.replace("https://github.com/", "").split("/")
            repo = "/".join(parts[:2]) if len(parts) >= 2 else html_url
            # file path after /blob/hash/
            file_path = "/".join(parts[4:]) if len(parts) >= 5 else parts[-1]

            code = _fetch_raw(raw_url, config)
            if not code:
                continue

            lines = code.splitlines()
            if len(lines) < 5 or len(lines) > 600:
                continue

            results.append({
                "source": "grep.app",
                "repo": repo,
                "file": file_path,
                "url": html_url,
                "code": code[:config.max_chars_per_file],
            })
            time.sleep(0.15)

    except requests.RequestException as e:
        print(f"  [grep.app] Network error: {e}")

    return results


def _fetch_raw(url: str, config: ResearcherConfig) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=config.timeout)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        pass
    return None
