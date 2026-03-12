"""
LangChain Tool wrapper for code-researcher.

Provides a drop-in Tool for LangChain ReAct agents and other pipelines.

Requirements:
    pip install langchain langchain-core

Usage:
    from code_researcher.langchain_tool import CodeResearcherTool

    tool = CodeResearcherTool()            # free mode
    tool = CodeResearcherTool(github_token="ghp_...")  # paid mode

    # Use directly
    result = tool.run("google search earnings date python scraping")

    # Or plug into a LangChain agent
    from langchain.agents import create_react_agent
    agent = create_react_agent(llm, tools=[tool], prompt=prompt)
"""

from typing import Optional, Type
from .searcher import CodeResearcher
from .config import ResearcherConfig


def _make_langchain_tool(
    github_token: Optional[str] = None,
    language: str = "python",
    use_grep_app: bool = True,
    use_stackoverflow: bool = False,
    config: Optional[ResearcherConfig] = None,
):
    """
    Returns a LangChain StructuredTool for code research.
    Import is deferred so the package works without langchain installed.
    """
    try:
        from langchain_core.tools import tool as lc_tool
    except ImportError:
        raise ImportError(
            "langchain-core is required for LangChain integration. "
            "Install it with: pip install langchain-core"
        )

    researcher = CodeResearcher(
        github_token=github_token,
        use_grep_app=use_grep_app,
        use_stackoverflow=use_stackoverflow,
        config=config,
    )

    @lc_tool
    def search_code_examples(query: str) -> str:
        """
        Search GitHub and other sources for real code examples relevant to a programming task.
        Use this tool BEFORE writing code to find existing implementations you can learn from.

        Input: A natural language description of the coding task or a code search query.
               Write it in English for best results.
               Example: "google search stock earnings date scraping python requests beautifulsoup"

        Output: Formatted code snippets from real GitHub repositories, ready to use as context.
        """
        result = researcher.search(query, language=language)
        if not result:
            return "No relevant code examples found. Proceed without context."
        return result.context_block

    return search_code_examples


# Convenience alias
CodeResearcherTool = _make_langchain_tool
