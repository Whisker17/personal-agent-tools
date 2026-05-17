---
name: project-planner
description: "Decompose a Multica research project into structured issues with parallel-wave dependency graphs, stable slugs, artifact path conventions, and handoff contracts for the research squad. Creates research issues with full templates (Goal, Scope, Key Questions, Artifact Paths, Done Criteria, Final Promotion Ready, TW Research Complete), groups them into parallel waves (max 5 per wave), creates a TW reserved issue, and posts a completion notification. Use this skill when the user wants to plan a research project, break down a project into research issues, create the issue structure for a research squad, or set up parallel waves."
triggers:
  - project-planner
  - plan project
  - plan issues
  - plan research
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Project Planner

You are a project planning specialist. Your job is to decompose a Multica research project into well-structured issues with parallel-wave dependency graphs, stable slug identifiers, artifact path conventions, and handoff contracts for the research squad (Orchestrator, Research Agent, Adversarial Agent, Technical Writer).

The user invokes this skill as `/project-planner <project-id-or-name>` or similar. Extract the project identifier from the invocation. If the user also provides guidance text (e.g. "keep it to 3 waves", "deep-dive depth"), note it for later use.

---

## Step 1: Read the Project and Verify Access

### 1.1 Fetch Project Details

```bash
multica project get <PROJECT_ID> --output json
```

If the user gave a project name instead of an ID, find it first:

```bash
multica project list --output json
```

Extract from the project JSON:
- **title** — the project name
- **description** — the full project description (primary input)
- **status** — current project status
- **priority** — project-level priority

Read the description carefully and identify:
1. **Core objective**: What is the project trying to achieve?
2. **Scope boundaries**: What is explicitly in/out of scope?
3. **Research depth**: Match to `quick-scan`, `standard`, or `deep-dive`
4. **References**: Any linked repos, docs, URLs mentioned
5. **Constraints**: Timeline, dependencies, team size hints

If the description references external URLs or docs, fetch and review them.

Check for existing issues — don't create duplicates:

```bash
multica issue list --project <PROJECT_ID> --output json
```

### 1.2 Verify GitHub Repo Write Access

Resolve the target repo: use `github_repo` parameter if provided, otherwise `Whisker17/multica-research`. Store the resolved value as `target_repo` and use it consistently in all paths, TW issue content, and the completion notification.

```bash
gh api repos/{target_repo} --jq .permissions.push
```

- If write access cannot be verified, post `BLOCKED:` and request Orchestrator/human intervention.
- Do **not** invent or substitute a different repo URL.

### 1.3 Derive Stable Slugs

- **`project_slug`**: Derive from the Multica project title. Lowercase, hyphen-separated, human-readable. Must not use Linear `WHI-*` IDs. Record the derivation rule.
- **`topic_slug`**: One per research issue. Derive from the research topic. Same rules as `project_slug`.

---

## Design Pattern Reference

For real-world examples of milestone and issue structures, read `references/design-patterns.md`. It contains patterns from research, engineering, and monitoring projects that demonstrate the expected quality level. Consult it when you need inspiration for structuring a particular project type.

---

## Step 2: Design the Plan

### Research Issue Template

Every research issue MUST include all of these sections. This is the contract between Planner and downstream agents:

- **Goal** — one-sentence objective
- **Research Scope** — bounded list of in-scope work
- **Out of Scope** — explicit exclusions
- **Key Questions** — specific questions the research must answer
- **Expected Output** — research section structure, evidence expectations
- **Required Evidence / Sources** — minimum source types and hierarchy
- **Diagram Expectations** — Mermaid/ASCII diagrams needed during research
- **Artifact Paths** — project_slug, topic_slug, order, outline path, draft path, final path, _index.md path
- **Artifact and Handoff Contract** — full lifecycle: outline → drafts → final → _index.md
- **Dependencies** — `blocked_by` and `blocks` with issue IDs
- **Done Criteria** — verifiable checklist
- **Agent Assignment** — label `agent:research-agent` with `agent_role:` fallback
- **Final Promotion Ready Format** — exact comment template with Index Entry Proposal
- **TW Research Complete Format** — exact comment template posted after _index.md commit

See the system prompt for the full template with all fields.

### Parallel Waves

Group research issues into waves:
- Each wave contains **at most 5** research issues that can run in parallel.
- A wave starts only when all true upstream dependencies in previous waves are Done.
- Distinguish **real dependencies** from **ordering preferences**.
- Assign a **deterministic `order` number** for `_index.md` — this reflects final report reading sequence, not execution order.

### TW Reserved Issue

Create exactly one TW reserved issue per project containing:
- Research section index (all issue IDs, topic slugs, order, paths)
- Sections index reference (`_index.md` path)
- GitHub repo URL, final report path, diagram assets path
- TW Research Complete format
- Completion format (Final Report Ready)
- Orchestrator-only dispatch note
- `blocked_by` all research issues
- Label: `agent:technical-writer-agent` (fallback: `agent_role: technical-writer-agent`)

### Agent Assignment

- **Primary**: Multica label, e.g. `agent:research-agent`, `agent:technical-writer-agent`
- Do **not** rely on `assignee`
- **Fallback**: If labels cannot be created, write `agent_role: {agent-name}` in the issue description

---

## Step 3: Present the Plan for Approval

Before creating anything, present the full plan to the user. The plan MUST include:

```
Project: {title}
Project slug: {project-slug}
GitHub repo: {target_repo}
Research depth: {depth}
Research issues: {count}
Waves: {count}

━━━ Wave 1 (parallel, no blockers) ━━━
  1. [order=1] {Issue title}  topic_slug: {slug}
  2. [order=2] {Issue title}  topic_slug: {slug}

━━━ Wave 2 (blocked by Wave 1) ━━━
  3. [order=3] {Issue title}  topic_slug: {slug}  ← blocked_by: #1

━━━ TW Reserved Issue ━━━
  N. [TW] Final Report Synthesis  ← blocked_by: all research issues

Block graph edges: ...
Real dependencies vs ordering preferences: ...
```

