# Deep Output Workflow Reference

## Modes

- Initial draft: no `adversarial_feedback`, no `promote`.
- Revision: `adversarial_feedback` present.
- Final promotion: `promote: true`.

All modes write to `branch_name`, default `research/{project_slug}/{topic_slug}`. If the runtime starts on any other branch, switch to `branch_name` before reading or writing artifacts.

## Load and Validate Outline

Fetch the approved outline from `outline_path` or use `outline_content`. Verify:

- status is `approved`;
- `project_slug`, `topic_slug`, `github_repo`, and `artifact_paths.*` are present and consistent;
- Items, Fields, Diagram Expectations, and Source Requirements are parseable.

Candidate outlines are blocked; deep research requires Orchestrator approval.

## Research Process

For each item in dependency and priority order:

1. Run targeted web research using recent, authoritative, primary sources where possible.
2. If `codebase_path` is provided, inspect relevant code and compare implementation to public docs.
3. For each applicable field, write content, sources, and confidence.
4. Mark unavailable evidence as a gap rather than inventing support.

Use `research-methodology.md` for source hierarchy and integrity rules.

## Draft Structure

Drafts are markdown files with frontmatter:

- `topic`, `project_slug`, `topic_slug`, `github_repo`
- `round`, `status: draft`
- `artifact_paths`
- `draft_metadata`

Body sections:

1. Executive Summary
2. Item Findings
3. Diagrams
4. Source Coverage
5. Gap Analysis
6. Revision Log

## Persistence

Before writing, fetch the target repo and switch to `branch_name`. If the branch does not exist, create it from latest `origin/main` and push it.

Persist every draft before adversarial review:

`{project_slug}/research-sections/{topic_slug}/drafts/round-{n}.md`

Commit and push to `branch_name`. Return path, work branch commit URL/SHA, branch name, round, mode, items covered, fields investigated, diagrams produced, source requirement coverage, and gaps.

## Final Promotion

Only run when `promote: true`.

### Always Required Inputs

- `approved_draft_path`
- `approved_draft_round`
- `approved_draft_commit`
- `approval_evidence`
- `multica_issue_id`
- `project_slug`
- `topic_slug`
- `github_repo`
- `branch_name`
- `round`

### Composable Mode Only (when `report_issue_id` is present)

Also required: `order`, `dependencies`.

Fetch the approved draft, verify the commit, write:

`{project_slug}/research-sections/{topic_slug}/final.md`

Commit and push to `branch_name`. Return final path, final branch commit, reviewed draft identity, approval evidence, and Index Entry Proposal. The main integration commit is produced later by Orchestrator, not by this skill.

### Lightweight Mode (no `report_issue_id`)

`order` and `dependencies` are not required. No Index Entry Proposal is produced.

Fetch the approved draft, verify the commit, write:

`{project_slug}/research-sections/{topic_slug}/final.md`

Commit and push to `branch_name`. Return final path, final branch commit, reviewed draft identity, and approval evidence. The Final Promotion Ready message must include `Target agent: @Orchestrator` and `Next action: @Orchestrator integrate final.md to main, delete branch, run lightweight Done Gate, and close research issue`.

Do not write `_index.md` in either mode.

## TW Handoff Boundary

This skill covers final promotion and the information needed for Final Promotion Ready. In squad/composable mode, Research Complete happens only after Orchestrator integrates the final section and `_index.md` to `main` and provides `main_merge_commit`. In single-issue lightweight mode (Orchestrator dispatch without `report_issue_id`), the pipeline ends at Final Promotion Ready — Research Agent does not post Research Complete or Done Gate Request.

Use `squad-communication-protocol.md` for exact Final Promotion Ready, Research Complete, Done Gate Request, and BLOCKED templates.

## Quality Checklist

- Required frontmatter present.
- Current git branch matches `branch_name`.
- Artifact paths match outline.
- Every outline item and applicable field covered.
- Every factual claim has a real source or is marked uncertain.
- Source Coverage accounts for all requirements.
- Diagrams match outline expectations.
- Gap Analysis is honest.
- Revision mode addresses flagged items and preserves unflagged content.

## Error Handling

- Missing `gh` or repo access: BLOCKED.
- Outline not approved: BLOCKED.
- Missing slug or artifact paths: BLOCKED.
- Push failure: retry once, then BLOCKED.
- Unmet source requirements: proceed only if clearly surfaced in Gap Analysis.
