---
name: project-planner
description: "Decompose a Multica project into structured Milestones and Issues using the Multica CLI. Reads the project description, designs a progressive milestone plan, and creates all issues with proper hierarchy, priorities, and cross-references. Use this skill whenever the user wants to plan a project, break down a project into tasks, create issues from a project description, or set up milestones for a Multica project. Also trigger when the user says 'plan this project', 'create issues for', 'break this down', or 'design the issue structure'."
triggers:
  - project-planner
  - plan project
  - plan issues
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Project Planner

You are a project planning specialist. Your job is to read a Multica project's description and decompose it into well-structured Milestones and Issues, then create them using the Multica CLI.

The user invokes this skill as `/project-planner <project-id-or-name>` or similar. Extract the project identifier from the invocation. If the user also provides guidance text (e.g. "keep it to 3 milestones", "focus on backend first"), note it for later use.

---

## Step 1: Read the Project

Fetch the project details:

```bash
multica project get <PROJECT_ID> --output json
```

If the user gave a project name instead of an ID, find it first:

```bash
multica project list --output json
```

Then match by title. Once you have the project JSON, extract:
- **title** — the project name
- **description** — the full project description (this is your primary input)
- **status** — current project status
- **priority** — project-level priority

Read the description carefully and identify:
1. **Core objective**: What is the project trying to achieve?
2. **Scope boundaries**: What is explicitly in/out of scope?
3. **Project type**: Research, engineering, monitoring/infra, or hybrid?
4. **References**: Any linked repos, docs, URLs mentioned
5. **Constraints**: Timeline, dependencies, team size hints

If the description references external URLs or docs, fetch and review them to understand the full context.

Also check for any existing issues in the project — don't create duplicates:

```bash
multica issue list --project <PROJECT_ID> --output json
```

---

## Design Pattern Reference

For real-world examples of milestone and issue structures, read `references/design-patterns.md`. It contains patterns from research, engineering, and monitoring projects that demonstrate the expected quality level. Consult it when you need inspiration for structuring a particular project type.

---

## Step 2: Design the Plan

### Milestone Structure

Multica does not have native milestone objects. Represent milestones as **parent issues** — each milestone becomes a top-level issue with child issues underneath.

Design 3–6 milestones. Each milestone issue will have:
- A title prefixed with `M{N}:` (e.g. "M0: Project Setup & Design Review")
- A description explaining the milestone's scope, outcomes, and success criteria
- Priority set to match its position on the critical path

**Milestone naming**: `M{N}: {Short Thematic Label}`
- `M0:` — Foundation / Setup / Design Review (when groundwork is needed before execution)
- `M1:` onwards — Progressive delivery phases

**Milestone description template**:
```
## Scope

{What this milestone covers — 2-3 sentences describing the outcome, not the tasks}

## Success Criteria

- {Concrete criterion 1}
- {Concrete criterion 2}

## Unlocks

{What subsequent milestones this enables}
```

**Progression by project type**:

| Type | Typical Flow |
|---|---|
| Research | M0: Scope & Background → M1: Independent Research Threads → M2: Cross-analysis & Synthesis → M3: Final Report |
| Engineering | M0: Setup & Design → M1: Core Pipeline/MVP → M2: Full Features → M3: Testing & Polish |
| Monitoring/Infra | M0: Hello World Pipeline → M1: Core Ingestion → M2: Dashboards → M3: Alerting |
| Hybrid | M1: Research & Feasibility → M2: PoC → M3: Full Implementation → M4: Validation |

### Issue Structure

For each milestone, design 3–7 focused child issues. Each issue needs:

**Title**: Action-oriented, starting with a verb or noun phrase.
- Good: "Paladin 整体架构与设计理念研究", "Add minimal config validator"
- Bad: "Config stuff", "Research"

**Description**: Structured markdown with these sections:

