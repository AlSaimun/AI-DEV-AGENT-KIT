from .base import make_pattern_tool

SerializerPatternTool = make_pattern_tool(
    key="serializer",
    name="get_serializer_pattern",
    description=(
        "Returns the serializer pattern for ai-agents-backend. "
        "Covers BaseModelSerializer write serializer, read/detail serializer, "
        "SerializerMethodField for FK expansion, and __init__.py export conventions."
    ),
)
