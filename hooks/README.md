# Django Coding Hooks

There are **two kinds of hooks** in AI coding tools. This folder covers both:

| Type | What it is | Analogy |
|------|------------|---------|
| **Instruction files** | Markdown files the AI reads as permanent context | `.cursorrules`, `CLAUDE.md`, `.windsurfrules` |
| **Lifecycle hooks** | Scripts/commands that run automatically at events | `SessionStart`, `PostToolUse`, `PreToolUse` |

Use both together for the best experience:
- **Instruction files** → "always apply these architecture rules"
- **Lifecycle hooks** → "always auto-format Python files after editing"

---

## Files in This Folder

| File | What it is |
|------|-----------|
| [`HOOK.md`](django%20hooks/HOOK.md) | The Django coding rules — deploy this as an instruction file to any AI tool |
| [`claude-settings.json`](django%20hooks/claude-settings.json) | Lifecycle hooks for Claude Code — merge into `.claude/settings.json` |
| [`copilot-hooks.json`](django%20hooks/copilot-hooks.json) | Lifecycle hooks for VS Code Copilot — copy to `.github/hooks/` |

---

## Part 1 — Instruction Files

Instruction files are Markdown files the AI reads automatically at the start of every conversation. No invocation needed. The AI always knows your architecture and coding rules.

### Claude Code

Claude Code reads `CLAUDE.md` from the project root automatically.

```
your-django-project/
└── CLAUDE.md
```

**Steps:**
```bash
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" /path/to/your/project/CLAUDE.md
```
Claude Code loads `CLAUDE.md` on every session. No restart needed.

---

### GitHub Copilot (VS Code)

Copilot reads `.github/copilot-instructions.md` from the repository root automatically.

```
your-django-project/
└── .github/
    └── copilot-instructions.md
```

**Steps:**
```bash
mkdir -p .github
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" .github/copilot-instructions.md
```
Commit the file. Copilot loads it automatically in every VS Code workspace.

---

### Cursor

Cursor reads `.cursorrules` from the project root automatically.

```
your-django-project/
└── .cursorrules
```

**Steps:**
```bash
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" .cursorrules
```
Cursor picks it up immediately — no restart required.

---

### Windsurf

Windsurf reads `.windsurfrules` from the project root automatically.

```
your-django-project/
└── .windsurfrules
```

**Steps:**
```bash
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" .windsurfrules
```
Open Cascade — the rules are active in every conversation automatically.

---

### Kiro (Amazon)

Kiro reads all files in `.kiro/steering/` as persistent context. Steering files are always active.

```
your-django-project/
└── .kiro/
    └── steering/
        └── django-coding-rules.md
```

**Steps:**
```bash
mkdir -p .kiro/steering
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" .kiro/steering/django-coding-rules.md
```

---

### Continue

Continue reads rule files from `.continue/rules/`. Add `alwaysApply: true` front-matter to make it active in every conversation.

```
your-django-project/
└── .continue/
    └── rules/
        └── django-coding-rules.md
```

**Steps:**
```bash
mkdir -p .continue/rules
printf -- '---\nalwaysApply: true\n---\n\n' | cat - "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" > .continue/rules/django-coding-rules.md
```

> Without `alwaysApply: true`, Continue applies rules contextually. Add the front-matter to make them unconditional.

---

### Antigravity (Gemini Code Assist)

Antigravity reads `GEMINI.md` from the project root.

```
your-django-project/
└── GEMINI.md
```

**Steps:**
```bash
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md" GEMINI.md
```

> **Alternative:** reference it in `.gemini/config.yaml`:
> ```yaml
> context_files:
>   - GEMINI.md
> ```

---

### Quick Copy — All Instruction Files at Once

