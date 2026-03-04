"""
MCP Resources registration.

Resources let clients browse patterns by URI without calling a tool.
Kept separate from server.py so the server stays a thin wiring layer.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import mcp.types as types

# ── Load patterns ─────────────────────────────────────────────────────────────

_patterns_file = Path(__file__).parent / "coding_patterns.py"
_spec = importlib.util.spec_from_file_location("coding_patterns", _patterns_file)
_mod  = importlib.util.module_from_spec(_spec)   # type: ignore[arg-type]
_spec.loader.exec_module(_mod)                    # type: ignore[union-attr]

_PATTERNS:     dict[str, str] = _mod.PATTERNS
_ALL_PATTERNS: str             = _mod.ALL_PATTERNS


# ── Resource definitions ──────────────────────────────────────────────────────

def get_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="coding://structure/full",
            name="Full Coding Structure Guide",
            description=(
                "Complete coding guide: import order, directory layout, "
                "coding rules, and all layer templates."
            ),
            mimeType="text/markdown",
        ),
        *[
            types.Resource(
                uri=f"coding://structure/{key}",
                name=key.replace("_", " ").title(),
                description=f"Pattern template: {key}",
                mimeType="text/markdown",
            )
            for key in _PATTERNS
        ],
    ]


def read_resource(uri: str) -> str:
    if uri == "coding://structure/full":
        return _ALL_PATTERNS

    key = uri.removeprefix("coding://structure/")
    if key in _PATTERNS:
        return _PATTERNS[key]

    raise ValueError(f"Unknown resource URI: {uri}")
