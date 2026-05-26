"""
Synthesizer Agent — produces the final comprehensive report.
"""

from __future__ import annotations

import anthropic

from src.agents.base import BaseAgent


class SynthesizerAgent(BaseAgent):
    name = "synthesizer"
    system_prompt = (
        "You are an expert analyst and technical writer. "
        "You receive research findings and a critic's evaluation. "
        "Your job is to synthesize them into one comprehensive, well-structured report. "
        "Structure:\n"
        "1. Executive Summary (3-5 sentences)\n"
        "2. Key Findings (bullet points with sources)\n"
        "3. Detailed Analysis (multiple sections as needed)\n"
        "4. Conclusions & Recommendations\n"
        "5. Sources\n\n"
        "Write clearly, avoid fluff. Use Markdown. Language: match the question language."
    )
    tools = []

    async def synthesize(
        self,
        topic: str,
        findings: list[tuple[str, str]],
        critique: str,
    ) -> str:
        findings_text = "\n\n".join(
            f"### Sub-topic: {q}\n{r}" for q, r in findings
        )
        messages = [
            {
                "role": "user",
                "content": (
                    f"Research question: {topic}\n\n"
                    f"=== RAW FINDINGS ===\n{findings_text}\n\n"
                    f"=== CRITIC EVALUATION ===\n{critique}\n\n"
                    f"Please write the final comprehensive research report."
                ),
            }
        ]
        return await self.run(messages)
