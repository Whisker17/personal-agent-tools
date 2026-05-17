# personal-agent-tools

Multica agent config source-of-truth. Stores agent initialization configs (YAML) that map to Multica's agent creation flow, AI-written system prompts, knowledge files, and external skill references.

## v1 Direction

This repo is a **configuration hub**, not a skills library. It manages agent definitions for Multica — it does not publish, distribute, or implement skills. Skills are referenced from external sources via git submodules.

The design doc (`~/.gstack/projects/personal-agent-tools/whisker-main-design-20260515-160816.md`) proposed a broader "self-maintaining agent skills library" direction with SKILL.md publishing, install scripts, and workflows/. That direction is **deferred, not adopted**. It may be revisited after M1 E2E testing (WHI-418) validates the config-repo approach. See WHI-423 for the full rationale.

## Project Structure

- `agents/` - Agent init configs, one YAML file per agent
- `prompts/system/` - Per-agent system instructions (AI-written)
- `prompts/shared/` - Reusable prompt fragments across agents (AI-written)
- `skills/` - External skill repos (git submodules, not written in this repo)
- `knowledge/shared/` - Domain knowledge shared across all agents
- `knowledge/shared/decisions/` - Architectural decision records (numbered ADRs)
- `knowledge/per-agent/` - Agent-specific knowledge
- `scripts/` - Helper scripts (validate, init-agent, sync-skills)
- `fixtures/validate/` - Test fixtures for validator testing
- `examples/` - Example inputs/outputs and test run artifacts

## Agent Config Spec

Each agent config lives at `agents/<agent-name>.yaml`. Field names are aligned with Multica's API.

```yaml
name: <agent-name>                # Required. Lowercase with hyphens, must match filename.
description: <one-liner>          # Required. One-line description.
runtime: claude-code              # Required. One of: claude-code, codex, opencode.
model: <model-id>                 # Required. Model ID string.

system_instructions: <path>       # Required. Path to file under prompts/system/.
                                  # Multica receives the file *content*, not the path.

skills: []                        # Optional. Local submodule paths or remote refs (github:user/repo).
knowledge: []                     # Optional. Repo-only. Paths to knowledge files (see below).
max_concurrent_tasks: 1           # Optional. Default: 1. Multica default is 6.
custom_env: {}                    # Optional. Passed to agent runtime.
custom_args: []                   # Optional. Additional flags for the AI tool.
visibility: private               # Optional. One of: private, public. Default: private.
```

### Multica Field Mapping

| Repo Field | Multica Field | Notes |
|---|---|---|
| `name` | `name` | Direct mapping. |
| `description` | `description` | Direct mapping. |
| `runtime` | `runtime` | Direct mapping. |
| `model` | `model` | Direct mapping. |
| `system_instructions` | `instructions` | Repo stores file path; Multica receives file content. |
| `skills` | Attached skills | Local paths or `github:` refs need translation for Multica import. |
| `knowledge` | **repo-only** | NOT a Multica native field. Referenced inside system prompts via `Read`. |
| `custom_env` | `custom_env` | Direct mapping. |
| `custom_args` | `custom_args` | Direct mapping. |
| `max_concurrent_tasks` | `max_concurrent_tasks` | Direct mapping. |
| `visibility` | `visibility` | Direct mapping. |

### Translation: YAML Config to Multica Agent

1. Read the file at `system_instructions` path and paste its **content** into Multica's `instructions` field.
2. `knowledge` paths are informational only — they are referenced inside the system prompt, not passed to Multica directly.
3. `skills` entries need translation: local submodule paths become Multica workspace skills or GitHub imports.
4. All other fields map directly to Multica's API by name.

### Security Warning

`custom_env` values are stored as **plaintext** in Multica's server database. Do not put high-value secrets (API keys, private keys, passwords) in this field.

### Validation Rules

These rules are implemented by `scripts/validate` (see WHI-424):

- `name`: non-empty, lowercase with hyphens, matches filename (`agents/{name}.yaml`)
- `description`: non-empty string
- `runtime`: one of `claude-code`, `codex`, `opencode`
- `model`: non-empty string
- `system_instructions`: path exists relative to repo root
- `skills`: each entry is a local path that exists OR a `github:` prefixed remote ref
- `knowledge`: each entry is a path that exists relative to repo root
- `visibility`: one of `private`, `public` (if present)
- `max_concurrent_tasks`: positive integer (if present)

