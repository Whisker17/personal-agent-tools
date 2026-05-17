---
name: research-deep-output
description: >
  Produce a complete, structured research section draft from an approved outline. For each outline
  item, conducts deep investigation across all applicable fields, gathers sources with attribution,
  generates diagrams (Mermaid/ASCII), and assembles the findings into a reviewable draft document.
  Persists drafts to GitHub before adversarial review. Supports multi-round revision when adversarial
  feedback is provided. After quality gate approval, promotes the accepted draft to final.md and
  posts Final Promotion Ready with an Index Entry Proposal. Use this skill whenever you need to
  execute deep research from an outline, produce a research section draft, write investigation
  findings, turn an outline into a full research document, or do the actual research work for a
  structured topic. Trigger on: 'start deep research', 'produce the draft', 'research this topic
  deeply', 'write the research section', 'execute the outline', 'do the deep research', or any
  request to turn an approved outline into a complete research section.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# /research-deep-output

Produce a complete structured research section draft from an approved outline. This is the Research Agent's primary tool during Phase B — it takes a consensus outline, investigates each item across every applicable field, gathers sources, generates diagrams, and assembles the findings into a draft that can be adversarially reviewed.

The outline conforms to the shared schema at `knowledge/shared/research-outline-schema.md` — read it before starting.

## Input

The invoking agent (typically Orchestrator via dispatch) provides these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `outline_path` | yes (or `outline_content`) | GitHub path to the approved outline |
| `outline_content` | yes (or `outline_path`) | Inline outline content |
| `topic` | yes | The research question or subject |
| `project_slug` | yes | Stable project identifier |
| `topic_slug` | yes | Stable topic identifier (never a Linear issue ID) |
| `github_repo` | no | GitHub repo for persistence. Default: `Whisker17/multica-research` |
| `round` | yes | Draft round number (starts at 1, increments on revision) |
| `artifact_paths` | yes | Object with `outline`, `draft`, `final`, `index` paths |
| `codebase_path` | no | Local repo path for codebase analysis |
| `adversarial_feedback` | no | Structured feedback from a previous round's review. When present, this is a revision pass |
| `multica_issue_id` | no | Multica research issue ID (for Index Entry Proposal) |
| `order` | no | Section order number assigned by Planner (for Index Entry Proposal) |
| `dependencies` | no | Upstream topic_slug list (for Index Entry Proposal) |
| `promote` | no | Set to `true` to trigger final promotion mode instead of research |
| `approved_draft_path` | promotion | Path to the approved draft (e.g., `{project_slug}/research-sections/{topic_slug}/drafts/round-{n}.md`). Required when `promote: true` |
| `approved_draft_round` | promotion | Round number of the approved draft. Required when `promote: true` |
| `approved_draft_commit` | promotion | Commit URL/SHA of the approved draft. Required when `promote: true` |
| `approval_evidence` | promotion | Link to the adversarial approval comment or Orchestrator's accept-risk comment. Required when `promote: true` |

## Modes

This skill operates in three modes:

- **Initial draft** (`adversarial_feedback` and `promote` both absent): full investigation from scratch.
- **Revision** (`adversarial_feedback` present, `promote` absent): targeted improvements based on review findings. The invocation must include the previous draft path or content in the feedback payload so unflagged content can be preserved.
- **Final promotion** (`promote: true`): promotes an approved draft to `final.md` and produces the Final Promotion Ready output. No new research — just file promotion and metadata assembly.

## Process

### Step 1: Load and Validate the Outline

1. If `outline_path` is provided, fetch from GitHub:

```bash
REPO="${github_repo:-Whisker17/multica-research}"
REPO_DIR=$(mktemp -d)
gh repo clone "$REPO" "$REPO_DIR"
cd "$REPO_DIR"
cat "${outline_path}"
```

2. If `outline_content` is provided, use it directly.

3. Parse the outline. Verify:
   - Status is `approved` (Orchestrator should only dispatch deep-output after approval).
   - `project_slug`, `topic_slug`, `github_repo`, `artifact_paths.*` are all present and consistent.
   - Items, Fields, Diagram Expectations, and Source Requirements sections are parseable.

4. If the outline status is still `candidate`, stop and report to the invoking agent. Deep research requires an approved outline.

