from .base import make_pattern_tool

ViewPatternTool = make_pattern_tool(
    key="view",
    name="get_view_pattern",
    description=(
        "Returns the API view pattern for ai-agents-backend. "
        "Covers BaseApiView subclass, GET/POST/PUT/DELETE methods, "
        "pagination with CustomPagination, response shape {message, data, pagination}, "
        "and logger.error() on exceptions."
    ),
)
