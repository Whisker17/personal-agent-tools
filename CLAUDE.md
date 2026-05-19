# personal-agent-tools

Multica component config source of truth. This repo stores agent definitions, squad orchestration records, autopilot schedules, project-level tools, and design decisions.

## Project Structure

- `agents/{agent-name}/` - Self-contained agent definition: `{agent-name}.yaml`, `instructions.md`, `skills/`, `README.md`
- `squads/{squad-name}/` - Squad composition and coordination instructions; no agent definitions
- `autocopilots/{autopilot-name}/` - Schedule config, runbook, and operational notes; no skills or fixtures
- `systems/init-agents/` - Project-level skill for designing or updating agent definitions
- `systems/validate/` - Validator and fixtures
- `DESIGN/` - Numbered design notes and decisions

Top-level `prompts/`, `skills/`, `knowledge/`, and `fixtures/` are deprecated. Put files under the component that owns them.

## Agent Config Spec

Each agent config lives at `agents/{name}/{name}.yaml`. The YAML `name` field is the Multica identity and must not be renamed during path-only migrations.

```yaml
name: <agent-name>                # Required. Lowercase with hyphens, must match directory and filename.
description: <one-liner>          # Required.
runtime: claude-code              # Required. One of: claude-code, codex, opencode.
model: <model-id>                 # Required.

system_instructions: agents/<agent-name>/instructions.md

skills: []                        # Local paths under the owning agent or github:owner/repo refs.
knowledge: []                     # Prefer skill references; use only when runtime access is verified.
max_concurrent_tasks: 1
custom_env: {}
custom_args: []
visibility: private
```

### Multica Field Mapping

| Repo Field | Multica Field | Notes |
|---|---|---|
| `name` | `name` | Direct mapping. |
| `description` | `description` | Direct mapping. |
| `runtime` | `runtime` | Direct mapping. |
| `model` | `model` | Direct mapping. |
| `system_instructions` | `instructions` | Repo stores a path; Multica receives file content. |
| `skills` | Attached skills | Local paths or `github:` refs need translation for Multica import. |
| `knowledge` | repo-only | Not a Multica native field. Use sparingly. |
| `custom_env` | `custom_env` | Direct mapping. |
| `custom_args` | `custom_args` | Direct mapping. |
| `max_concurrent_tasks` | `max_concurrent_tasks` | Direct mapping. |
| `visibility` | `visibility` | Direct mapping. |

### Validation Rules

Implemented by `systems/validate/validate`:

- `name`: non-empty, lowercase with hyphens, matches `agents/{name}/{name}.yaml`
- `description`: non-empty string
- `runtime`: one of `claude-code`, `codex`, `opencode`
- `model`: non-empty string
- `system_instructions`: must be `agents/{name}/instructions.md` and exist
- `skills`: each entry is a local path with `SKILL.md` or a valid `github:owner/repo` ref
- `knowledge`: each entry must exist
- `visibility`: one of `private`, `public` if present
- `max_concurrent_tasks`: positive integer if present
- `squads/research-squad/protocol.md` is the canonical squad communication protocol; skill-local copies must match it

## Authoring Standards

System instructions define role, inputs, boundaries, and required skills. Long workflows, templates, schemas, examples, CLI recipes, and domain references belong in the agent's `skills/{skill}/references/`.

When adding or updating an agent:

1. Create or update `agents/{name}/{name}.yaml`
2. Create or update `agents/{name}/instructions.md`
3. Put agent-specific skills under `agents/{name}/skills/`
4. Keep `knowledge: []` unless runtime access is verified
5. Run `systems/validate/validate`

## Current Agents

- `project-orchestrator-agent` - Coordinates planning, worker dispatch, quality gates, and final handoff
- `project-planner-agent` - Builds structured project issues and dependency graphs
- `research-agent` - Produces persisted outlines, drafts, and final sections
- `research-adversarial-agent` - Reviews persisted research artifacts
- `technical-writer-agent` - Aggregates accepted sections into final reports
- `repo-tracker-agent` - Produces GitHub repo intelligence reports for autopilot runs

## Skill Routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming -> invoke /office-hours
- Strategy/scope -> invoke /plan-ceo-review
- Architecture -> invoke /plan-eng-review
- Design system/plan review -> invoke /design-consultation or /plan-design-review
- Full review pipeline -> invoke /autoplan
- Bugs/errors -> invoke /investigate
- QA/testing site behavior -> invoke /qa or /qa-only
- Code review/diff check -> invoke /review
- Visual polish -> invoke /design-review
- Ship/deploy/PR -> invoke /ship or /land-and-deploy
- Save progress -> invoke /context-save
- Resume context -> invoke /context-restore
