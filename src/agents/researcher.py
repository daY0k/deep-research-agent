"""
Researcher Agent — searches the web and collects raw findings.
Runs N parallel sub-queries for a given research topic.
"""

from __future__ import annotations

import asyncio

import anthropic

from src.agents.base import BaseAgent
from src.tools.web_search import TOOL_DEFINITIONS


class ResearcherAgent(BaseAgent):
    name = "researcher"
    system_prompt = (
        "You are a senior research analyst. Your job is to search the web and collect "
        "accurate, relevant information on the assigned sub-topic. "
        "Use web_search to find sources, then fetch_page to read the most relevant ones. "
        "Return a structured findings report in Markdown: "
        "key facts, quotes, sources (URLs). Be thorough. Language: match the query language."
    )
    tools = TOOL_DEFINITIONS

    async def research(self, sub_query: str) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    f"Research this sub-topic thoroughly and return a findings report:\n\n"
                    f"{sub_query}"
                ),
            }
        ]
        return await self.run(messages)


async def run_parallel_researchers(
    client: anthropic.AsyncAnthropic,
    sub_queries: list[str],
) -> list[tuple[str, str]]:
    """Run multiple ResearcherAgents in parallel. Returns [(sub_query, findings)]."""
    agent = ResearcherAgent(client)
    tasks = [agent.research(q) for q in sub_queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = []
    for q, r in zip(sub_queries, results):
        if isinstance(r, Exception):
            output.append((q, f"[ERROR] {r}"))
        else:
            output.append((q, r))
    return output
