from .base import make_pattern_tool

ModelPatternTool = make_pattern_tool(
    key="model",
    name="get_model_pattern",
    description=(
        "Returns the Django model pattern for ai-agents-backend. "
        "Covers BaseModel inheritance, field conventions (CharField, ForeignKey, etc.), "
        "Meta class, verbose names wrapped in _(), and db_table naming."
    ),
)
