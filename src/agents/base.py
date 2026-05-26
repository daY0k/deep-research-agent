"""
Base agent class — wraps Claude API with tool use loop.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator

import anthropic

from src.tools.web_search import TOOL_DEFINITIONS, execute_tool


MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


class BaseAgent:
    """Single agent backed by Claude with optional tool use."""

    name: str = "agent"
    system_prompt: str = "You are a helpful assistant."
    tools: list[dict] = []

    def __init__(self, client: anthropic.AsyncAnthropic):
        self._client = client

    async def run(
        self,
        messages: list[dict],
        extra_system: str = "",
        stream: bool = False,
    ) -> str:
        system = self.system_prompt
        if extra_system:
            system += "\n\n" + extra_system

        current_messages = list(messages)

        while True:
            response = await self._client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                tools=self.tools,
                messages=current_messages,
            )

            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                current_messages = current_messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results},
                ]
            else:
                return self._extract_text(response)

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str:
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts)
