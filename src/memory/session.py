"""
Session memory — stores research steps and findings in-memory.
Optionally persists to a JSON file.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class ResearchMemory:
    def __init__(self, persist_path: str | None = None):
        self._entries: list[dict] = []
        self._persist_path = Path(persist_path) if persist_path else None

        if self._persist_path and self._persist_path.exists():
            self._load()

    def add(self, role: str, content: str, metadata: dict | None = None) -> None:
        entry = {
            "ts": time.time(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        self._entries.append(entry)
        if self._persist_path:
            self._save()

    def get_all(self) -> list[dict]:
        return list(self._entries)

    def get_by_role(self, role: str) -> list[dict]:
        return [e for e in self._entries if e["role"] == role]

    def summary(self, max_items: int = 20) -> str:
        items = self._entries[-max_items:]
        lines = []
        for e in items:
            lines.append(f"[{e['role'].upper()}] {e['content'][:300]}")
        return "\n---\n".join(lines)

    def clear(self) -> None:
        self._entries.clear()
        if self._persist_path and self._persist_path.exists():
            self._persist_path.unlink()

    def _save(self) -> None:
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._persist_path.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2))

    def _load(self) -> None:
        self._entries = json.loads(self._persist_path.read_text())
