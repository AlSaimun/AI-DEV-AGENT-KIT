# MCP Servers

This directory contains **MCP (Model Context Protocol) servers** — each one gives AI assistants live awareness of a specific framework or stack.

An MCP server runs as a subprocess alongside your AI tool and exposes tools the AI can call by name during a conversation. Every tool result is injected into the AI's context — no copy-pasting, no stale information.

---

## Available Servers

| Server | Stack | README |
|--------|-------|--------|
| [`django_mcp/`](django_mcp/README.md) | Django + DRF | Full docs, tool list, and per-tool client config |
| `react_mcp/` | React | 🔜 Coming soon |

---

## What MCP Gives You

Without MCP, the AI guesses at your project structure based on open files.  
With MCP, the AI can call tools like:

- `list_django_models` → "Show me every model in this codebase right now"
- `get_app_structure` → "What files does the billing app have?"
- `list_pending_migrations` → "Are there unapplied migrations?"
- `detect_circular_imports` → "Are there any import cycles?"
- `generate_drf_api` → "Scaffold a full DRF API for this model"

These run against your actual project files every time, so the AI always has current, accurate data.

---

## MCP vs Hooks vs Skills

| | MCP | Hooks | Skills |
|--|-----|-------|--------|
| **What** | Live project data | Always-on coding rules | On-demand code templates |
| **When** | AI calls a tool | Every conversation | You invoke manually |
| **Example** | "Here are your 12 actual models" | "Always use BaseModel, never models.Model" | "Here's the scaffold for a service class" |

→ [Set up hooks](../hooks/README.md) — always-active coding rules for every AI tool  
→ [Set up skills](../skills/README.md) — manually-invoked code generation templates

---

## Quick Start

```bash
# Django MCP server
cd django_mcp
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Then configure your AI tool — see [`django_mcp/README.md`](django_mcp/README.md#client-configuration) for VS Code, Cursor, Claude Code, and Windsurf setup.
