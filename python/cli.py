#!/usr/bin/env python3
"""
code-researcher CLI

Usage:
    python cli.py "google search earnings date python"
    python cli.py "rust async http client reqwest" --language rust
    python cli.py "fetch API typescript" --language typescript --no-grep-app
    python cli.py "sqlite insert python" --paid   # requires GITHUB_TOKEN in .env
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from code_researcher import CodeResearcher
from code_researcher.config import Mode


def main():
    parser = argparse.ArgumentParser(
        description="code-researcher – search GitHub for real code examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "google search stock earnings python requests"
  python cli.py "async http client" --language rust
  python cli.py "fetch JSON API" --language typescript
  python cli.py "sqlite orm" --language python --paid

Free vs Paid:
  Free mode  : No token needed. GitHub limit: 60 req/hour.
               grep.app is always free and has no rate limit.
  Paid mode  : Set GITHUB_TOKEN in .env for 5,000 GitHub req/hour.
               Get token: https://github.com/settings/tokens (public_repo scope)
        """,
    )

    parser.add_argument("query", help="Search query (in English for best results)")
    parser.add_argument(
        "--language", "-l",
        default="python",
        help="Programming language (python, javascript, typescript, rust, go, ...) [default: python]",
    )
    parser.add_argument(
        "--paid", action="store_true",
        help="Force paid mode (requires GITHUB_TOKEN in .env)",
    )
    parser.add_argument(
        "--free", action="store_true",
        help="Force free mode (ignores GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help="Max number of results [default: 3 free / 10 paid]",
    )
    parser.add_argument(
        "--no-github", action="store_true",
        help="Skip GitHub source",
    )
    parser.add_argument(
        "--no-grep-app", action="store_true",
        help="Skip grep.app source",
    )
    parser.add_argument(
        "--stackoverflow", action="store_true",
        help="Also search StackOverflow",
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Output raw code only (no headers/formatting)",
    )

    args = parser.parse_args()

    mode = None
    if args.paid:
        mode = Mode.PAID
    elif args.free:
        mode = Mode.FREE

    researcher = CodeResearcher(
        mode=mode,
        max_results=args.max,
        use_github=not args.no_github,
        use_grep_app=not args.no_grep_app,
        use_stackoverflow=args.stackoverflow,
    )

    result = researcher.search(args.query, language=args.language)

    print()
    print("=" * 65)
    print(f"Results: {result.found} | Mode: {result.mode} | Language: {args.language}")
    print("=" * 65)

    if not result:
        print("\nNo results found.")
        print("Tips:")
        print("  - Use English search queries")
        print("  - Try shorter, more specific terms")
        print("  - Set GITHUB_TOKEN in .env for better results")
        return

    if args.raw:
        for r in result.results:
            print(f"\n# [{r.source}] {r.repo} – {r.file}")
            print(f"# {r.url}")
            print(r.code)
    else:
        print()
        print(result.context_block)
        print()
        print("Sources:")
        for i, r in enumerate(result.results, 1):
            print(f"  {i}. [{r.source}] {r.repo} – {r.url}")


if __name__ == "__main__":
    main()
