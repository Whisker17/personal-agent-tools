# Decision 002: Local Skills Convention

**Status:** Accepted
**Date:** 2026-05-16
**Issue:** WHI-429 (surfaced during review)

## Context

ADR 001 chose "defer skills" for v1, with `skills: []` as the default. Since then, the repo has organically grown two skill sourcing patterns:

1. **External skills** via `github:` refs (e.g., `github:Weizhena/Deep-Research-skills` for research-agent)
2. **Local skills** written directly in `skills/` (e.g., `skills/project-orchestration`, `skills/crypto-adversarial-review`, `skills/project-planner`, `skills/init-agents`, `skills/technical-writer-reporting`)

CLAUDE.md's Skills Management section states "Skills are git submodules referencing external repos. Skill content is not written in this repo." This no longer matches reality — 5 of 6 skills are local.

## Decision

Both patterns are legitimate. Update CLAUDE.md to reflect the dual convention:

| Pattern | When to Use | Example |
|---|---|---|
| **Local skill** (`skills/<name>/`) | Agent-specific workflow skills tightly coupled to this repo's agent configs. The skill's logic, references, and evals live alongside the config. | `skills/technical-writer-reporting` |
| **External skill** (`github:owner/repo`) | Reusable skills maintained independently, useful across multiple projects or agents beyond this repo. | `github:Weizhena/Deep-Research-skills` |

## Rationale

- Local skills for agent-specific workflows avoid the overhead of maintaining a separate repo for config-coupled logic that only this repo's agents use.
- External `github:` refs remain the right choice for shared, reusable skills that have independent versioning needs.
- The original submodule-only rule was a v1 simplification. The research pipeline now has 5 agents with distinct skill needs, making local skills a practical necessity.

## Consequences

- CLAUDE.md's Skills Management section is updated to document both patterns.
- `recommended-skills.yaml` continues to track external skills only. Local skills are tracked implicitly by their presence in `skills/` and their reference in agent YAML configs.
- The `systems/validate/validate` skill check already handles both patterns (local path existence check + `github:` regex match).
