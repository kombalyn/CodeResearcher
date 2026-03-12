"""
Example: code-researcher integrated into the planner → controller pipeline.

This shows how code-researcher enriches each planning step with
real GitHub code examples before the controller sends tasks to the
programmer agent.

This is the pattern used in planner_agent.py from the parent project.

Requirements:
    pip install langchain langchain-openai langgraph python-dotenv requests

.env:
    OPENAI_API_KEY=sk-...
    GITHUB_TOKEN=ghp_...     # optional
    PROJECT_PATH=.
    OUTPUT_DIR=output
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../python"))

from dotenv import load_dotenv
load_dotenv()

from code_researcher import CodeResearcher
from code_researcher.config import Mode


def enrich_task_with_research(task: str, language: str = "python") -> str:
    """
    Search for relevant code examples and append them to the task description.
    Returns the enriched task string ready for the programmer agent.

    Args:
        task:     Original task description for the programmer agent
        language: Target programming language

    Returns:
        task + context block with GitHub code examples
    """
    researcher = CodeResearcher(
        # Auto-detects paid/free mode from GITHUB_TOKEN in .env
        use_grep_app=True,       # grep.app works without token
        use_stackoverflow=False,
    )

    result = researcher.search(task, language=language)

    if not result:
        print(f"  [Researcher] No examples found for: '{task[:50]}'")
        return task

    print(f"  [Researcher] Found {result.found} examples (mode: {result.mode})")
    return task + "\n\n" + result.context_block


def demo_planner_step():
    """
    Simulates one planner step: enrich task → send to programmer agent.
    """
    # Original task from the planner
    original_task = (
        "Write a Python script in the output/ directory that reads a stock name "
        "from stdin, searches Google for its next earnings report date, "
        "and prints the date in 'Mon. DD' format (e.g. 'Mar. 18')."
    )

    print("Original task:")
    print(f"  {original_task[:80]}...")
    print()

    # Enrich with GitHub examples
    print("Searching for code examples...")
    enriched_task = enrich_task_with_research(
        "google search stock earnings date python requests beautifulsoup scraping",
        language="python",
    )

    # The enriched task now contains real code context
    final_task = original_task + "\n\n" + enriched_task.split("\n\n", 1)[-1]

    print()
    print("Enriched task (first 500 chars of context block):")
    context_start = final_task.find("## Code Examples")
    if context_start != -1:
        print(final_task[context_start:context_start + 500] + "...")
    print()

    # In the real planner_agent.py, this enriched_task is passed to run_controller()
    # Here we just show what it would look like:
    print("This enriched task would be passed to the controller:")
    print("  run_controller(task=enriched_task, input_data=..., expected_output=...)")


def demo_standalone_research():
    """
    Shows how to use code-researcher standalone without any agent pipeline.
    """
    researcher = CodeResearcher()  # auto-detects mode from .env

    print(f"Mode: {'paid' if researcher.config.is_paid else 'free'}")
    print()

    queries = [
        ("google search earnings date python", "python"),
        ("fetch JSON REST API", "typescript"),
        ("async http client reqwest", "rust"),
    ]

    for query, lang in queries:
        print(f"Query: '{query}' (language: {lang})")
        result = researcher.search(query, language=lang)
        print(f"  → Found {result.found} examples")
        if result.found > 0:
            print(f"  → First result: [{result.results[0].source}] {result.results[0].repo}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="code-researcher pipeline integration demo")
    parser.add_argument(
        "--demo",
        choices=["planner", "standalone"],
        default="planner",
        help="Which demo to run",
    )
    args = parser.parse_args()

    if args.demo == "planner":
        demo_planner_step()
    else:
        demo_standalone_research()