### Open Questions

1. **`mcp_config`**: Multica may support MCP server configuration. Deferred — add when needed.
2. **Versioning**: No version field yet. For personal use, always run latest.
3. **`knowledge` runtime accessibility**: Need to verify agents on Multica can `Read` knowledge files from the execution context.

## Prompt Authoring Standards

When writing system instructions, follow these conventions:

1. Open with a clear agent role and objective
2. Define the input schema (what format the agent receives)
3. Define the output schema (what format the agent must produce)
4. List work steps (numbered)
5. Include error handling instructions
6. Reference shared fragments in `prompts/shared/` via `Read` instead of copy-pasting

Shared prompts use relative paths: `prompts/shared/<name>.md`

### Prompt vs Knowledge Boundary

- `prompts/shared/` contains **evaluation criteria, templates, and reusable instructions** — HOW to evaluate or process something.
- `knowledge/shared/` contains **domain knowledge, benchmarks, and reference data** — WHAT "good" looks like.

Rule of thumb: if it tells the agent what steps to follow or how to judge quality, it belongs in `prompts/shared/`. If it provides facts, examples, or standards the agent references during those steps, it belongs in `knowledge/shared/`.

## Skills Management

Skills use two sourcing patterns (see ADR 002):

### Local skills (`skills/<name>/`)
Agent-specific workflow skills written directly in this repo. Use when the skill is tightly coupled to an agent config in this repo and has no reuse need outside it.

- Create: `mkdir -p skills/<name>` and add `SKILL.md` + optional `references/`
- These are NOT submodules — they are version-controlled alongside agent configs

### External skills (`github:owner/repo`)
Reusable skills maintained in separate repos. Use when the skill is useful across multiple projects or has independent versioning needs.

- Add: `git submodule add <url> skills/<name>`
- Update: `git submodule update --remote --merge`

## Knowledge Base

- `knowledge/shared/` - Markdown documents organized by topic, referenceable by all agents
- `knowledge/shared/decisions/` - Architecture Decision Records (ADRs), numbered sequentially (`001-*.md`)
- `knowledge/per-agent/<agent-name>/` - Agent-specific context
- Agent configs declare knowledge dependencies via the `knowledge` field

### Knowledge File Conventions

- **Strict access**: agents only read knowledge files explicitly listed in their YAML config `knowledge` field — no automatic discovery. (Access mechanism on Multica is unverified pending WHI-418; see Open Questions.)
- Each knowledge file should include a `last_updated: YYYY-MM-DD` date in its YAML frontmatter or as a heading-level note.
- Tentative file size guideline: keep individual knowledge files under 50KB. Larger files should be split by subtopic. (Will be refined after M1 E2E testing provides real-world data on agent context limits.)

## Standard Workflow for Adding a New Agent

1. Create `agents/<agent-name>.yaml` config file
2. Write `prompts/system/<agent-name>.md` system instructions
3. If shared prompt fragments are needed, add to `prompts/shared/`
4. If agent-specific knowledge is needed, create `knowledge/per-agent/<agent-name>/`
5. If new skills are needed, create locally in `skills/<name>/` (agent-specific) or add via `git submodule add` (reusable/external)
6. Create the agent on Multica following the config, attach corresponding skills

## Linear Status Sync Rules

- When a file documented in a Linear issue is created locally, move the corresponding Linear issue to **In Progress**.
- When a local file is a draft pending review, add a Linear comment noting "existing local draft, not accepted yet" so the issue reflects the true state.
- Do not mark issues as Done until the file has been reviewed and accepted.

## Current Agents

- **research-agent** - Researches a given topic, produces structured reports
- **research-adversarial-agent** - Adversarial reviewer for crypto/DeFi research reports (GPT-5.5 via Codex)
- **project-planner-agent** - Reads Multica project descriptions and creates structured Milestones + Issues via Multica CLI
- **project-orchestrator-agent** - Orchestrates end-to-end project execution by dispatching planning, work, and review to specialized agents
- **technical-writer-agent** - Aggregates completed research sections into the final project report

## Skill routing

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
