"""
Orchestrator — coordinates the full research pipeline.
1. Decomposes the question into sub-queries
2. Runs ResearcherAgents in parallel
3. Runs CriticAgent on findings
4. Runs SynthesizerAgent for final report
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator, Callable

import anthropic

from src.agents.base import BaseAgent
from src.agents.researcher import run_parallel_researchers
from src.agents.critic import CriticAgent
from src.agents.synthesizer import SynthesizerAgent
from src.memory.session import ResearchMemory


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    system_prompt = (
        "You are a research orchestrator. Given a research question, "
        "decompose it into 3-5 focused sub-queries that together cover the topic completely. "
        "Return ONLY a JSON array of strings, no explanation. Example:\n"
        '["sub-query 1", "sub-query 2", "sub-query 3"]'
    )
    tools = []

    async def decompose(self, topic: str) -> list[str]:
        messages = [
            {
                "role": "user",
                "content": f"Research question: {topic}\n\nDecompose into sub-queries.",
            }
        ]
        raw = await self.run(messages)
        try:
            start = raw.index("[")
            end = raw.rindex("]") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            return [topic]


class ResearchPipeline:
    """Full multi-agent research pipeline."""

    def __init__(self, api_key: str, base_url: str | None = None):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = anthropic.AsyncAnthropic(**kwargs)
        self.memory = ResearchMemory()

    async def run(
        self,
        topic: str,
        on_step: Callable[[str, str], None] | None = None,
    ) -> dict:
        """
        Execute full pipeline.

        Args:
            topic: The research question.
            on_step: Optional callback(step_name, message) for progress updates.

        Returns:
            dict with keys: topic, sub_queries, findings, critique, report
        """
        def step(name: str, msg: str):
            self.memory.add(name, msg)
            if on_step:
                on_step(name, msg)

        step("orchestrator", f"Starting research: {topic}")

        # Step 1: Decompose
        step("orchestrator", "Decomposing question into sub-queries...")
        orchestrator = OrchestratorAgent(self._client)
        sub_queries = await orchestrator.decompose(topic)
        step("orchestrator", f"Sub-queries: {sub_queries}")

        # Step 2: Parallel research
        step("researcher", f"Running {len(sub_queries)} researchers in parallel...")
        findings = await run_parallel_researchers(self._client, sub_queries)
        for q, r in findings:
            step("researcher", f"[{q}]\n{r[:500]}...")

        # Step 3: Critique
        step("critic", "Evaluating findings...")
        critic = CriticAgent(self._client)
        critique = await critic.critique(topic, findings)
        step("critic", critique[:500] + "...")

        # Step 4: Synthesize
        step("synthesizer", "Writing final report...")
        synthesizer = SynthesizerAgent(self._client)
        report = await synthesizer.synthesize(topic, findings, critique)
        step("synthesizer", "Report complete.")

        return {
            "topic": topic,
            "sub_queries": sub_queries,
            "findings": findings,
            "critique": critique,
            "report": report,
        }
