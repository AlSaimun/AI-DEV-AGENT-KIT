# AI Agents — Coding Structure MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that gives any AI coding assistant instant, structured access to:

- **Coding pattern tools** — architecture templates (models, services, repositories, views, serializers, URLs, constants) so the AI generates code that matches your project's exact conventions.
- **Project documentation search** — semantic vector search over your own PDF specs, requirements, and architecture docs so the AI understands *what* the project does before deciding *how* to implement a feature.

Works with **GitHub Copilot Chat** (VS Code), **Cursor**, **Claude Code**, **Antigravity**, **Windsurf**, and any other MCP-compatible client.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Client Configuration](#client-configuration)
   - [VS Code — GitHub Copilot Chat](#vs-code--github-copilot-chat)
   - [Cursor](#cursor)
   - [Claude Code (CLI)](#claude-code-cli)
   - [Antigravity](#antigravity)
   - [Windsurf](#windsurf)
5. [Adding Project Documentation](#adding-project-documentation)
6. [Available Tools](#available-tools)
7. [Example Prompts](#example-prompts)
8. [Project Structure](#project-structure)
9. [Updating Patterns](#updating-patterns)

---

## How It Works

```
  Server startup
  ──────────────
  django_mcp/docs/*.pdf  ──chunk+embed──▶  ChromaDB (django_mcp/chroma_db/)
                                          │
                                          │  (ready before first tool call)
                                          ▼
Your AI Chat  ──MCP stdio──▶  django_mcp/server.py
                                │
                 ┌──────────────┼────────────────────┐
                 ▼              ▼                     ▼
           Pattern tools   Scaffold tool       search_project_docs
           (direct lookup) (token subst.)      (queries ChromaDB)
```

- **On startup**, every PDF in `django_mcp/docs/` is chunked, embedded with `all-MiniLM-L6-v2` (local — no API key), and stored in ChromaDB. The vector DB is fully ready before the server accepts any tool calls.
- **Pattern tools** return architecture templates instantly from in-memory strings — no DB, no latency.
- **`generate_api_scaffold`** performs token substitution (`{ModelName}`, `{model_name}`, `{app_name}`) across all six layers and returns a complete, ready-to-paste scaffold.
- **`search_project_docs`** queries the pre-built ChromaDB collection and returns the most semantically relevant excerpts with filename and page number.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.11 |
| Active virtual environment | project `venv/` |
| AI client with MCP support | see [Client Configuration](#client-configuration) |

```bash
# Verify Python
python --version
```

---

## Installation

### Option A — Global (recommended)

Install the MCP server once in your home directory and reuse it across every project:

```bash
# Clone / copy this django_mcp/ folder to your home directory
cp -r django_mcp/ ~/django_mcp

# Create a dedicated venv for it
python3 -m venv ~/django_mcp/venv
source ~/django_mcp/venv/bin/activate
pip install -r ~/django_mcp/requirements.txt
```

Then in every project's `.vscode/mcp.json`, point to `~/django_mcp/`:

```jsonc
{
  "servers": {
    "ai-agents-coding-structure": {
      "type": "stdio",
      "command": "/Users/yourname/django_mcp/venv/bin/python",
      "args": ["/Users/yourname/django_mcp/server.py"],
      "env": { "PROJECT_ROOT": "${workspaceFolder}" }
    }
  }
}
```

### Option B — Per-project

Keep `django_mcp/` inside the project repo and install into the project venv:

```bash
source venv/bin/activate
pip install -r django_mcp/requirements.txt
```

Verify the server loads:

```bash
PROJECT_ROOT=$PWD venv/bin/python django_mcp/server.py &
# Expected stderr:
# [MCP] Project root : /your/project
# [MCP] Indexed N chunk(s) from: architecture.md, ...
```

---

## Client Configuration

The server communicates over **stdio** — the client spawns it as a subprocess.

> **Key point:** set `PROJECT_ROOT` to the absolute path of each project. The server uses it to locate `<project>/django_mcp/docs/` and store the vector DB at `<project>/django_mcp/chroma_db/`. Every project gets a completely isolated vector DB — no cross-project context leakage.

### VS Code — GitHub Copilot Chat

Create or edit **`.vscode/mcp.json`** at the workspace root:

```jsonc
{
  "servers": {
    "ai-agents-coding-structure": {
      "type": "stdio",
      "command": "${workspaceFolder}/venv/bin/python",
      "args": ["${workspaceFolder}/django_mcp/server.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

> **Windows:** replace `venv/bin/python` with `venv\\Scripts\\python.exe`.

Then in Copilot Chat:

1. Open the chat panel (`Ctrl+Alt+I` / `Cmd+Alt+I`) and switch to **Agent** mode.
2. Click the **Tools** icon (plug) at the bottom of the panel.
3. Locate **ai-agents-coding-structure** and toggle it **on**.
4. The server starts automatically — no manual process needed.

---

### Cursor

Open **Cursor Settings → MCP** (or edit `~/.cursor/mcp.json`):

```jsonc
{
  "mcpServers": {
    "ai-agents-coding-structure": {
      "command": "/absolute/path/to/project/venv/bin/python",
      "args": ["/absolute/path/to/project/django_mcp/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```

After saving, restart Cursor and enable the server from **Settings → MCP → Available Servers**.

---

### Continue

Create a server config file under `.continue/mcpServers/` in your project (create the directory if missing). Example file: `.continue/mcpServers/ai-agents-coding-structure.yaml`:

```yaml
# .continue/mcpServers/ai-agents-coding-structure.yaml
name: ai-agents-coding-structure
version: 0.0.1
schema: v1
mcpServers:
  - name: ai-agents-coding-structure
    command: /absolute/path/to/project/venv/bin/python
    args:
      - /absolute/path/to/project/django_mcp/server.py
    env:
      PROJECT_ROOT: /absolute/path/to/project
```

Restart Continue (or reload its MCP servers) and enable the server from Continue's settings. Make sure `PROJECT_ROOT` is set to your workspace so the MCP server indexes `<PROJECT_ROOT>/docs/` into `<PROJECT_ROOT>/.mcp_chroma/`.

---

### Claude Code (CLI)

```bash
PROJECT_ROOT=/absolute/path/to/project \
claude mcp add ai-agents-coding-structure \
  --env PROJECT_ROOT=/absolute/path/to/project \
  /absolute/path/to/project/venv/bin/python \
  -- /absolute/path/to/project/django_mcp/server.py
```

Project-scoped (checked into `.mcp.json`):

```bash
claude mcp add ai-agents-coding-structure \
  --scope project \
  --env PROJECT_ROOT=/absolute/path/to/project \
  /absolute/path/to/project/venv/bin/python \
  -- /absolute/path/to/project/django_mcp/server.py
```

---

### Antigravity

Edit **`~/.gemini/antigravity/mcp_config.json`** (global config, shared across all projects):

```jsonc
{
  "mcpServers": {
    "ai-agents-coding-structure": {
      "command": "/absolute/path/to/project/venv/bin/python",
      "args": ["/absolute/path/to/project/django_mcp/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```

> **Note:** Antigravity reads its MCP config from `~/.gemini/antigravity/mcp_config.json` — not from a workspace-local file. Always use absolute paths; `${workspaceFolder}` is not supported. Use the project venv Python (`venv/bin/python`), not the system `python3`.

Restart Antigravity after saving. The server will start automatically when you open the project.

---

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```jsonc
{
  "mcpServers": {
    "ai-agents-coding-structure": {
      "command": "/absolute/path/to/project/venv/bin/python",
      "args": ["/absolute/path/to/project/django_mcp/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/project"
      }
    }
  }
}
```

Restart Windsurf, then open **Cascade** and confirm the tool list shows the server's tools.

---

## Adding Project Documentation

`search_project_docs` indexes **`<PROJECT_ROOT>/docs/`** automatically — this is your project's existing `docs/` folder. Both `.pdf` and `.md` files are supported.

Just drop files into `docs/` and restart the MCP server:

```
docs/
├── architecture.md          ← already indexed
├── developer_guidelines.md  ← already indexed
├── RAG_IMPLEMENTATION.md    ← already indexed
├── requirements.pdf         ← add your own
└── api/
    └── api_overview.md        ← subdirectories are scanned too
```

On restart the server logs:
```
[MCP] Project root : /your/project
[MCP] Indexed 149 chunk(s) from: architecture.md, developer_guidelines.md, ...
```

> The vector DB lives at `<PROJECT_ROOT>/.mcp_chroma/` and is git-ignored. The `docs/` folder itself is not git-ignored.

---

## Available Tools

### Coding Pattern Tools

| Tool | Description |
|---|---|
| `get_coding_structure` | Full coding guide — all patterns concatenated in one Markdown response |
| `get_import_order` | The exact 4-group import sequence |
| `get_model_pattern` | `BaseModel` subclass template |
| `get_constants_pattern` | `TextChoices` + scalar constant pattern |
| `get_repository_pattern` | `BaseRepository` subclass template |
| `get_service_pattern` | `BaseService` subclass template |
| `get_serializer_pattern` | `BaseModelSerializer` read/write pair |
| `get_view_pattern` | `BaseApiView` CRUD template |
| `get_url_pattern` | App-level and version-level URL config |
| `get_directory_structure` | Full app directory layout |
| `get_coding_rules` | Response shape, error handling, logging conventions |

### Scaffold Generator

| Tool | Inputs | Description |
|---|---|---|
| `generate_api_scaffold` | `model_name` (PascalCase), `app_name` | Generates a complete, token-substituted scaffold across all six layers |

### Project Documentation Search

| Tool | Inputs | Description |
|---|---|---|
| `search_project_docs` | `query` (string), `n_results` (int, default 4, max 8) | Semantic search over indexed PDFs — returns ranked excerpts with filename and page number |

---

## Example Prompts

**Code generation using patterns:**

```
Create a Product API following our coding structure.
```
```
Generate a full scaffold for model_name=OrderItem app_name=billing.
```
```
Show me the repository pattern so I can implement ProductRepository.
```
```
What is the correct import order for a new service file?
```

**Project understanding using PDF search:**

```
What does the billing module do?
```
```
How does the RAG pipeline work in this project?
```
```
What are the subscription plan limits?
```
```
How is multi-tenancy implemented?
```
```
What third-party integrations are supported?
```

---

## Project Structure

```
~/django_mcp/  (or anywhere — one copy shared across all projects)
├── server.py                  # MCP entry point — reads PROJECT_ROOT env var
├── coding_patterns.py         # All pattern templates as Python string constants
├── vector_store.py            # ChromaDB indexing & semantic search (PDF + Markdown)
├── resources.py               # MCP resource definitions
├── requirements.txt           # mcp, chromadb, pypdf, fpdf2
│
└── tools/
    ├── __init__.py            # Central registry — ALL_TOOLS, TOOL_REGISTRY
    ├── base.py                # PatternTool ABC + factory
    ├── model_pattern.py
    ├── view_pattern.py
    ├── service_pattern.py
    ├── repository_pattern.py
    ├── serializer_pattern.py
    ├── url_pattern.py
    ├── constants_pattern.py
    ├── import_order.py
    ├── coding_rules.py
    ├── directory_structure.py
    ├── scaffold_generator.py
    ├── full_guide.py
    └── semantic_search.py     # search_project_docs tool

Per-project paths  (set by PROJECT_ROOT=${workspaceFolder}):
  <PROJECT_ROOT>/docs/         ← your project's existing docs folder (PDF + .md)
  <PROJECT_ROOT>/.mcp_chroma/  ← vector DB, auto-created, git-ignored
```

---

## Updating Patterns

All code templates live in `django_mcp/coding_patterns.py` as plain Python string constants. Edit any pattern and restart the MCP server — no other changes needed.

---

## License

MIT

