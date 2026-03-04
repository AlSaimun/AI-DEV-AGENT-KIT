from .base import make_pattern_tool

ConstantsPatternTool = make_pattern_tool(
    key="constants",
    name="get_constants_pattern",
    description=(
        "Returns the constants / enums pattern for ai-agents-backend. "
        "Covers models.TextChoices classes with _() labels, "
        "module-level scalar constants, and naming conventions."
    ),
)