5. Extract the research plan:
   - Which items to investigate (sorted by dependency order, then priority).
   - Which fields apply to each item.
   - Which diagrams to produce.
   - Source requirements to meet.

### Step 2: Deep Research Each Item

For each item (in dependency order, high priority first), investigate all applicable fields.

**Research approach per item:**

1. **Web research** — run 3-6 targeted searches per item, focusing on:
   - Recent and authoritative sources
   - Multiple perspectives when the topic is debated
   - Concrete data, metrics, and examples rather than general overviews
   - Primary sources over secondary summaries

2. **Codebase analysis** (if `codebase_path` provided) — for items that involve implementation or architecture:
   - Read relevant source files
   - Trace key code paths
   - Identify design patterns, dependencies, and integration points
   - Document what the code reveals that public documentation might not

3. **For each applicable field**, produce a finding that includes:
   - **Content**: the substantive finding (2-8 sentences depending on complexity)
   - **Sources**: specific URLs, papers, or code paths that support the finding
   - **Confidence**: `high` (multiple corroborating sources), `medium` (single authoritative source or reasonable inference), `low` (limited evidence, extrapolation, or conflicting sources)

4. **Source discipline** — every factual claim must have a source. If you cannot find a source for something, say so explicitly and mark confidence as `low`. Never fabricate URLs, paper titles, or data points.

**Revision mode**: when `adversarial_feedback` is present, focus investigation effort on items and fields that were flagged. Load the previous draft from the path or content in the feedback payload and carry forward unflagged findings unchanged (but verify any sources if the feedback questions sourcing quality). If the previous draft is not available, report BLOCKED instead of reconstructing it from memory.

### Step 3: Generate Diagrams

For each diagram expectation in the outline:

1. Determine which items' findings inform the diagram.
2. Generate the diagram in the specified format (`mermaid` or `ascii`).
3. Ensure the diagram is accurate to the findings — diagrams that contradict the text undermine trust.
4. Keep diagrams focused. A diagram that tries to show everything shows nothing.

Mermaid diagrams should be syntactically valid and render correctly. Test complex diagrams mentally before committing them.

### Step 4: Gap Analysis

After completing all item investigations, assess:

1. **Source coverage**: did the research meet the outline's source requirements? For each source requirement, count how many sources of that type were actually found.
2. **Field coverage**: were there fields where findings were thin across multiple items? These are research gaps.
3. **Cross-item patterns**: are there themes or findings that span multiple items and deserve explicit callout?
4. **Open questions**: what couldn't be answered with available information? Be specific about what's missing and why.

### Step 5: Assemble the Draft Document

Produce the draft as a markdown document with this structure:

```markdown
---
topic: {topic}
project_slug: {project_slug}
topic_slug: {topic_slug}
github_repo: {github_repo}
round: {round}
status: draft
artifact_paths:
  outline: {artifact_paths.outline}
  draft: {artifact_paths.draft}  # with round number resolved
  final: {artifact_paths.final}
  index: {artifact_paths.index}
draft_metadata:
  created_by: {agent identifier}
  created_at: {ISO-8601}
  based_on_outline_round: {outline round number}
  mode: {initial | revision}
---

# Research Section Draft: {topic}

> Round {round} | Status: draft | Based on outline round {N}

## Executive Summary

{3-5 sentences summarizing the key findings across all items. Written last, after all items are investigated.}

## Item Findings

### item-1: {Item Title}

#### {field_name_1}

{Finding content — 2-8 sentences}

**Sources**:
- [{source title}]({url}) — {brief relevance note}
- ...

**Confidence**: {high | medium | low}

#### {field_name_2}
...

{Repeat for all applicable fields}

### item-2: {Item Title}
...

{Repeat for all items}

## Diagrams

### diag-1: {Description}

{Mermaid codeblock or ASCII diagram}

### diag-2: ...

## Source Coverage

| Requirement | Type | Min Required | Actual | Met? |
|-------------|------|-------------|--------|------|
| src-1 | {type} | {N} | {actual count} | yes/no |
| ... |

## Gap Analysis

### Coverage Gaps
- {gap 1: what's missing and why it matters}
- {gap 2: ...}

### Cross-Item Patterns
- {pattern 1: theme that spans multiple items}
- ...

### Open Questions
- {question 1: what couldn't be answered}
- ...

## Revision Log

| Round | Changes | Trigger |
|-------|---------|---------|
| {round} | {summary of what was investigated/changed} | {initial draft / adversarial feedback from round N} |
```

