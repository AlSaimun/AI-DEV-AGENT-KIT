"""
Project documentation search tool.

Searches the ChromaDB vector store built from PDFs in django_mcp/docs/.
Returns the most relevant chunks from the project description / requirements.

Completely separate from the coding-pattern tools — those are direct lookups.
This tool is for searching WHAT the project does, not HOW code is structured.

To index a new document: drop a PDF into django_mcp/docs/ and restart the server.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# vector_store lives one level up (in django_mcp/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from vector_store import get_store  # noqa: E402

from .base import PatternTool, ToolDefinition

_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": (
                "Natural-language question about the project, e.g. "
                "'what does the billing module do', "
                "'how does subscription management work', "
                "'what are the user roles in this system'."
            ),
        },
        "n_results": {
            "type": "integer",
            "description": "Number of relevant chunks to return (default 4, max 8).",
            "default": 4,
            "minimum": 1,
            "maximum": 8,
        },
    },
    "required": ["query"],
}


class SemanticSearchTool(PatternTool):
    """
    Searches project description PDFs via ChromaDB.
    Separate from coding-pattern tools — those never touch the vector DB.
    """

    def __init__(self) -> None:
        pass

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_project_docs",
            description=(
                "Searches the project's PDF documentation (requirements, architecture, "
                "feature specs) using semantic similarity. Use this to understand WHAT "
                "the project does before deciding HOW to implement a feature. "
                "Returns the most relevant excerpts from PDFs placed in django_mcp/docs/."
            ),
            input_schema=_SCHEMA,
        )

    def execute(self, arguments: dict[str, Any]) -> str:
        query     = arguments.get("query", "").strip()
        n_results = min(int(arguments.get("n_results", 4)), 8)

        if not query:
            return "Please provide a non-empty query string."

        store = get_store()

        if store.doc_count() == 0:
            return (
                "No project documents indexed yet.\n\n"
                "**To index your project description:**\n"
                "1. Drop one or more PDF files into  `django_mcp/docs/`\n"
                "2. Restart the MCP server\n"
                "3. Run this search again"
            )

        results = store.search(query, n_results=n_results)

        if not results:
            return f'No relevant content found for: "{query}"'

        lines = [
            f'# Project Docs — Search: "{query}"',
            f'_{len(results)} chunk(s) from {len({r["filename"] for r in results})} file(s)_',
        ]

        for rank, r in enumerate(results, start=1):
            lines.append(
                f"\n---\n"
                f'**{rank}. {r["filename"]}** · page {r["page"]} '
                f'(similarity distance: {r["distance"]})\n\n'
                f'{r["content"]}'
            )

        return "\n".join(lines)
