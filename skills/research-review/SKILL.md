---
name: research-review
description: >
  Adversarial review of research outlines. Evaluates structural integrity, coverage completeness,
  field quality, and research feasibility, then produces concrete, traceable patches. Output
  includes a verdict, patch summary, detailed findings, and the full updated outline. Use this
  skill whenever you need to review a research outline, challenge outline quality, find gaps in
  research structure, propose outline improvements, or do adversarial quality checks on research
  plans. Trigger on: 'review this outline', 'check the outline', 'audit the research plan',
  'find gaps', 'improve this outline', or any request to critically evaluate a research outline.
allowed-tools:
  - Bash
  - Read
  - WebSearch
  - WebFetch
---

# /research-review

Review an existing research outline and produce structured patches. This is the Adversarial Agent's primary tool during Phase A — it reads a candidate outline, evaluates it against research quality standards, and proposes specific, traceable modifications.

The review is opinionated but constructive: it identifies gaps, weak items, missing fields, and structural problems, then produces concrete patches rather than vague suggestions. Acceptance of the patches is the Orchestrator's decision, not this command's.

The outline conforms to the shared schema at `knowledge/shared/research-outline-schema.md` — read it before reviewing.

## Input

The invoking agent provides these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `outline_path` | yes (or `outline_content`) | GitHub path to the current outline (e.g., `{project_slug}/outlines/{topic_slug}.md`) |
| `outline_content` | yes (or `outline_path`) | Inline outline content. Use when the outline hasn't been persisted yet |
| `project_slug` | yes | Stable project identifier |
| `topic_slug` | yes | Stable topic identifier (never a Linear issue ID) |
| `github_repo` | no | GitHub repo. Default: `Whisker17/multica-research` |
| `artifact_commit` | no | Commit URL/SHA for the outline artifact. If provided, fetch the outline at this exact commit |
| `artifact_paths` | no | Object with `outline`, `draft`, `final`, `index` paths. If provided by Orchestrator, use these verbatim and verify the outline's internal artifact_paths match. If omitted, trust the outline's own artifact_paths |
| `review_focus` | no | Specific areas to scrutinize. If omitted, review the full outline |
| `review_finding` | no | Specific finding or concern from Orchestrator to evaluate |
| `requested_changes` | no | Explicit requested additions or modifications to items, fields, diagram expectations, or source requirements |
| `prior_patches` | no | Summary of patches from previous rounds that were rejected, to avoid re-proposing them |

## Process

### Step 1: Load and Parse the Outline

1. If `outline_path` is provided, fetch from GitHub:

```bash
REPO="<github_repo or Whisker17/multica-research>"
OUTLINE_PATH="<outline_path>"
ARTIFACT_COMMIT="<artifact_commit, if provided>"

REPO_DIR=$(mktemp -d)
gh repo clone "$REPO" "$REPO_DIR"
cd "$REPO_DIR"

if [ -n "$ARTIFACT_COMMIT" ]; then
  COMMIT_REF="${ARTIFACT_COMMIT##*/}"
  git checkout "$COMMIT_REF"
  test "$(git rev-parse HEAD)" = "$(git rev-parse "$COMMIT_REF")"
fi

cat "$OUTLINE_PATH"
```

2. If `outline_content` is provided, use it directly.

3. Parse the outline's YAML frontmatter and markdown body. Verify all required schema fields are present by checking against `knowledge/shared/research-outline-schema.md`. Missing required fields are themselves findings.

4. Verify context consistency:
   - `project_slug`, `topic_slug`, and `github_repo` in the outline must match the invocation.
   - If `artifact_paths` was provided by Orchestrator, every `artifact_paths.*` value in the outline must match it exactly.
   - If `artifact_paths` was not provided, preserve the outline's existing `artifact_paths.*` values unchanged.

5. Record the current `round` number. The patched outline will use `round + 1`.

### Step 2: Evaluate the Outline

Apply these evaluation lenses in order. Each lens produces zero or more findings.

**Lens 1: Structural Integrity**

