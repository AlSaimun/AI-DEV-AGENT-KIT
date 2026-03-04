"""
Scaffold generator tool.

Generates a complete, filled-in API scaffold (all layers) for any resource
by replacing placeholder tokens in every pattern template.
"""

from __future__ import annotations

import re
from typing import Any

from .base import PatternTool, ToolDefinition

# Layers rendered in output order
_SCAFFOLD_LAYERS = ("model", "constants", "repository", "service", "serializer", "view", "urls")

_SCHEMA = {
    "type": "object",
    "properties": {
        "model_name": {
            "type": "string",
            "description": "PascalCase model name, e.g. 'UserProfile'.",
        },
        "app_name": {
            "type": "string",
            "description": "Django app name, e.g. 'user' or 'ai_agent'.",
        },
    },
    "required": ["model_name", "app_name"],
}


class ScaffoldGeneratorTool(PatternTool):
    """
    Generates a fully-rendered multi-file scaffold for any resource name.
    All {ModelName} / <app_name> placeholders are substituted automatically.
    """

    def __init__(self, patterns: dict[str, str]) -> None:
        self._patterns = patterns

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="generate_api_scaffold",
            description=(
                "Generates a complete API scaffold (model, constants, repository, "
                "service, serializer, view, urls) for a given resource. "
                "Placeholders like {ModelName} and <app_name> are replaced automatically."
            ),
            input_schema=_SCHEMA,
        )

    def execute(self, arguments: dict[str, Any]) -> str:
        model_name: str = arguments.get("model_name", "MyModel")
        app_name: str   = arguments.get("app_name", "my_app")

        snake  = self._to_snake(model_name)
        plural = snake + "s"

        tokens = {
            "{ModelName}":         model_name,
            "{model_name}":        snake,
            "{model_name_plural}": plural,
            "{ResourceName}":      model_name,
            "<app_name>":          app_name,
            "<model_name>":        snake,
            "<model_name_plural>": plural,
        }

        sections = [
            f"# Generated API Scaffold — `{model_name}` in app `{app_name}`",
        ]
        for layer in _SCAFFOLD_LAYERS:
            rendered = self._render(self._patterns.get(layer, ""), tokens)
            sections.append(f"---\n{rendered}")

        return "\n\n".join(sections)

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_snake(pascal: str) -> str:
        s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", pascal)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()

    @staticmethod
    def _render(template: str, tokens: dict[str, str]) -> str:
        for old, new in tokens.items():
            template = template.replace(old, new)
        return template
