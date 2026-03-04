from .base import make_pattern_tool

DirectoryStructureTool = make_pattern_tool(
    key="directory",
    name="get_directory_structure",
    description=(
        "Returns the standard app directory layout for ai-agents-backend: "
        "models/, repositories/, services/, api/v1/views/, api/v1/serializers/, "
        "migrations/, tests/, fixtures/, tasks/, and __init__.py export conventions."
    ),
)