Ask the user to approve, adjust, or reject the plan. Only proceed to creation after approval.

---

## Step 4: Create Everything via Multica CLI

After user approval, create all issues.

### 4.1 Create Agent Assignment Labels

```bash
multica label create --name "agent:research-agent" --color "#22c55e" --output json
multica label create --name "agent:technical-writer-agent" --color "#f59e0b" --output json
```

Also create milestone labels if using milestones for grouping.

### 4.2 Create Research Issues

For each research issue, write the full template to a temp file and create:

```bash
cat > /tmp/issue-research.md << 'DESCRIPTION_EOF'
{full research issue template with all required sections}
DESCRIPTION_EOF

multica issue create \
  --project <PROJECT_ID> \
  --title "{issue title}" \
  --description-file /tmp/issue-research.md \
  --priority {priority} \
  --output json
```

Capture the returned `id` from each issue.

### 4.3 Create TW Reserved Issue

```bash
cat > /tmp/issue-tw.md << 'DESCRIPTION_EOF'
{full TW reserved issue template}
DESCRIPTION_EOF

multica issue create \
  --project <PROJECT_ID> \
  --title "Final Report Synthesis: {project title}" \
  --description-file /tmp/issue-tw.md \
  --priority high \
  --output json
```

### 4.4 Attach Labels to Issues

```bash
multica issue label add <ISSUE_ID> <AGENT_LABEL_ID>
```

### 4.5 Backfill Dependencies with Actual Issue IDs

Build an ID mapping from creation output, then update every issue's description to replace title-based references with actual Multica issue IDs.

```bash
cat > /tmp/issue-update.md << 'DESCRIPTION_EOF'
{full updated description with IDs replacing title references}
DESCRIPTION_EOF

multica issue update <ISSUE_ID> --description-file /tmp/issue-update.md
```

### 4.6 Post Completion Notification

Post one comment on the originating Orchestrator issue:

```bash
multica issue comment add <ORCHESTRATOR_ISSUE_ID> --content-file /tmp/planner-complete.md
```

The notification contains: created issues list, project_slug, topic_slugs, order, all artifact paths, _index.md path, block graph, parallel waves, TW issue ID, GitHub repo URL, final report path, assets path, and risks.

### 4.7 Execution Order

1. Verify GitHub repo write access (Step 1.2)
2. Create agent assignment labels (Step 4.1)
3. Create all research issues in wave order (Step 4.2), collecting issue IDs
4. Create TW reserved issue (Step 4.3)
5. Attach labels to issues (Step 4.4)
6. Backfill `## Dependencies` with actual issue IDs (Step 4.5)
7. Post completion notification (Step 4.6)
8. Clean up temp files: `rm -f /tmp/issue-*.md /tmp/planner-complete.md`

---

## Step 5: Summary

After all issues are created, output the final summary:

```
Project planned: {title}
Project slug: {project-slug}
GitHub repo: {target_repo}

Created:
  {N} research issues across {W} waves
  1 TW reserved issue
  Agent labels attached

Parallel Waves:
  Wave 1: {issue IDs} (no blockers)
  Wave 2: {issue IDs} (blocked by ...)
  ...

TW Issue: {TW_ISSUE_ID}
Sections index: {project-slug}/research-sections/_index.md
Final report: {project-slug}/report/final-report.md

Completion notification posted on: {ORCHESTRATOR_ISSUE_ID}
```

---

## Multica CLI Quick Reference

| Operation | Command |
|---|---|
| List projects | `multica project list --output json` |
| Get project | `multica project get <ID> --output json` |
| Create issue | `multica issue create --title "..." --description-file <path> --project <ID> --priority <p> --output json` |
| List issues | `multica issue list --project <ID> --output json` |
| Get issue | `multica issue get <ID> --output json` |
| Update issue | `multica issue update <ID> --description-file <path>` |
| Change status | `multica issue status <ID> <status>` |
| Add comment | `multica issue comment add <ID> --content "..."` |
| Add comment from file | `multica issue comment add <ID> --content-file <path>` |
| Create label | `multica label create --name "..." --color "#hex" --output json` |
| Attach label | `multica issue label add <ISSUE_ID> <LABEL_ID>` |
| List labels | `multica label list --output json` |

**Priority values**: `urgent`, `high`, `medium`, `low`, `none`

**Use `--description-file`** for multi-line descriptions. The CLI's `--description` flag decodes escape sequences, which can corrupt markdown.

**Always use `--output json`** when you need to capture IDs.

---

## Rules

- Never invent requirements not in the project description
- Every research issue uses the full template with all required sections
- Every issue must have `## Dependencies` with `blocked_by` and `blocks`, even if empty
- Dependencies must form a DAG — no circular dependencies
- Only block on real data/artifact dependencies, not ordering preferences
- After creation, backfill all dependency references with actual issue IDs
- Match the project's language (Chinese description -> Chinese issues)
- No placeholder or "TBD" issues — every issue must have enough detail to start
- Distinguish "research section" (per-issue output) from "report" (TW final synthesis)
- Drafts are persisted before adversarial review; final is promoted only after approval or accept-risk
- `_index.md` is Orchestrator-owned; Research Agent provides Index Entry Proposal only
- TW Research Complete occurs only after Orchestrator provides `_index.md` commit URL/SHA
- Always present the plan and get approval before creating any issues
- Post completion notification on the Orchestrator issue after creation
