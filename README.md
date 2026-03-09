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
└── skills/                       ← AI coding skills (one folder per framework)
    ├── django skills/             ✅ Django + DRF
    └── react skills/              🔜 React (coming soon)
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

See [`skills/README.md`](skills/README.md) for setup instructions for every tool.

---

## How They Work Together

```
Your Django project
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

- **Skills** define *how* code should be written (patterns, templates, rules)
- **MCP server** provides *live project awareness* (actual models, apps, migrations, circular imports)
- **`ai_project_overview.md`** gives the AI the domain context (what the project does, its apps, decisions)

Used together, the AI generates code that matches your exact architecture on the first attempt.

---

## Roadmap

- [x] Django + DRF MCP server
- [x] Django coding skills (7 skills)
- [ ] React MCP server
- [ ] React coding skills
- [ ] Next.js skills
- [ ] Shared/agnostic skills (git conventions, PR descriptions, code review)

---

## Contributing

Each framework lives in its own isolated folder under `mcp/` and `skills/`.  
To add a new framework:

1. Create `mcp/<framework>_mcp/` with its own `server.py`, `tools/`, and `README.md`
2. Create `skills/<framework> skills/` with a `SKILL.md` per skill and a `README.md`
3. Update this root README

---

## License

MIT
