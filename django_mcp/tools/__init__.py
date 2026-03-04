"""
Tool registry — single place to register every tool.

To add a new tool:
  1. Create django_mcp/tools/my_tool.py  (subclass PatternTool or use make_pattern_tool)
  2. Import it here and append an instance to ALL_TOOLS.
  Nothing else changes.  (Open/Closed Principle)
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# ── Load coding_patterns data (avoids django_mcp/ being a package that shadows SDK) ─

_patterns_file = Path(__file__).parent.parent / "coding_patterns.py"
_spec = importlib.util.spec_from_file_location("coding_patterns", _patterns_file)
_mod  = importlib.util.module_from_spec(_spec)   # type: ignore[arg-type]
_spec.loader.exec_module(_mod)                    # type: ignore[union-attr]

_PATTERNS:     dict[str, str] = _mod.PATTERNS
_ALL_PATTERNS: str             = _mod.ALL_PATTERNS

# ── Import every tool class ───────────────────────────────────────────────────

from .model_pattern       import ModelPatternTool
from .view_pattern        import ViewPatternTool
from .service_pattern     import ServicePatternTool
from .repository_pattern  import RepositoryPatternTool
from .serializer_pattern  import SerializerPatternTool
from .url_pattern         import UrlPatternTool
from .constants_pattern   import ConstantsPatternTool
from .import_order        import ImportOrderTool
from .coding_rules        import CodingRulesTool
from .directory_structure import DirectoryStructureTool
from .scaffold_generator  import ScaffoldGeneratorTool
from .full_guide          import FullGuideTool
from .semantic_search     import SemanticSearchTool

# ── Build registry ────────────────────────────────────────────────────────────

ALL_TOOLS = [
    # ── individual pattern tools (each injected with the shared patterns dict)
    ModelPatternTool(_PATTERNS),
    ViewPatternTool(_PATTERNS),
    ServicePatternTool(_PATTERNS),
    RepositoryPatternTool(_PATTERNS),
    SerializerPatternTool(_PATTERNS),
    UrlPatternTool(_PATTERNS),
    ConstantsPatternTool(_PATTERNS),
    ImportOrderTool(_PATTERNS),
    CodingRulesTool(_PATTERNS),
    DirectoryStructureTool(_PATTERNS),
    # ── complex tools
    ScaffoldGeneratorTool(_PATTERNS),
    FullGuideTool(_ALL_PATTERNS),
    # ── semantic search (uses ChromaDB vector store)
    SemanticSearchTool(),
]

# name → tool lookup used by call_tool handler
TOOL_REGISTRY: dict[str, object] = {t.definition.name: t for t in ALL_TOOLS}
