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

# Steps

1. Use `Whisker17/counterparty-daily-summary` as the tracker data repo.
2. Ensure the Multica runtime can run `gh api` and has read access to tracked repos.
3. Configure a daily autopilot with `Report type: daily`.
4. Configure a weekly autopilot with `Report type: weekly`.
5. Configure a monthly autopilot with `Report type: monthly`.
6. Use the description format:

```text
Track repos: org1/repo1,org2/repo2
Report type: daily
Focus: security,bridge
Language: zh
Data repo: Whisker17/counterparty-daily-summary
Timezone: Asia/Shanghai
```

7. For each run, verify the issue includes:
   - PR status breakdown
   - Key PRs
   - for each Key PR, a content-based understanding using PR body, changed files, modules, and commit subjects
   - Data Notes
   - metadata comment
8. For weekly and monthly runs, verify the report explains engineering direction from Key PRs, not only commit counts.
9. Verify the Markdown report is persisted to:
   - daily: `YYYY/MM/DD-DD/DD/project/YYYYMMDD-summary.md`
   - weekly: `YYYY/MM/DD-DD/weeks-summarys/project/YYYYMM-week-summary.md`
   - monthly: `YYYY/MM/months-summarys/project/YYYYMM-month-summary.md`
10. If a weekly/monthly report lacks Key PR Themes or Engineering Direction, rerun after checking that daily summaries exist and daily snapshots contain `key_prs`, `pr_status`, and `content_signals`.
