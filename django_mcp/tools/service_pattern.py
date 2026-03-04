from .base import make_pattern_tool

ServicePatternTool = make_pattern_tool(
    key="service",
    name="get_service_pattern",
    description=(
        "Returns the service layer pattern for ai-agents-backend. "
        "Covers BaseService subclass, constructor with repository injection, "
        "catching RepositoryError and re-raising as ServiceError, "
        "and Q-based filtering helpers."
    ),
)
