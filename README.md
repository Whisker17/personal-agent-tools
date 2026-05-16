# personal-agent-tools

Configuration hub for Multica agents. This repo is the source-of-truth for agent configs that map to Multica's agent creation flow, including AI-written system prompts and knowledge files referenced at runtime.

This repo manages agent **definitions**, not skill implementations. Skills are referenced from external sources via git submodules — they are not authored or published from this repo. A broader skills-library direction was considered and deferred for v1 (see CLAUDE.md for details).

## Directory Structure

```
personal-agent-tools/
├── agents/                  # Agent init configs (one YAML per agent)
│   └── research-agent.yaml  # Example: research agent config
├── prompts/                 # AI-written system prompts and instructions
│   ├── system/              # Per-agent system instructions
│   └── shared/              # Reusable prompt fragments across agents
├── skills/                  # External skill repos (git submodules)
├── knowledge/               # Agent context and knowledge base
│   ├── shared/              # Knowledge accessible to all agents
│   └── per-agent/           # Agent-specific knowledge
├── scripts/                 # Helper scripts
│   ├── init-agent           # Initialize new agent from YAML config
│   └── sync-skills          # Update all skill submodules
├── fixtures/                # Test fixtures for validation scripts
├── examples/                # Example inputs/outputs and test run artifacts
└── CLAUDE.md                # Project conventions and agent dev standards
```

## Quick Start

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>

# Update all skill submodules
git submodule update --remote --merge

# Add a new external skill
git submodule add <skill-repo-url> skills/<skill-name>
```

## Agent Init Config

Each agent has a YAML config under `agents/`, defining everything needed to create the agent on Multica:

```yaml
# agents/research-agent.yaml
name: research-agent
description: Research a topic, gather sources, extract attributed claims
runtime: claude-code
model: claude-sonnet-4-6

system_instructions: prompts/system/research-agent.md

skills:
  - skills/gstack              # Local submodule path
  - github:user/skill-repo     # Or remote GitHub reference

knowledge:
  - knowledge/shared/research-methodology.md
  - knowledge/per-agent/research-agent/

max_concurrent_tasks: 1
visibility: private

custom_env: {}
custom_args: []
```

Field names are aligned with Multica's API. See CLAUDE.md for the full field mapping table and translation steps.

Adding a new agent:
1. Create YAML config under `agents/`
2. Write system instructions under `prompts/system/`
3. Add skill submodules as needed
4. Create the agent on Multica using the config (see CLAUDE.md for field mapping)

## Skills Management

Skills are external repos referenced as git submodules, staying in sync with upstream:

```bash
# Add a new skill
git submodule add https://github.com/user/skill-repo skills/skill-name

# Update all skills to latest
git submodule update --remote --merge

# Update a single skill
cd skills/skill-name && git pull origin main
```

Skills are consumed as-is from upstream repos. This repo does not publish or distribute skills.

## Prompts

All content under `prompts/` is AI-written and maintained:

- `prompts/system/` - Full system instructions per agent
- `prompts/shared/` - Reusable prompt fragments (evaluation criteria, output format templates, etc.)

Prompt authoring principles:
- Define input/output schemas explicitly
- Include error handling instructions (malformed input, unavailable tools, etc.)
- Reference shared fragments in `prompts/shared/` instead of duplicating content

## Knowledge Base Design

`knowledge/` stores domain knowledge and context for agents, organized in two tiers:

**shared/** - General knowledge accessible to all agents
- Research methodology, evaluation frameworks, domain glossaries
- Format: Markdown documents, organized by topic

**per-agent/** - Agent-specific knowledge
- One subdirectory per agent for specialized context
- Historical research reports, domain expert compilations, common data source catalogs

Knowledge files are declared in the agent config's `knowledge` field and loaded at runtime via the Read tool.

**Boundary with prompts/shared/**: `prompts/shared/` contains evaluation criteria, templates, and reusable instructions (HOW to evaluate). `knowledge/shared/` contains domain knowledge, benchmarks, and reference data (WHAT "good" looks like). See CLAUDE.md for the full convention.

## First Experiment: Research Pipeline

1. **research-agent** - Takes a research topic, gathers sources, extracts attributed claims, outputs a structured research report
2. **research-adversarial-agent** - Adversarial reviewer that challenges claims, probes logical gaps, and stress-tests assumptions

Flow: research-agent produces report -> research-adversarial-agent reviews -> if needs-attention, feeds revision instructions back
