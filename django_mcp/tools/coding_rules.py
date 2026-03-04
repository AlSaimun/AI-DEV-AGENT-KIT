from .base import make_pattern_tool

CodingRulesTool = make_pattern_tool(
    key="coding_rules",
    name="get_coding_rules",
    description=(
        "Returns the coding rules summary for ai-agents-backend: "
        "response shape (message/data/pagination), error handling chain "
        "(DatabaseError → RepositoryError → ServiceError), "
        "Logger usage, soft-delete convention, and pagination rules."
    ),
)
