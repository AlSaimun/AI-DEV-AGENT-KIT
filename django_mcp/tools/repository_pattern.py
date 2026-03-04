from .base import make_pattern_tool

RepositoryPatternTool = make_pattern_tool(
    key="repository",
    name="get_repository_pattern",
    description=(
        "Returns the repository pattern for ai-agents-backend. "
        "Covers BaseRepository subclass, __init__ with model injection, "
        "and guidelines for adding custom query methods on top of the "
        "built-in get / filter / create / update / delete / bulk_* methods."
    ),
)
