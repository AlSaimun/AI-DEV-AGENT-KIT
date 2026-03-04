from .base import make_pattern_tool

UrlPatternTool = make_pattern_tool(
    key="urls",
    name="get_url_pattern",
    description=(
        "Returns the URL configuration pattern for ai-agents-backend. "
        "Covers app-level urls.py with app_name + include(), "
        "version-level urls.py with path() entries using <uuid:id>, "
        "and config/urls.py registration."
    ),
)
