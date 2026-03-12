"""
code-researcher: Search GitHub for real code examples and inject them into LLM prompts.
"""

from .searcher import CodeResearcher, SearchResult, ResearchResult
from .config import ResearcherConfig, Mode

__all__ = ["CodeResearcher", "SearchResult", "ResearchResult", "ResearcherConfig", "Mode"]
__version__ = "1.0.0"