Check that the outline conforms to the shared schema:
- All required frontmatter fields present and non-empty
- `project_slug`, `topic_slug`, `github_repo`, `artifact_paths.*` all consistent and correctly computed
- Item IDs follow `item-{N}` format and are unique
- Field names are snake_case
- Diagram IDs follow `diag-{N}` format
- Source requirement IDs follow `src-{N}` format
- `applies_to` references in fields, diagrams point to valid item IDs or `all`
- Patch Log is present (empty is fine for round 1)

**Lens 2: Coverage Completeness**

Evaluate whether the items together cover the research question fully:
- **Gap analysis**: are there important subtopics the outline misses? Run 2-3 targeted web searches to verify coverage against the current state of the topic.
- **Overlap detection**: do any items substantially overlap? If so, propose merging or sharpening boundaries.
- **Scope drift**: do any items stray beyond the stated scope? Flag items that investigate tangential topics.
- **Dependency coherence**: are item dependencies correctly specified? An item studying "performance optimization" should depend on the item covering "architecture".

**Lens 3: Field Quality**

Evaluate whether the fields will produce useful, actionable findings during deep research:
- **Answerability**: can a researcher actually produce concrete data for each field? Vague fields like `general_observations` are weak.
- **Comparability**: fields applying to `all` items should produce findings that can be meaningfully compared across items.
- **Completeness**: given the topic's domain, are important investigation dimensions missing? (e.g., security research without an `audit_status` field, market research without `competitive_landscape`)
- **Redundancy**: do any fields overlap significantly? Propose merging or differentiating.

**Lens 4: Diagram and Source Adequacy**

- Are diagram expectations specific enough that a researcher knows what to produce?
- Do diagram types match the content? (architecture topics need architecture diagrams, not timelines)
- Are source requirements realistic and sufficient? Too few sources risks single-source dependency; too many risks scope explosion.
- Are source types appropriate for the topic's domain?

**Lens 5: Research Feasibility**

Consider whether the outline is actually executable:
- Can each item be researched with publicly available information and the specified source types?
- Is the total scope realistic for a single research pass, or does it need scoping down?
- Are there items that require access to proprietary data or systems the researcher may not have?

### Step 3: Formulate Patches

For each finding, decide on a concrete action. Every patch must be one of these operations:

| Action | Target | Description |
|--------|--------|-------------|
| `add_item` | new item ID | Add a missing subtopic |
| `remove_item` | existing item ID | Remove a redundant or out-of-scope item |
| `modify_item` | existing item ID | Change description, priority, or dependencies |
| `add_field` | new field name | Add a missing investigation dimension |
| `remove_field` | existing field name | Remove a redundant or unanswerable field |
| `modify_field` | existing field name | Change description or `applies_to` |
| `add_diagram` | new diagram ID | Add a missing diagram expectation |
| `remove_diagram` | existing diagram ID | Remove an unhelpful diagram expectation |
| `modify_diagram` | existing diagram ID | Change type, description, format, or `applies_to` |
| `add_source_req` | new source req ID | Add a missing source requirement |
| `modify_source_req` | existing source req ID | Change description or min_count |

Rules for patches:
- **New fields apply broadly** — when adding a field, default `applies_to: all` unless there's a clear reason it only applies to specific items.
- **New items inherit universal fields** — when adding an item, it automatically gets all fields with `applies_to: all`.
- **No renumbering** — removing `item-3` leaves a gap; the next new item is `item-{max+1}`, not `item-3`.
- **No identity changes** — never modify `project_slug`, `topic_slug`, `github_repo`, or `artifact_paths.*`.
- **Each patch needs justification** — a reason tied to a finding, not just "could be better".
- **Idempotency first** — before adding anything, check whether an equivalent field, item, diagram, source requirement, or Patch Log entry already exists. If it exists, modify or reference it instead of duplicating it.
- **Requested changes are inputs, not commands** — apply `review_finding` and `requested_changes` only when they are consistent with the outline and schema; otherwise report the conflict in Remaining Gaps.

If `prior_patches` mentions rejected patches, do not re-propose the same changes unless the outline context has shifted enough to justify revisiting.

### Step 4: Apply Patches to Produce Updated Outline Proposal

Apply all patches to produce the updated outline document **in memory only**. This skill does NOT persist the updated outline to GitHub — acceptance is the Orchestrator's decision. The Orchestrator (or Research Agent on Orchestrator's instruction) performs the actual write after accepting the proposal.

