from .base import make_pattern_tool

ImportOrderTool = make_pattern_tool(
    key="import_order",
    name="get_import_order",
    description=(
        "Returns the 4-group import order convention for ai-agents-backend: "
        "1) Python stdlib  2) Django & third-party  "
        "3) dxh_libraries then dxh_common  4) Local app imports "
        "(models → repositories → services → serializers → constants)."
    ),
)
