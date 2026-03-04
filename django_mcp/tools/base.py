"""
Base abstraction for all MCP pattern tools.

Every tool is a self-contained unit that:
  1. Declares its own name / description / JSON schema  (ToolDefinition)
  2. Knows how to execute itself                        (execute)
  3. Can convert itself to MCP wire types               (to_mcp_tool / to_mcp_content)

Adding a new tool = creating one new file + one line in tools/__init__.py.
No changes to server.py ever needed.  (Open/Closed Principle)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import mcp.types as types


# ── Value object ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict


# ── Abstract base ─────────────────────────────────────────────────────────────

class PatternTool(ABC):
    """
    Single-Responsibility: one tool = one concern.
    Liskov: every subclass is a drop-in replacement wherever PatternTool is expected.
    """

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition: ...

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> str: ...

    # ── MCP wire helpers (shared implementation) ──────────────────────────

    def to_mcp_tool(self) -> types.Tool:
        return types.Tool(
            name=self.definition.name,
            description=self.definition.description,
            inputSchema=self.definition.input_schema,
        )

    def to_mcp_content(self, arguments: dict[str, Any]) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=self.execute(arguments))]


# ── Factory for zero-argument pattern tools ─────────────────────────────────

def make_pattern_tool(*, key: str, name: str, description: str) -> type[PatternTool]:
    """
    Returns a PatternTool *class* (not instance) for a single pattern key.

    Usage in each tool file:
        MyTool = make_pattern_tool(key="model", name="get_model_pattern", description="...")

    The class is instantiated by the registry with the shared patterns dict injected
    via __init__, keeping tool files completely free of import-path concerns.
    (Dependency Inversion Principle)
    """

    class _PatternTool(PatternTool):
        _key = key

        def __init__(self, patterns: dict[str, str]) -> None:
            self._text = patterns.get(key, f"Pattern '{key}' not found.")

        @property
        def definition(self) -> ToolDefinition:
            return ToolDefinition(
                name=name,
                description=description,
                input_schema={"type": "object", "properties": {}, "required": []},
            )

        def execute(self, arguments: dict[str, Any]) -> str:
            return self._text

    _PatternTool.__name__ = name
    _PatternTool.__qualname__ = name
    return _PatternTool
