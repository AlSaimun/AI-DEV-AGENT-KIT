"""
Full guide tool — returns every pattern concatenated into one document.
Useful when the user wants the complete reference in a single response.
"""

from __future__ import annotations

from typing import Any

from .base import PatternTool, ToolDefinition


class FullGuideTool(PatternTool):
    """Returns the complete concatenated coding guide."""

    def __init__(self, all_patterns: str) -> None:
        self._all_patterns = all_patterns

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_coding_structure",
            description=(
                "Returns the FULL coding structure guide for ai-agents-backend. "
                "Includes import order, directory layout, coding rules, and all "
                "layer templates (model, constants, repository, service, serializer, "
                "view, urls) plus a complete Company reference example."
            ),
            input_schema={"type": "object", "properties": {}, "required": []},
        )

    def execute(self, arguments: dict[str, Any]) -> str:
        return self._all_patterns
