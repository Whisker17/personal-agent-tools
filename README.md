# personal-agent-tools

Configuration hub for Multica components.

This repo stores self-contained agent definitions, squad orchestration records, autopilot schedules, project-level tools, and design notes. Agent YAML `name` values are Multica identities and should stay stable across file moves.

## Directory Structure

```text
personal-agent-tools/
├── agents/           # One directory per agent: YAML, instructions, skills, README
├── squads/           # Thin orchestration records; no agent definitions
├── autocopilots/     # Thin scheduling records and runbooks
├── systems/          # Project-level tools such as init-agents and validate
└── DESIGN/           # Numbered design notes and decisions
```

Deprecated top-level directories such as `prompts/`, `skills/`, `knowledge/`, and `fixtures/` have been folded into the component that owns the files.

## Agent Definition

Each agent lives at `agents/{name}/`:

```text
agents/research-agent/
├── research-agent.yaml
├── instructions.md
├── skills/
│   ├── research-outline/
│   └── research-deep-output/
└── README.md
```

Example config:

```yaml
name: research-agent
description: Deep research analyst for crypto/DeFi topics
runtime: claude-code
model: claude-sonnet-4-6

system_instructions: agents/research-agent/instructions.md

skills:
  - agents/research-agent/skills/research-outline
  - agents/research-agent/skills/research-deep-output

knowledge: []
max_concurrent_tasks: 1
visibility: private
```

## Squads And Autocopilots

- `squads/research-squad/` records the four-agent runtime research squad composition and coordination protocol. Project Planner remains a separate pre-planning tool.
- `autocopilots/repo-tracker/` records the repo-tracker schedule and operations runbook.

These layers reference agents; they do not duplicate agent skills or instructions.

## Validation

Run:

```bash
./systems/validate/validate
```

For a single agent:

```bash
./systems/validate/validate --agent repo-tracker-agent
```

Repo-tracker regression checks:

```bash
./agents/repo-tracker-agent/skills/repo-tracker/scripts/test-repo-tracker.py
```