### Step 6: Persist to GitHub

The draft must be persisted before adversarial review — this is a protocol invariant. Use the resolved `artifact_paths.draft` for the current round as the write path; do not recompute a different path at write time. Replace the `{assembled draft content}` placeholder with the actual draft before running the command.

```bash
REPO="<github_repo or Whisker17/multica-research>"
DRAFT_PATH="<resolved artifact_paths.draft for this round>"
TOPIC_SLUG="<topic_slug>"
ROUND="<round>"

REPO_DIR=$(mktemp -d)
gh repo clone "$REPO" "$REPO_DIR"
cd "$REPO_DIR"

mkdir -p "$(dirname "$DRAFT_PATH")"

cat > "$DRAFT_PATH" << 'DRAFT_EOF'
{assembled draft content}
DRAFT_EOF

git add .
git commit -m "research-deep-output: ${TOPIC_SLUG} draft round ${ROUND}"
git push
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_URL=$(gh api repos/${REPO}/commits/${COMMIT_SHA} --jq '.html_url')

cd -
rm -rf "$REPO_DIR"
```

### Step 7: Report Artifact Ready

Return to the invoking agent with all information needed for the Artifact Ready: deep-draft message:

```
Draft produced: {topic}
Path: {draft_path}
Commit URL: {commit_url}
Commit SHA: {commit_sha}
Round: {round}
Mode: {initial | revision}
Items covered: {count}
Fields investigated: {count}
Diagrams produced: {count}
Source requirements met: {met_count}/{total_count}
Gaps identified: {count}
Status: draft (awaiting adversarial review)
```

The invoking agent uses this to post the **Artifact Ready: deep-draft** message per the squad communication protocol.

### Step 8: Final Promotion (promote mode)

This step executes only when `promote: true` is set. The Orchestrator dispatches this after adversarial approval or accept-risk. No new research is performed — this is a file promotion and metadata assembly step.

**Required promotion inputs** (all must be provided):
- `approved_draft_path` — which draft was approved
- `approved_draft_round` — which round number
- `approved_draft_commit` — commit URL/SHA of the approved draft
- `approval_evidence` — link to adversarial approval or Orchestrator accept-risk comment
- `multica_issue_id` — for the Index Entry Proposal
- `order` — section order number from Planner
- `dependencies` — upstream topic_slug list

If any required promotion input is missing, report BLOCKED with the missing fields listed.

**Promotion process:**

1. Fetch the approved draft from GitHub at `approved_draft_path` and verify its commit matches `approved_draft_commit`.

2. Write `final.md` using `artifact_paths.final`; do not recompute a different final path. Replace the `{draft content with status changed to: final}` placeholder with the approved draft content before running the command:

```bash
REPO="<github_repo or Whisker17/multica-research>"
FINAL_PATH="<artifact_paths.final>"
TOPIC_SLUG="<topic_slug>"
APPROVED_DRAFT_ROUND="<approved_draft_round>"

REPO_DIR=$(mktemp -d)
gh repo clone "$REPO" "$REPO_DIR"
cd "$REPO_DIR"

mkdir -p "$(dirname "$FINAL_PATH")"

# Copy approved draft content, update status in frontmatter from "draft" to "final"
cat > "$FINAL_PATH" << 'FINAL_EOF'
{draft content with status changed to: final}
FINAL_EOF

git add .
git commit -m "research-deep-output: ${TOPIC_SLUG} final promotion (from round ${APPROVED_DRAFT_ROUND})"
git push
FINAL_COMMIT_SHA=$(git rev-parse HEAD)
FINAL_COMMIT_URL=$(gh api repos/${REPO}/commits/${FINAL_COMMIT_SHA} --jq '.html_url')

cd -
rm -rf "$REPO_DIR"
```

3. Return all information needed for the **Final Promotion Ready** message:

```
Final promotion complete: {topic}
Final path: {final_path}
Final commit URL: {final_commit_url}
Final commit SHA: {final_commit_sha}
Reviewed draft: {approved_draft_path}
Reviewed draft commit: {approved_draft_commit}
Adversarial approval / accept-risk: {approval_evidence}

Index Entry Proposal:
| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| {order} | {topic_slug} | {multica_issue_id} | {final_path} | {dependencies or -} | done |
```