```bash
HOOK_SOURCE="/path/to/ai-dev-agent-kit/hooks/django hooks/HOOK.md"
cd /path/to/your/django/project

# Claude Code
cp "$HOOK_SOURCE" CLAUDE.md

# GitHub Copilot
mkdir -p .github
cp "$HOOK_SOURCE" .github/copilot-instructions.md

# Cursor
cp "$HOOK_SOURCE" .cursorrules

# Windsurf
cp "$HOOK_SOURCE" .windsurfrules

# Kiro
mkdir -p .kiro/steering
cp "$HOOK_SOURCE" .kiro/steering/django-coding-rules.md

# Continue (with alwaysApply front-matter)
mkdir -p .continue/rules
printf -- '---\nalwaysApply: true\n---\n\n' | cat - "$HOOK_SOURCE" > .continue/rules/django-coding-rules.md

# Antigravity
cp "$HOOK_SOURCE" GEMINI.md

echo "Done — Django coding instruction files deployed to all tools."
```

---

## Part 2 — Lifecycle Hooks

Lifecycle hooks run shell commands automatically at specific points in the AI tool's lifecycle — before/after file edits, at session start, etc. They provide **deterministic automation**: the AI always runs them, regardless of its own decision-making.

### Claude Code — `.claude/settings.json`

Claude Code supports lifecycle hooks via `.claude/settings.json` (project-level) or `~/.claude/settings.json` (global).

**Available events:**

| Event | When it fires |
|-------|--------------|
| `SessionStart` | When a session begins or resumes |
| `PreToolUse` | Before a tool call executes (can block it) |
| `PostToolUse` | After a tool call succeeds |
| `Stop` | When Claude finishes responding |
| `Notification` | When Claude needs your attention |
| `UserPromptSubmit` | When you submit a prompt |

**`claude-settings.json` — ready-to-use Django hooks:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/CLAUDE.md\" 2>/dev/null || true"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(jq -r '.tool_input.file_path // empty'); [[ \"$FILE\" == *.py ]] && python -m isort \"$FILE\" --quiet 2>/dev/null; [[ \"$FILE\" == *.py ]] && python -m black \"$FILE\" --quiet 2>/dev/null; exit 0"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(jq -r '.tool_input.file_path // empty'); for p in \".env\" \".env.local\" \"settings.py\" \"migrations/\"; do [[ \"$FILE\" == *\"$p\"* ]] && echo \"Blocked: $FILE is protected\" >&2 && exit 2; done; exit 0"
          }
        ]
      }
    ]
  }
}
```

**What each hook does:**
- `SessionStart` (startup) → re-injects `CLAUDE.md` into context after session resume or compaction
- `PostToolUse` (Edit|Write) → auto-runs `isort` + `black` on every Python file Claude edits
- `PreToolUse` (Edit|Write) → blocks edits to `.env`, `.env.local`, `settings.py`, and `migrations/`

**Setup:**

```bash
# Option A — copy the example
mkdir -p .claude
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/claude-settings.json" .claude/settings.json

# Option B — merge into existing .claude/settings.json manually
# Open .claude/settings.json and add the "hooks" key from the example file
```

> **Note:** Claude Code requires `jq` for the PostToolUse/PreToolUse commands. Install with `brew install jq` (macOS).

---

### VS Code Copilot — `.github/hooks/<name>.json`

VS Code Copilot reads hook files from `.github/hooks/` in your project root.

The format is simpler than Claude Code — no `matcher` or nested `hooks` array:

```json
{
  "hooks": {
    "EventName": [
      {
        "type": "command",
        "command": "your shell command here"
      }
    ]
  }
}
```

**`copilot-hooks.json` — Django hooks example:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "cat .github/copilot-instructions.md 2>/dev/null || true"
      }
    ]
  }
}
```

**Setup:**

```bash
mkdir -p .github/hooks
cp "/path/to/ai-dev-agent-kit/hooks/django hooks/copilot-hooks.json" .github/hooks/django-hooks.json
```

> You can have multiple `.json` files in `.github/hooks/` — Copilot loads all of them.

---

## Adding a New Framework Hook

1. Create a folder: `hooks/<framework> hooks/`
2. Create `HOOK.md` with that framework's architecture rules (instruction file)
3. Create `claude-settings.json` with framework-specific lifecycle hooks
4. Create `copilot-hooks.json` with Copilot lifecycle hooks
5. Update this `README.md` — add the new hook to the table above
6. Update the root `README.md`

