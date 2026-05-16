# Decision 001: v1 Skill Source Strategy

**Status:** Accepted
**Date:** 2026-05-15
**Issue:** WHI-422

## Context

Each Multica agent config has a `skills` field. We need to decide how skills are sourced for v1 before the research pipeline has been E2E tested.

## Approaches Evaluated

### 1. Multica Built-in Discovery
- Browse and import skills via Multica UI during agent creation.
- **Pros:** Zero setup, integrated with the agent creation flow.
- **Cons:** Limited to Multica's index, entirely manual.

### 2. ClawHub + GitHub Manual Browse
- Manually search ClawHub (Multica's community skill discovery index) and GitHub for skills matching agent roles.
- **Pros:** Broader coverage than Multica alone.
- **Cons:** Time-consuming, no automation, no record of decisions.

### 3. Curated Allowlist (`recommended-skills.yaml`)
- Maintain a YAML file mapping agent roles to recommended skills with source, reason, and last-evaluated date.
- **Pros:** Documented decisions, easy to audit, version-controlled.
- **Cons:** Becomes stale without periodic review.

### 4. Defer Skills Entirely
- Keep `skills: []` for v1. Run the research pipeline with prompts and knowledge only. Add skills when E2E testing reveals a clear need.
- **Pros:** Simplest path, avoids premature optimization.
- **Cons:** May miss easy capability gains.

## Decision

**Option 4 (Defer)** for v1, with **Option 3 (Curated Allowlist)** as the mechanism when skills are eventually added.

## Rationale

- The research pipeline's core loop (research + review) relies on web search, document synthesis, and structured output. These are covered by system instructions and knowledge files — no external skill is required to make the pipeline functional.
- With only 2 agents, manual curation overhead is negligible, so there's no urgency to automate discovery.
- E2E testing (WHI-418) will produce concrete evidence of whether skills are needed. Deciding without that evidence risks wasted effort.
- When skills are needed, `recommended-skills.yaml` provides a lightweight, auditable mechanism that fits the project's scale.

## Trigger Conditions for Adding Skills

Skills should be added when any of the following signals emerge during E2E testing or operation:

| Signal | Example | Likely Skill Needed |
|--------|---------|-------------------|
| Agent cannot access a required external system | Research agent fails to clone/browse GitHub repos | `github-integration` |
| Agent output quality bottleneck traced to missing tool | Review agent cannot run code to verify claims | `code-execution` |
| Repeated manual intervention for a task the agent should handle | Manually converting formats before feeding to agent | Format-specific skill |

When a trigger fires:

1. **Evaluate:** Identify candidate skill via Multica UI, ClawHub, or GitHub.
2. **Record:** Add an entry to `knowledge/shared/decisions/recommended-skills.yaml` with `status: evaluating`, source, reason, and date.
3. **Activate:** After validation, add the skill as a git submodule (`git submodule add <url> skills/<name>`), update the entry status to `active`, and update the relevant agent YAML config's `skills` field.

## Consequences

- `skills: []` stays in both agent configs for now. No submodules added.
- `recommended-skills.yaml` schema is defined but left empty until a trigger fires.
- No discovery agent is built.
- **Revisit trigger:** When WHI-418 (E2E testing) closes, open a follow-up issue to re-evaluate whether skills are needed based on test results.