The invoking agent uses this to post the **Final Promotion Ready** comment on the research issue. The Orchestrator then validates the proposal and serializes the `_index.md` commit. This skill does NOT write `_index.md`.

**After Final Promotion Ready**: this skill's work is done for the research phase. The Research Complete notification to TW happens only after the Orchestrator commits `_index.md` and provides the commit URL/SHA back to the Research Agent. See "Research Complete Boundary" below.

## Research Complete Boundary

This skill covers up to and including the **Final Promotion Ready** message. It does NOT post the **Research Complete** notification to the TW reserved issue.

The sequence after this skill finishes final promotion:

1. Research Agent posts **Final Promotion Ready** on the research issue (using this skill's output).
2. Orchestrator validates the Index Entry Proposal and serializes a commit to `_index.md`.
3. Orchestrator provides the `_index.md` commit URL/SHA back to the Research Agent.
4. **Only then** does the Research Agent post **Research Complete** on the TW reserved issue, including the `_index.md` commit URL/SHA.

If the Research Agent posts Research Complete before receiving the `_index.md` commit, TW would lack the index reference it needs. This boundary is enforced by the protocol, not by this skill — but the skill's output deliberately omits `_index.md` commit info to make premature TW notification impossible.

## Research Quality Standards

### Source Attribution

- Every factual claim needs at least one source.
- URLs must be real and visited during research. Never generate plausible-looking URLs.
- When citing code, reference the file path and relevant line ranges.
- Prefer primary sources (official docs, code, on-chain data) over secondary commentary.
- When sources conflict, present both views and note the conflict.

### Confidence Calibration

| Level | Meaning | When to use |
|-------|---------|-------------|
| `high` | Multiple independent, authoritative sources agree | Well-documented facts, established patterns |
| `medium` | Single authoritative source, or reasonable inference from strong evidence | Recent developments, informed analysis |
| `low` | Limited evidence, extrapolation, or sources conflict | Emerging topics, speculation-adjacent findings |

Mark confidence honestly. A draft full of `high` confidence claims is suspicious — real research encounters uncertainty.

### Diagram Quality

- Diagrams must be accurate to the findings. Never include components or flows not supported by research.
- Mermaid syntax must be valid. Common pitfalls: unquoted labels with special characters, missing direction declarations, circular references in flowcharts.
- Keep diagrams focused on one concept each. Split complex systems into multiple diagrams rather than one overloaded diagram.

## Quality Checklist

Before persisting, verify:

- [ ] All frontmatter fields present (`topic`, `project_slug`, `topic_slug`, `github_repo`, `round`, `status`, `artifact_paths`, `draft_metadata`)
- [ ] `project_slug`, `topic_slug`, `github_repo`, `artifact_paths.*` match the input outline exactly
- [ ] Every item from the outline has a corresponding section in Item Findings
- [ ] Every applicable field for each item has a finding with sources and confidence
- [ ] No fabricated sources — every URL was actually visited
- [ ] Diagrams match their expectations from the outline (type, format, scope)
- [ ] Source Coverage table accounts for all source requirements
- [ ] Gap Analysis is honest — doesn't hide shortcomings
- [ ] Revision Log records what was done and why
- [ ] In revision mode: adversarial feedback items are addressed; unflagged content preserved

## Error Handling

- `gh` not available or not authenticated: **BLOCKED**. The draft must be persisted to GitHub before adversarial review — this is a protocol invariant. Do not return the draft inline as a fallback. Report BLOCKED to the invoking agent with the reason, and request that `gh` be configured before retrying.
- Outline not approved: **BLOCKED**. Deep research requires an approved outline. Report the error — the Orchestrator may have dispatched prematurely.
- `project_slug` or `topic_slug` missing: **BLOCKED**. These are required orchestration context. Report the error — do not invent values.
- GitHub push fails (repo access, network): retry once. If it still fails, **BLOCKED**. Report the error with the assembled draft path so the invoking agent can troubleshoot and retry.
- Source requirements not met: proceed with the draft but flag unmet requirements prominently in the Gap Analysis. The adversarial reviewer will assess whether the gaps are acceptable.
- Web search failures: note which searches failed and what information is missing. Partial research is better than no research — persist what you have and document the gaps.
