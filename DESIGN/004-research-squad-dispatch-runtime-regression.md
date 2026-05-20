# Decision 004: Research Squad Dispatch Runtime Regression

**Status:** Implemented
**Date:** 2026-05-20
**Issue:** WHI-441

## Context

Multica runtime issue UUID `2e44db1f-a572-47a4-b25e-ea1e2f0fa358` (Multica number 49) exposed three research squad workflow failures:

1. Dispatch comments triggered non-target agents because the full agent list used triggerable `mention://agent/` links.
2. Run history was hard to read as a timeline because `multica issue runs` default output is newest-first, while issue comments can be grouped by parent comment.
3. Orchestrator stopped after an intermediate "revision applied" message instead of posting the next review dispatch in the same run.

## Evidence

Representative trigger comments:

| Trigger comment | Intended target | Actual extra runs | Root cause |
|---|---|---|---|
| `9987708e` | Deep Research Agent | Research Review Agent, Technical Writer Agent | Dispatch included a full triggerable agent list |
| `f27eb792` | Research Review Agent | Deep Research Agent, Technical Writer Agent | Dispatch included a full triggerable agent list |
| `af3dcdf1` | Research Review Agent | Deep Research Agent, Technical Writer Agent, Project Planner | Dispatch included Project Planner's `mention://agent/969dcafe-8ede-4ef6-a293-f747c6f202e1` |
| `b5c3442f` | Research Review Agent | Deep Research Agent, Technical Writer Agent, Project Planner | Dispatch included Project Planner's `mention://agent/969dcafe-8ede-4ef6-a293-f747c6f202e1` |

Project Planner was not triggered by a hidden subscription mechanism in this sample. It was explicitly mentioned in draft review round 1 and round 2 dispatch comments. That means the primary fix is to remove all non-target triggerable mention links from dispatch bodies.

## Decision

Research squad dispatch and handoff comments now use a single-target trigger model:

- Each dispatch or continuous handoff contains exactly one `mention://agent/` link.
- The only full mention link must be the current `Target agent`.
- Non-target agent IDs are provided in a non-triggering `Agent Directory` as bare UUIDs.
- Worker agents build exactly one target mention from the Agent Directory and do not call `multica agent list`.
- Non-target guards must not write Multica issue comments. If runtime does not allow silent exit, agents use cancel/no-op and record the limitation in runtime output.
- Orchestrator must finish continuous stages by posting the next dispatch, posting a terminal state, or emitting `=== PENDING MULTICA ACTIONS ===`.
- Timeline readers sort comments and runs by `created_at` ascending, then use `phase` and `round`; no `event_seq`, `parent_event`, or daemon watchdog is used.

## Implementation

Updated local source:

- `squads/research-squad/protocol.md`
- `squads/research-squad/instructions.md`
- Runtime agent instructions for Orchestrator, Research Agent, Research Review Agent, Technical Writer Agent, and Project Planner
- Skill references for `project-orchestration`, `research-outline`, `research-deep-output`, `research-review`, `technical-writer-reporting`, and `project-planner`
- `systems/validate/validate` with a `research-dispatch-policy` check

Updated deployed Multica objects:

- Agents: Orchestrator, Deep Research Agent, Research Review Agent, Technical Writer Agent, Project Planner
- Squad: Research Squad
- Skills: `project-orchestration`, `research-outline`, `research-deep-output`, `research-review`, `technical-writer-reporting`, `project-planner`

## Verification

Local:

```bash
python3 -m unittest systems.validate.test_validate
./systems/validate/validate
git diff --check
```

Deployed:

- Deployed agent instruction checks confirm the runtime squad agents now contain `Agent Directory`, no `Agent Roster`, and `exactly one` mention guidance.
- Deployed squad instruction check confirms `Agent Directory`, no `Agent Roster`, and the non-target "do not post a Multica issue comment" guard.
- Deployed skill file checks confirm all six updated skills contain `Agent Directory` and no `Agent Roster` / `from-roster` references.

## Remaining Validation

A new Multica single-issue lightweight E2E run is still required before closing WHI-441. It should verify that each dispatch creates one target run, no non-target comments are posted, and no human continuation comment is needed after the initial trigger.
