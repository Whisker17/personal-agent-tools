---
name: init-agents
description: >
  Use when designing, creating, or updating a Multica agent config, system prompt, parameter set,
  skill attachment list, or new local skill for an agent.
triggers:
  - "init agent"
  - "create agent"
  - "new agent"
  - "init-agents"
  - "design agent"
---

# Init Agents

Design Multica agents with thin prompts and self-contained skills.

## References

Load as needed:

- `references/agent-authoring-workflow.md` — prompt boundary, discovery questions, prompt template, skill placement, and validation.
- `references/decisions/001-v1-skill-source-strategy.md` — skill source strategy.
- `references/decisions/recommended-skills.yaml` — current skill allowlist.

## Workflow

1. Discover purpose, I/O, domain, parameters, and needed skills.
2. Draft a thin system prompt: identity, capabilities, boundaries, inputs, required skills.
3. Put workflow details into an existing or new skill, using `references/` for long material.
4. Generate or update the agent YAML.
5. Run `scripts/validate`.

## Rules

- Ask one discovery question at a time.
- Do not put long procedures, templates, schemas, examples, or CLI guides in system prompts.
- Prefer skill references over repo-level `knowledge`.
- Use `knowledge: []` unless the runtime explicitly requires otherwise.
- Follow `CLAUDE.md` for repository schema and file placement.