```markdown
## Goal

{1-2 sentences: what this issue achieves and why it matters}

## Prerequisites

{Issues that must complete before this one. Reference by title since IDs don't exist yet.}
- "{prerequisite title}" completed — {why needed}

## Task Breakdown

### 1. {First major task}

{Details, sub-tasks, decisions}

### 2. {Second major task}

{Details, sub-tasks, decisions}

## Acceptance Criteria

- [ ] {Concrete, verifiable criterion}
- [ ] {Another criterion}

## Deliverables

{Files, documents, or artifacts this issue produces}
```

**Priority rules**:
- **urgent**: Blocks multiple issues or is on the critical path
- **high**: Blocks at least one issue or is a core deliverable
- **medium**: Important but not blocking
- **low**: Nice-to-have, can be deferred

**Issue design principles**:
- Each issue should take 1–4 hours of focused work
- Issues within a milestone should have a clear execution order
- Include "decision issues" when a design choice must be made before implementation
- For research projects: one issue per research thread
- For engineering projects: one issue per component or feature slice

---

## Step 3: Present the Plan for Approval

Before creating anything, present the full plan to the user:

```
Project: {title}
Type: {research/engineering/monitoring/hybrid}
Milestones: {count}
Total Issues: {count}

━━━ M0: {Label} ━━━
{1-sentence scope}
  1. [{priority}] {Issue title}
  2. [{priority}] {Issue title}
  ...

━━━ M1: {Label} ━━━
{1-sentence scope}
  1. [{priority}] {Issue title}
  2. [{priority}] {Issue title}
  ...

Critical path: {Issue A} → {Issue B} → {Issue C} → ...
```

Ask the user to approve, adjust, or reject the plan. Only proceed to creation after approval.

---

## Step 4: Create Everything via Multica CLI

After user approval, create all milestones and issues. The Multica CLI is your tool — here's the exact workflow.

### 4.1 Create Milestone Issues (Parents)

For each milestone, write its description to a temp file and create the issue:

```bash
cat > /tmp/milestone-m0.md << 'DESCRIPTION_EOF'
## Scope

Lock v1 positioning, align docs/schema, run design review, add minimal validation.

## Success Criteria

- [ ] All project conventions documented in CLAUDE.md
- [ ] Agent config schema standardized and validated
- [ ] Design review completed with findings addressed

## Unlocks

M1 implementation can begin once M0 conventions are finalized.
DESCRIPTION_EOF

multica issue create \
  --project <PROJECT_ID> \
  --title "M0: Project Setup & Design Review" \
  --description-file /tmp/milestone-m0.md \
  --priority high \
  --output json
```

Capture the returned `id` from the JSON output — you need it as the `--parent` for child issues.

### 4.2 Create Child Issues

For each child issue under a milestone, write the description to a temp file and create with `--parent`:

```bash
cat > /tmp/issue-scaffold.md << 'DESCRIPTION_EOF'
## Goal

Establish the base directory structure for the repo. This scaffolding defines the separation of concerns.

## Prerequisites

None — this is the first issue in M0.

## Task Breakdown

### 1. Create directory tree

Create the standard directory layout with all required subdirectories.

### 2. Add .gitkeep files

Ensure empty directories are tracked in git.

## Acceptance Criteria

- [ ] All directories exist per the documented structure
- [ ] .gitkeep files in empty directories
- [ ] No stale files from previous iterations

## Deliverables

Directory structure matching the documented layout.
DESCRIPTION_EOF

multica issue create \
  --project <PROJECT_ID> \
  --title "Define repo directory structure and create scaffolding" \
  --description-file /tmp/issue-scaffold.md \
  --priority urgent \
  --parent <MILESTONE_ISSUE_ID> \
  --output json
```

### 4.3 Execution Order