1. Apply all patches to produce the updated outline document:
   - Increment `round` by 1
   - Update `revision_metadata.last_modified_by` to your agent identifier
   - Update `revision_metadata.last_modified_at` to current ISO-8601 timestamp
   - Append all patches to the Patch Log table
   - Modify the body sections (Items, Fields, Diagram Expectations, Source Requirements) according to the patches

2. Return the full updated outline content as part of the review output (see Step 5). Do not write it to GitHub. The review is advisory — the Orchestrator decides whether to accept, partially accept, or reject the patches.

### Step 5: Produce Review Output

Assemble the final output as a structured report.

## Output Format

Return the review as a structured markdown document with this exact format:

```markdown
# Research Review: {topic_slug} (Round {new_round})

## Verdict

**{verdict}** — {one-sentence summary of the review outcome}

## Patch Summary

| # | Action | Target | Reason | Impact |
|---|--------|--------|--------|--------|
| 1 | {action} | {target} | {why this change is needed} | {what improves} |
| 2 | ... | ... | ... | ... |

## Detailed Findings

### Finding 1: {title}

**Lens**: {which evaluation lens surfaced this}
**Severity**: critical | major | minor
**Description**: {what's wrong and why it matters}
**Patch**: {the concrete action taken, or "no patch — informational only" for findings that don't warrant a structural change}

### Finding 2: ...

## Remaining Gaps

{Bulleted list of issues that this review did NOT address — either because they're out of scope, require Orchestrator decision, or need information this review can't access. Empty section if no gaps remain.}

## Artifact Metadata

- **Project slug**: {project_slug}
- **Topic slug**: {topic_slug}
- **GitHub repo**: {github_repo}
- **Outline path**: {artifact_paths.outline}
- **Draft path**: {artifact_paths.draft}
- **Final path**: {artifact_paths.final}
- **Index path**: {artifact_paths.index}
- **Round**: {new_round}
- **Status**: candidate (acceptance is Orchestrator's decision)
- **Persistence**: not persisted — updated outline is a proposal only; Orchestrator decides whether to write
- **Patches applied**: {count}
- **Findings**: {critical_count} critical, {major_count} major, {minor_count} minor
```

Additionally, return the **full updated outline content** after the review report, so the Orchestrator can inspect both the review rationale and the resulting outline.

## Verdict Rules

- **revise**: any critical finding, OR total patches > 0, OR major structural issues remain
- **pass**: no critical findings, no patches needed, outline is ready for Orchestrator approval
- The verdict indicates the reviewer's assessment only. The Orchestrator decides whether to accept.

## Quality Checklist

Before returning the patched outline proposal, verify:

- [ ] All required frontmatter fields still present (nothing dropped during patching)
- [ ] `project_slug`, `topic_slug`, `github_repo`, `artifact_paths.*` unchanged from input
- [ ] `round` incremented by exactly 1
- [ ] `revision_metadata` updated with reviewer identity and timestamp
- [ ] All new Patch Log entries have round, action, target, reason, source
- [ ] Item IDs are unique and no renumbering occurred
- [ ] All `applies_to` references point to valid item IDs or `all`
- [ ] New items inherit all `applies_to: all` fields
- [ ] New fields applied to appropriate items
- [ ] No duplicate fields, equivalent items, equivalent diagrams, equivalent source requirements, or duplicate Patch Log entries were introduced
- [ ] Patch count in output matches actual patches in Patch Log

## Error Handling

- `gh` not available or not authenticated: this skill only needs `gh` to fetch the outline (Step 1). If the outline is provided via `outline_content`, `gh` is not required. If `outline_path` is provided but `gh` is unavailable, report BLOCKED and request the invoking agent to provide the outline content inline instead.
- Outline parse failure (malformed frontmatter or missing sections): report the structural issues as critical findings. Attempt to review what you can, but flag that the outline needs reformatting before patches can be reliably applied.
- `project_slug` or `topic_slug` missing from outline: this is a critical finding. The outline must carry these — they are orchestration context that cannot be inferred.
- Empty outline (no items): create a full review noting that the outline needs items before meaningful review is possible. Suggest items if the topic is clear enough.
