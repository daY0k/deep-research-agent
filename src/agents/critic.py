"""
Critic Agent — evaluates research findings for quality, gaps, and contradictions.
"""

from __future__ import annotations

import anthropic

from src.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    name = "critic"
    system_prompt = (
        "You are a rigorous research critic and fact-checker. "
        "You receive a collection of research findings from multiple researchers. "
        "Your job: identify gaps, contradictions, unverified claims, and low-quality sources. "
        "Also suggest what additional information is needed. "
        "Output a structured critique in Markdown with sections: "
        "✅ Strengths | ⚠️ Gaps & Issues | 🔍 Recommended Follow-ups. "
        "Be direct and specific. Language: match the input language."
    )
    tools = []

    async def critique(self, topic: str, findings: list[tuple[str, str]]) -> str:
        findings_text = "\n\n".join(
            f"### Sub-topic: {q}\n{r}" for q, r in findings
        )
        messages = [
            {
                "role": "user",
                "content": (
                    f"Original research question: {topic}\n\n"
                    f"Research findings from multiple agents:\n\n{findings_text}\n\n"
                    f"Please critique these findings."
                ),
            }
        ]
        return await self.run(messages)