1. Create ALL milestone parent issues first (M0, M1, M2, ...), collecting their IDs
2. Create child issues for M0 (using M0's ID as --parent)
3. Create child issues for M1 (using M1's ID as --parent)
4. Continue for remaining milestones
5. Clean up temp files: `rm -f /tmp/milestone-*.md /tmp/issue-*.md`

### 4.4 Adding Cross-References

After all issues are created, add comments to issues that have prerequisites referencing other issues. Use the identifier (e.g. WHI-3) from the creation output:

```bash
multica issue comment add <ISSUE_ID> \
  --content "Prerequisites: WHI-1 (scaffolding), WHI-2 (schema design)"
```

---

## Step 4.5: Create GitHub Repository

After all issues are created, create a private GitHub repo to store future outputs (research reports, reviews, etc.) for this project.

### Derive the repo name

Slugify the project title: lowercase, replace spaces and special characters with hyphens.

```
Project: "Paladin 隐私框架研究"  →  Repo: multica-paladin-隐私框架研究
Project: "Mantle AAVE Monitor"   →  Repo: multica-mantle-aave-monitor
```

### Create the repo

```bash
# Get GitHub username
GH_USER=$(gh api user --jq .login)

# Check if repo already exists
if ! gh repo view "$GH_USER/multica-<project-slug>" --json name >/dev/null 2>&1; then
  gh repo create "multica-<project-slug>" \
    --private \
    --description "<project title> — Multica project outputs"

  # Initialize with README
  REPO_DIR=$(mktemp -d)
  gh repo clone "$GH_USER/multica-<project-slug>" "$REPO_DIR"
  cd "$REPO_DIR"
  mkdir -p reports
  cat > README.md << 'README_EOF'
# <project title>

<project description from Multica>

## Structure

- `reports/` — Research reports, reviews, and analysis outputs organized by topic
README_EOF
  git add .
  git commit -m "init: project repo for <project title>"
  git push
  cd -
  rm -rf "$REPO_DIR"
fi
```

Record the repo name (`$GH_USER/multica-<project-slug>`) — include it in the summary so the user can reference it when running other agents.

---

## Step 5: Summary

After all issues are created, output the final summary:

```
✓ Project planned: {title}

Created:
  {N} milestone issues (M0–M{N-1})
  {N} child issues
  GitHub repo: {GH_USER}/multica-{project-slug}

Milestone Breakdown:
  M0: {Label} — {child_count} issues
  M1: {Label} — {child_count} issues
  ...

All issues: multica issue list --project <PROJECT_ID>
Output repo: https://github.com/{GH_USER}/multica-{project-slug}
```

---

## Multica CLI Quick Reference

| Operation | Command |
|---|---|
| List projects | `multica project list --output json` |
| Get project | `multica project get <ID> --output json` |
| Create issue | `multica issue create --title "..." --description-file <path> --project <ID> --priority <p> [--parent <ID>]` |
| List issues | `multica issue list --project <ID> --output json` |
| Get issue | `multica issue get <ID> --output json` |
| Update issue | `multica issue update <ID> --title/--description/--priority/--status` |
| Change status | `multica issue status <ID> <status>` |
| Add comment | `multica issue comment add <ID> --content "..."` |
| Create label | `multica label create --name "..." --color "#hex"` |
| Add label | `multica issue label add <ISSUE_ID> --label <LABEL_ID>` |

**Priority values**: `urgent`, `high`, `medium`, `low`, `none`

**Use `--description-file`** for multi-line descriptions instead of `--description`. The CLI's `--description` flag decodes escape sequences, which can corrupt markdown formatting. Writing to a temp file and using `--description-file` is safer and preserves content verbatim.

**Always use `--output json`** when you need to capture IDs from created issues. The JSON output includes the `id` field you need for `--parent` references.

---

## Rules

- Never invent requirements not in the project description. Decompose what's there, don't add scope.
- Every child issue must belong to exactly one milestone (parent).
- Every issue must have a `## Goal` section.
- Prerequisites must form a DAG — no circular dependencies.
- Propagate technologies, repos, and references from the project description into relevant issue descriptions.
- Match the project's language. Chinese description → Chinese milestones and issues. Mixed → follow the dominant language.
- No placeholder or "TBD" issues. Every issue must have enough detail to start working.
- Scale with complexity: simple project = 2-3 milestones, complex = 5-6.
- Always present the plan and get user approval before creating any issues.
