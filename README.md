# AI DEV AGENT KIT

A collection of **MCP servers** and **AI coding skills** that give AI assistants (GitHub Copilot, Cursor, Claude Code, Windsurf, Kiro, Continue, Antigravity) deep awareness of your project's architecture, conventions, and coding rules.

Designed to be framework-agnostic and extensible — currently covers **Django**, with **React** and other frameworks planned.

---

## Repository Structure

```
ai-dev-agent-kit/
│
├── mcp/                          ← MCP servers (one per framework/stack)
│   ├── django_mcp/               ✅ Django + DRF
│   └── react_mcp/                🔜 React (coming soon)
│
├── skills/                       ← On-demand AI coding templates (invoke manually)
│   ├── django skills/             ✅ Django + DRF
│   └── react skills/              🔜 React (coming soon)
│
└── hooks/                        ← Always-on coding rules (auto-loaded by AI tools)
    ├── django hooks/              ✅ Django + DRF
    └── react hooks/               🔜 React (coming soon)
```

---

## What's Included

### `mcp/` — MCP Servers

MCP servers run as a subprocess alongside your AI tool and expose tools the AI can call during a conversation.

| Server | Stack | Tools |
|--------|-------|-------|
| [`mcp/django_mcp/`](mcp/django_mcp/README.md) | Django + DRF | `get_project_overview`, `list_django_models`, `get_app_structure`, `generate_drf_api`, `analyze_queryset`, `list_pending_migrations`, `detect_circular_imports`, `search_project_docs` |
| `mcp/react_mcp/` | React | 🔜 Coming soon |

### `skills/` — AI Coding Skills

Skills are structured Markdown files that tell the AI exactly how to generate or fix code following your project's conventions. They work as slash commands in Copilot and as rules/context in all other tools.

| Skills folder | Stack | Skills |
|--------------|-------|--------|
| [`skills/django skills/`](skills/README.md) | Django + DRF | `create-feature`, `create-model`, `create-repository`, `create-service`, `create-serializer`, `create-view`, `fix-coding-structure` |
| `skills/react skills/` | React | 🔜 Coming soon |

### `hooks/` — Always-On Coding Rules

Hooks are persistent instruction files that AI tools read **automatically** for every conversation in a project. No invocation needed — the AI always knows your architecture and coding rules.

| Hooks folder | Stack | Content |
|--------------|-------|---------|
| [`hooks/django hooks/`](hooks/README.md) | Django + DRF | 4-layer architecture, import order, model/repo/service/view rules, queryset rules |
| `hooks/react hooks/` | React | 🔜 Coming soon |

---

## Quick Start

### 1. MCP Server — pick your framework

```bash
# Django
cd mcp/django_mcp
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Then configure your AI tool — see [`mcp/django_mcp/README.md`](mcp/django_mcp/README.md) for per-tool setup (VS Code, Cursor, Claude Code, Windsurf, etc.).

### 2. Skills — copy to your project

```bash
SKILLS_SOURCE="$(pwd)/skills/django skills"
PROJECT="path/to/your/django/project"

# GitHub Copilot
for skill in "$SKILLS_SOURCE"/*/; do
  name=$(basename "$skill")
  mkdir -p "$PROJECT/.github/skills/$name"
  cp "$skill/SKILL.md" "$PROJECT/.github/skills/$name/SKILL.md"
done
```

See [`skills/README.md`](skills/README.md) for setup instructions for every tool (including Claude Code).

### 3. Hooks — deploy to your project

```bash
HOOK_SOURCE="$(pwd)/hooks/django hooks/HOOK.md"
cd path/to/your/django/project

cp "$HOOK_SOURCE" CLAUDE.md                                   # Claude Code
cp "$HOOK_SOURCE" .github/copilot-instructions.md             # GitHub Copilot
cp "$HOOK_SOURCE" .cursorrules                                # Cursor
cp "$HOOK_SOURCE" .windsurfrules                              # Windsurf
mkdir -p .kiro/steering && cp "$HOOK_SOURCE" .kiro/steering/django-coding-rules.md
```

See [`hooks/README.md`](hooks/README.md) for full setup instructions.

---

## How They Work Together

```
Your Django project
       │
       ├── CLAUDE.md / .cursorrules / .windsurfrules  ← Hooks: always-on rules (architecture, conventions)
       │
       ├── .github/skills/          ← Skills: teach the AI HOW to write code
       │   ├── create-model/
       │   └── ...
       │
       ├── docs/
       │   └── ai_project_overview.md  ← MCP: tells the AI WHAT the project does
       │
       └── .vscode/mcp.json            ← MCP server connection config
```

| | What it answers | When it runs |
|--|----------------|-------------|
| **Hooks** | "What rules should I always follow?" | Every conversation, automatically |
| **Skills** | "What's the exact template for a service?" | When you invoke `/create-service` |
| **MCP** | "What models actually exist right now?" | When the AI calls a tool |

---

## Roadmap

- [x] Django + DRF MCP server
- [x] Django coding skills (7 skills)
- [x] Django coding hooks (always-on rules for Copilot, Claude, Cursor, Windsurf, Kiro, Continue, Antigravity)
- [ ] React MCP server
- [ ] React coding skills
- [ ] React coding hooks
- [ ] Next.js skills
- [ ] Shared/agnostic skills (git conventions, PR descriptions, code review)

---

## Contributing

Each framework lives in its own isolated folder under `mcp/`, `skills/`, and `hooks/`.  
To add a new framework:

1. Create `mcp/<framework>_mcp/` with its own `server.py`, `tools/`, and `README.md`
2. Create `skills/<framework> skills/` with a `SKILL.md` per skill and a `README.md`
3. Create `hooks/<framework> hooks/` with a `HOOK.md` containing always-active coding rules
4. Update this root README

---

## License

MIT
