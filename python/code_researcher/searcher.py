"""
Core CodeResearcher class.

Orchestrates multiple sources (GitHub, grep.app, StackOverflow)
and formats results as context blocks for LLM prompts.
"""

from dataclasses import dataclass, field
from typing import Optional
from .config import ResearcherConfig, Mode


@dataclass
class SearchResult:
    """A single code file/snippet result."""
    source: str        # "github", "grep.app", "stackoverflow"
    repo: str          # e.g. "user/repo" or SO question title
    file: str          # file path or ""
    url: str           # link to original
    code: str          # raw code snippet


@dataclass
class ResearchResult:
    """Full research result for a task."""
    task: str
    results: list[SearchResult] = field(default_factory=list)
    context_block: str = ""     # ready-to-inject LLM context
    found: int = 0
    mode: str = "free"

    def __bool__(self):
        return self.found > 0


class CodeResearcher:
    """
    Search multiple sources for code examples relevant to a task.

    Usage (free mode – no token needed):
        researcher = CodeResearcher()
        result = researcher.search("google search stock earnings date python")
        print(result.context_block)

    Usage (paid mode – GitHub token):
        researcher = CodeResearcher(github_token="ghp_...")
        result = researcher.search("google search stock earnings date python")

    Usage (from .env file):
        # Set GITHUB_TOKEN=ghp_... in your .env
        researcher = CodeResearcher()   # auto-detects token from env
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        mode: Optional[Mode] = None,
        max_results: Optional[int] = None,
        use_github: bool = True,
        use_grep_app: bool = True,
        use_stackoverflow: bool = False,
        config: Optional[ResearcherConfig] = None,
    ):
        if config:
            self.config = config
        else:
            self.config = ResearcherConfig(
                github_token=github_token or "",
                mode=mode,
                max_results=max_results,
                use_github=use_github,
                use_grep_app=use_grep_app,
                use_stackoverflow=use_stackoverflow,
            )

    def search(
        self,
        task: str,
        language: str = "python",
    ) -> ResearchResult:
        """
        Search for code examples relevant to the task.

        Args:
            task:     Description of the programming task
            language: Target language ("python", "javascript", "typescript", "rust", ...)

        Returns:
            ResearchResult with .context_block ready for LLM injection
        """
        from .sources import search_github, search_grep_app, search_stackoverflow

        all_results: list[SearchResult] = []
        mode_label = "paid" if self.config.is_paid else "free"

        print(f"  [Researcher] Mode: {mode_label} | Query: '{task[:60]}{'...' if len(task) > 60 else ''}'")

        # Source 1: GitHub (paid = authenticated, free = unauthenticated)
        if self.config.use_github:
            print(f"  [Researcher] Searching GitHub ({'authenticated' if self.config.is_paid else 'unauthenticated, 60 req/h limit'})...")
            raw = search_github(task, language=language, config=self.config)
            all_results.extend([SearchResult(**r) for r in raw])
            print(f"    → {len(raw)} files found")

        # Source 2: grep.app (always free, no token needed)
        if self.config.use_grep_app and len(all_results) < self.config.max_results:
            print("  [Researcher] Searching grep.app (no token needed)...")
            raw = search_grep_app(task, language=language, config=self.config)
            all_results.extend([SearchResult(**r) for r in raw])
            print(f"    → {len(raw)} files found")

        # Source 3: StackOverflow (optional)
        if self.config.use_stackoverflow and len(all_results) < self.config.max_results:
            print("  [Researcher] Searching StackOverflow...")
            raw = search_stackoverflow(task, config=self.config)
            all_results.extend([SearchResult(**r) for r in raw])
            print(f"    → {len(raw)} snippets found")

        # Deduplicate by URL
        seen_urls = set()
        unique = []
        for r in all_results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                unique.append(r)

        final = unique[:self.config.max_results]
        print(f"  [Researcher] Total: {len(final)} unique results")

        ctx = self._build_context_block(final)
        return ResearchResult(
            task=task,
            results=final,
            context_block=ctx,
            found=len(final),
            mode=mode_label,
        )

    def _build_context_block(self, results: list[SearchResult]) -> str:
        """Format results as a context block for LLM injection."""
        if not results:
            return ""

        lines = [
            "## Code Examples from GitHub (use as reference, adapt don't copy blindly)\n",
        ]

        for i, r in enumerate(results, 1):
            source_label = r.source.upper()
            label = r.repo or r.file or "unknown"
            lines.append(f"### [{i}] [{source_label}] {label}")
            if r.file:
                lines.append(f"File: `{r.file}`")
            lines.append(f"URL: {r.url}")
            lines.append("```")
            lines.append(r.code.rstrip())
            lines.append("```\n")

        return "\n".join(lines)
