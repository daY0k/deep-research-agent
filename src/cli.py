"""
CLI entry point for Deep Research Agent.

Usage:
    python -m src.cli "Your research question"
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli \"Your research question\"")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set. Add it to .env or environment.")
        sys.exit(1)

    from src.agents.orchestrator import ResearchPipeline

    print(f"\n🔬 Deep Research Agent")
    print(f"📌 Topic: {topic}\n")
    print("=" * 60)

    def on_step(step: str, msg: str):
        short = msg[:120].replace("\n", " ")
        print(f"[{step.upper():12s}] {short}")

    pipeline = ResearchPipeline(api_key=api_key, base_url=base_url)

    start = time.time()
    result = asyncio.run(pipeline.run(topic, on_step=on_step))
    elapsed = time.time() - start

    print("=" * 60)
    print(f"\n✅ Done in {elapsed:.1f}s\n")
    print(result["report"])

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(f"report_{ts}.md")
    out_path.write_text(result["report"], encoding="utf-8")
    print(f"\n💾 Saved to {out_path}")


if __name__ == "__main__":
    main()
