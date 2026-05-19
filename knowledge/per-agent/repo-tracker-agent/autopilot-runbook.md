# Goal

Run `repo-tracker-agent` as a Multica autopilot that periodically tracks configured GitHub repos and produces competitive development intelligence focused on PR activity.

# Context

This autopilot is for tracking competitors or important upstream projects. The main signal is PR activity, split by status:

- draft
- open
- merged
- closed without merge

Weekly and monthly reports should not be generic activity summaries. They should explain the important PRs in the period and extend that evidence into engineering trend analysis.

Persistence uses a GitHub data repo. Daily reports are Markdown summaries. Weekly and monthly reports depend on those daily Markdown summaries, then add higher-level synthesis.

## Issue Ownership

All issues created by the autopilot must be attached to the **"竞争对手 Repo 跟踪"** project.

## Tracked Repo Source

Do not hardcode `Track repos` in the autopilot description. The agent reads the repo list from the **"竞争对手 Repo 跟踪"** project **Resources** at runtime by extracting `owner/repo` from each GitHub URL.

Benefits:

- Adding or removing tracked repos only requires editing the project Resources — no autopilot reconfiguration needed
- All autopilot instances (daily/weekly/monthly) share the same repo list

# Steps

1. Use `Whisker17/counterparty-daily-summary` as the tracker data repo.
2. Ensure the Multica runtime can run `gh api` and has read access to tracked repos.
3. The agent reads the repo list from the "竞争对手 Repo 跟踪" project Resources before fetching data.
4. Configure a daily autopilot with `Report type: daily`.
5. Configure a weekly autopilot with `Report type: weekly`.
6. Configure a monthly autopilot with `Report type: monthly`.
7. Use the description format:

```text
Report type: daily
Focus: security,bridge
Language: zh
Data repo: Whisker17/counterparty-daily-summary
Timezone: Asia/Shanghai
Project: 竞争对手 Repo 跟踪
```

Note: `Track repos` is not in the description — the agent reads it from the project Resources at runtime. The `Project` field tells the agent which project to read Resources from and which project to attach the created issue to. `Track repos` can still be provided explicitly to override the project Resources if needed.

8. For each run, verify the issue:
   - Is attached to the "竞争对手 Repo 跟踪" project
   - Includes PR status breakdown
   - Includes Key PRs
   - For each Key PR, includes a content-based understanding using PR body, changed files, modules, and commit subjects
   - Includes Data Notes
   - Includes metadata comment
9. For weekly and monthly runs, verify the report explains engineering direction from Key PRs, not only commit counts.
10. Verify the Markdown report is persisted to:
    - daily: `YYYY/MM/DD-DD/DD/owner/repo/YYYYMMDD-summary.md`
    - weekly: `YYYY/MM/DD-DD/weeks-summarys/owner/repo/YYYYMM-week-summary.md`
    - monthly: `YYYY/MM/months-summarys/owner/repo/YYYYMM-month-summary.md`
11. If a weekly/monthly report lacks Key PR Themes or Engineering Direction, rerun after checking that daily summaries exist and daily snapshots contain `key_prs`, `pr_status`, and `content_signals`.

# Managing Tracked Repos

To add or remove tracked repos, edit the "竞争对手 Repo 跟踪" project Resources in Multica:

- Add a resource with the GitHub repo URL (e.g. `https://github.com/base/base`)
- The agent extracts `owner/repo` from the URL at runtime
- Changes take effect on the next autopilot run — no autopilot reconfiguration needed
