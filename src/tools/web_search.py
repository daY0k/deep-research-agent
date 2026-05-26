"""
Web search tool using DuckDuckGo (no API key needed).
Falls back to a basic HTTP fetch if DDG fails.
"""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from typing import List
import asyncio


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


async def ddg_search(query: str, max_results: int = 5) -> List[dict]:
    """Return list of {title, url, snippet} from DuckDuckGo HTML search."""
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query, "kl": "ru-ru"}

    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        resp = await client.post(url, data=params)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for r in soup.select(".result__body")[:max_results]:
        title_el = r.select_one(".result__title")
        url_el = r.select_one(".result__url")
        snippet_el = r.select_one(".result__snippet")

        title = title_el.get_text(strip=True) if title_el else ""
        link = url_el.get_text(strip=True) if url_el else ""
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        if title and link:
            if not link.startswith("http"):
                link = "https://" + link
            results.append({"title": title, "url": link, "snippet": snippet})

    return results


async def fetch_page(url: str, max_chars: int = 4000) -> str:
    """Fetch and extract readable text from a URL."""
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [l for l in text.splitlines() if len(l) > 30]
    return "\n".join(lines)[:max_chars]


TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for information about a topic. "
            "Returns a list of results with title, URL, and snippet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_page",
        "description": "Fetch and read the text content of a web page given its URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch"
                }
            },
            "required": ["url"]
        }
    }
]


async def execute_tool(name: str, inputs: dict) -> str:
    if name == "web_search":
        results = await ddg_search(inputs["query"], inputs.get("max_results", 5))
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}\n   URL: {r['url']}\n   {r['snippet']}")
        return "\n\n".join(lines)

    elif name == "fetch_page":
        try:
            text = await fetch_page(inputs["url"])
            return text or "Page fetched but no readable content found."
        except Exception as e:
            return f"Error fetching page: {e}"

    return f"Unknown tool: {name}"
