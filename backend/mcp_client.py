"""Client for the ESPN MCP server hosted on Apify (mrbridge/espn-mcp-server).

The server speaks MCP over streamable HTTP. Tools are discovered at runtime with
`tools/list` and converted to OpenAI function-calling format, so the LLM can call
them exactly like the local tools.
"""
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)

DEFAULT_ESPN_MCP_URL = "https://mrbridge--espn-mcp-server.apify.actor/mcp"
TOOL_CACHE_SECONDS = 300
# Keep tool output small enough for free models with limited context windows
MAX_RESULT_CHARS = 12000


class ESPNMCPClient:
    """Thin wrapper that opens a short-lived MCP session per operation."""

    def __init__(self, token: Optional[str] = None, url: Optional[str] = None):
        self.token = token or os.getenv("APIFY_TOKEN")
        self.url = url or os.getenv("ESPN_MCP_URL") or DEFAULT_ESPN_MCP_URL

    @property
    def enabled(self) -> bool:
        return bool(self.token)

    @asynccontextmanager
    async def _session(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with streamablehttp_client(self.url, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Return the server's tools in OpenAI function-calling format."""
        async with self._session() as session:
            result = await session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or tool.name,
                    "parameters": tool.inputSchema or {"type": "object", "properties": {}},
                },
            }
            for tool in result.tools
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool and return a JSON-serialisable result dict."""
        async with self._session() as session:
            result = await session.call_tool(name, arguments)

        text = "\n".join(
            block.text for block in result.content if getattr(block, "text", None)
        )

        if result.isError:
            return {"success": False, "source": "espn-mcp", "error": text or "MCP tool error"}

        try:
            data: Any = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            data = text

        response: Dict[str, Any] = {"success": True, "source": "espn-mcp", "tool": name}

        # Used by the frontend scoreboard widget
        games = extract_games(data)
        if games:
            response["games"] = games

        if len(text) > MAX_RESULT_CHARS:
            response["data"] = text[:MAX_RESULT_CHARS] + "\n...[truncated]"
            response["truncated"] = True
        else:
            response["data"] = data
        return response


# ---- Normalisation of ESPN scoreboard data for the UI --------------------------------

def _as_score(value: Any) -> Any:
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _normalize_event(event: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(event, dict):
        return None

    # ESPN native shape: events[].competitions[].competitors[]
    competitions = event.get("competitions")
    if isinstance(competitions, list) and competitions:
        comp = competitions[0]
        competitors = comp.get("competitors") or []
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not (home and away):
            return None
        status = (comp.get("status") or event.get("status") or {}).get("type", {}) or {}
        detail = status.get("detail") or status.get("description") or ""
        if status.get("state") == "in":
            detail = f"Live - {detail}"
        return {
            "home": (home.get("team") or {}).get("displayName", "Home"),
            "away": (away.get("team") or {}).get("displayName", "Away"),
            "home_score": _as_score(home.get("score", 0)),
            "away_score": _as_score(away.get("score", 0)),
            "status": str(detail),
            "date": str(event.get("date", ""))[:10],
        }

    # Already-flat shape
    home = event.get("home") or event.get("home_team")
    away = event.get("away") or event.get("away_team")
    if isinstance(home, str) and isinstance(away, str):
        return {
            "home": home,
            "away": away,
            "home_score": _as_score(event.get("home_score", 0)),
            "away_score": _as_score(event.get("away_score", 0)),
            "status": str(event.get("status", "")),
            "date": str(event.get("date", ""))[:10],
        }
    return None


def extract_games(data: Any) -> List[Dict[str, Any]]:
    """Best-effort conversion of scoreboard output into flat game dicts."""
    events = None
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict):
        for key in ("events", "games", "scoreboard", "results"):
            value = data.get(key)
            if isinstance(value, list):
                events = value
                break
            if isinstance(value, dict) and isinstance(value.get("events"), list):
                events = value["events"]
                break
    games = [_normalize_event(e) for e in (events or [])]
    return [g for g in games if g]


# ---- Tool-list cache -----------------------------------------------------------------

_tool_cache: Dict[str, Any] = {"at": 0.0, "tools": []}


async def get_espn_tools(client: ESPNMCPClient) -> List[Dict[str, Any]]:
    """List MCP tools, cached briefly so we don't reconnect on every request."""
    if _tool_cache["tools"] and time.time() - _tool_cache["at"] < TOOL_CACHE_SECONDS:
        return _tool_cache["tools"]
    tools = await client.list_tools()
    _tool_cache.update(at=time.time(), tools=tools)
    return tools
