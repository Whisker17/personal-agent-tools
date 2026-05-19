# Research Review Workflow Reference

## Modes

- `review_type=outline`: use structured outline review and patch proposal.
- `review_type=draft`: review the persisted draft at the specified path and commit.

## Branch and Artifact Access

This agent is read-only. Fetch the specified `artifact_commit` from `github_repo` and review the artifact at `artifact_path`; do not create branches, switch work branches for writes, or persist revised research artifacts. If the referenced commit or path is unreadable, report `BLOCKED` to Orchestrator.

## Outline Review

Use `research-outline-schema.md` to validate structure.

Evaluate:

1. Structural integrity.
2. Coverage completeness.
3. Field quality.
4. Diagram and source adequacy.
5. Research feasibility.

Patch operations:

- `add_item`, `remove_item`, `modify_item`
- `add_field`, `remove_field`, `modify_field`
- `add_diagram`, `remove_diagram`, `modify_diagram`
- `add_source_req`, `modify_source_req`

Do not modify `project_slug`, `topic_slug`, `github_repo`, or `artifact_paths.*`.

Return an advisory report and full updated outline proposal. Do not persist changes.

## Draft Review

Fetch the persisted draft at `artifact_path` and verify `artifact_commit`. Also fetch the approved outline for coverage checks.

Attack surfaces:

1. fabricated or unverifiable sources;
2. logical gaps;
3. outline coverage gaps;
4. source-claim mismatch;
5. confidence inflation;
6. hidden gaps;
7. diagram inaccuracy;
8. stale sources for current-state claims;
9. missing counterarguments;
10. cross-item contradictions.

For high-risk claims, independently spot-check sources, claim support, freshness, and diagram correctness. Record verification results.

Use `research-methodology.md` for source hierarchy and integrity rules.

## Verdict Rules

Outline:

- critical or major issue: `outline-needs-revision`;
- no critical/major issue and no patch required: `outline-approved`.

Draft:

- any critical finding: `reject`;
- any major finding or confidence under 0.6: `needs-attention`;
- no critical findings, fewer than 3 major findings, confidence at least 0.6: `approve`.

Only Orchestrator decides whether to advance.

## Finding Standards

Every finding must include:

- what can fail;
- why it is weak;
- impact;
- suggested fix;
- grounding evidence or explicit `[INFERRED]` marker.

Skip style-only or tone-only findings.

## Communication

Post verdict comments to the Multica research issue. Use `squad-communication-protocol.md` for exact templates and fallback payloads.

If the runtime cannot post comments, emit the full pending action payload for Orchestrator to relay.
