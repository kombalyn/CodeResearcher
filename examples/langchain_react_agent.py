"""
Example: code-researcher as a LangChain ReAct agent tool.

The agent automatically calls search_code_examples() before writing code,
giving it real GitHub examples as context.

Requirements:
    pip install langchain langchain-openai langgraph python-dotenv requests

.env:
    OPENAI_API_KEY=sk-...
    GITHUB_TOKEN=ghp_...     # optional, enables paid mode
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../python"))

from dotenv import load_dotenv
load_dotenv()

from code_researcher.langchain_tool import CodeResearcherTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


def main():
    # 1. Create the code researcher tool
    #    Free mode: no token needed, 60 GitHub req/h
    #    Paid mode: set GITHUB_TOKEN in .env for 5,000 req/h
    research_tool = CodeResearcherTool(
        language="python",
        use_grep_app=True,       # grep.app always works without token
        use_stackoverflow=False,
    )

    # 2. Add other tools your agent needs
    from langchain_core.tools import tool

    @tool
    def write_file(file_path: str, content: str) -> str:
        """Write content to a file."""
        import os
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written: {file_path}"

    # 3. Build the agent
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.1,
    )

    system_prompt = """You are a professional coding agent.

IMPORTANT: Before writing any code, ALWAYS use the search_code_examples tool
to find real GitHub examples. Use the found code as inspiration and reference,
but adapt it to the specific task — never copy blindly.

Workflow:
1. search_code_examples("relevant search terms in English")
2. Study the found examples
3. Write clean, working code based on what you learned
4. Save it using write_file
"""

    agent = create_react_agent(llm, [research_tool, write_file], prompt=system_prompt)

    # 4. Run the agent
    task = "Write a Python script that takes a stock name from stdin and prints its next earnings report date using web scraping"
    print(f"Task: {task}\n")
    print("=" * 65)

    for step in agent.stream({"messages": [("user", task)]}):
        if "agent" in step:
            msgs = step["agent"]["messages"]
            if msgs and hasattr(msgs[-1], "content") and msgs[-1].content:
                print(msgs[-1].content)


if __name__ == "__main__":
    main()
