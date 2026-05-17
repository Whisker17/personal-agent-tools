# Reporting Workflow Reference

## Inputs

- `project_id`
- `report_issue_id`
- `project_slug`
- `github_repo`, default `Whisker17/multica-research`

Primary inputs are Research Complete comments on the TW reserved issue, `{project_slug}/research-sections/_index.md`, and final section files.

## Preflight

Block before synthesis if:

1. any research issue lacks a Research Complete comment;
2. any referenced GitHub artifact is unreadable;
3. any section lacks adversarial approval or Orchestrator accept-risk;
4. any unresolved upstream blocker remains.

Critical unresolved findings can never be accepted through TW.

## Synthesis

1. Read Research Complete comments.
2. Read `_index.md`.
3. Read each final section.
4. Identify cross-section themes, contradictions, gaps, and narrative order.
5. Use thematic organization rather than issue-by-issue concatenation.
6. Preserve source traceability to issue ID and GitHub section path.
7. Mark TW-added conclusions as `[TW inference]`.

## Diagrams

Use `diagram-upgrade-guide.md` for decisions.

- Upgrade architecture/system topology diagrams when visual tooling is available.
- Keep process, sequence, and state diagrams as Mermaid unless a richer visual adds real clarity.
- Upgrade ASCII diagrams at least to Mermaid.
- Put assets under `{project_slug}/report/assets/`.

## Output Paths

- final report: `{project_slug}/report/final-report.md`
- assets: `{project_slug}/report/assets/`

Do not write elsewhere.

## Final Report Structure

- Executive Summary
- Thematic sections
- Cross-Cutting Analysis
  - Consensus
  - Conflicts
  - Open Questions
- Appendix
  - Input Research Sections
  - Sections Index Reference
  - Diagram Assets
  - Methodology Notes

## Completion Comment

Post Final Report Ready on the TW reserved issue. Include:

- final report path and commit;
- diagram assets path and commit;
- source sections aggregated;
- sections index path;
- inputs consumed with approval/accept-risk links;
- unresolved risks or integration gaps;
- target agent `@Orchestrator`.

Use `squad-communication-protocol.md` for exact message shape and fallback payload.

## Blockers

If a section is incomplete, contradictory beyond reconciliation, missing, or unreadable, notify Orchestrator on `report_issue_id`. Do not contact Research Agent directly.
