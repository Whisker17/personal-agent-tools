#!/usr/bin/env python3
"""Aggregate repo tracker daily snapshots into weekly or monthly summaries."""

import argparse
import base64
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path


def pr_current_status(pr, event_type=None):
    if event_type == "merged":
        return "merged"
    if event_type == "closed_unmerged":
        return "closed_unmerged"
    if pr.get("draft"):
        return "draft"
    if pr.get("merged_at"):
        return "merged"
    if pr.get("state") == "closed":
        return "closed_unmerged"
    return "open"


def pr_sort_score(pr):
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    changed_files = int(pr.get("changed_files") or 0)
    status_weight = {
        "merged": 4000,
        "open": 2500,
        "draft": 1500,
        "closed_unmerged": 500,
    }.get(pr.get("current_status"), 0)
    label_weight = 1000 if pr.get("labels") else 0
    return status_weight + label_weight + additions + deletions + changed_files * 25


def key_pr_summary(pr, event_types):
    labels = pr.get("labels") or []
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    changed_files = int(pr.get("changed_files") or 0)
    return {
        "number": pr.get("number"),
        "title": pr.get("title"),
        "author": pr.get("user"),
        "current_status": pr.get("current_status"),
        "event_types": sorted(event_types),
        "labels": labels,
        "additions": pr.get("additions"),
        "deletions": pr.get("deletions"),
        "changed_files": pr.get("changed_files"),
        "review_time_hours": pr.get("review_time_hours"),
        "importance_score": pr_sort_score(pr),
        "evidence": f"{additions + deletions} LOC, {changed_files} files, labels: {', '.join(labels) if labels else 'none'}",
        "content_signals": build_content_signals(pr),
    }


def build_content_signals(pr):
    return pr.get("content_signals") or {
        "body_excerpt": pr.get("body") or "",
        "changed_files": pr.get("files") or [],
        "modules": [],
        "commit_subjects": [],
        "summary_basis": [],
    }


def build_pr_status_and_key_prs(opened, merged, closed_unmerged, updated_open=None):
    updated_open = updated_open or []
    by_number = {}
    for event_type, prs in (
        ("opened", opened),
        ("updated_open", updated_open),
        ("merged", merged),
        ("closed_unmerged", closed_unmerged),
    ):
        for pr in prs:
            pr.setdefault("current_status", pr_current_status(pr, event_type))
            pr.setdefault("content_signals", build_content_signals(pr))
            number = pr.get("number")
            if number is None:
                continue
            existing = by_number.setdefault(number, {"pr": pr, "event_types": set()})
            if pr_sort_score(pr) >= pr_sort_score(existing["pr"]):
                existing["pr"] = pr
            existing["event_types"].add(event_type)

    pr_status = {
        "draft": [],
        "open": [],
        "closed_unmerged": [],
        "merged": [],
    }
    for item in by_number.values():
        pr = item["pr"]
        status = pr.get("current_status") or pr_current_status(pr)
        pr_status.setdefault(status, []).append(pr)

    key_prs = [
        key_pr_summary(item["pr"], item["event_types"])
        for item in sorted(by_number.values(), key=lambda value: pr_sort_score(value["pr"]), reverse=True)[:10]
    ]
    return pr_status, key_prs


def run_gh(args):
    return subprocess.run(["gh", *args], text=True, capture_output=True)


def week_range_for(day):
    days_since_saturday = (day.weekday() - 5) % 7
    start = day - timedelta(days=days_since_saturday)
    end = start + timedelta(days=6)
    return start, end


def report_path(report_type, report_date, project):
    day = date.fromisoformat(report_date)
    week_start, week_end = week_range_for(day)
    year = f"{day.year:04d}"
    month = f"{day.month:02d}"
    week_dir = f"{week_start.day:02d}-{week_end.day:02d}"
    safe_project = project.strip().strip("/")
    if report_type == "daily":
        return f"{year}/{month}/{week_dir}/{day.day:02d}/{safe_project}/{year}{month}{day.day:02d}-summary.md"
    if report_type == "weekly":
        return f"{year}/{month}/{week_dir}/weeks-summarys/{safe_project}/{year}{month}-week-summary.md"
    if report_type == "monthly":
        return f"{year}/{month}/months-summarys/{safe_project}/{year}{month}-month-summary.md"
    raise ValueError(f"unknown report type: {report_type}")


def daterange(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def count_value(value):
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return int(value.get("count") or len(value))
    if isinstance(value, int):
        return value
    return 0


def load_snapshot_from_fixture(fixture_dir, day):
    path = Path(fixture_dir) / f"{day.isoformat()}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def load_snapshot_from_repo(data_repo, day):
    result = run_gh(
        [
            "api",
            f"repos/{data_repo}/contents/daily/{day.isoformat()}.json",
            "--jq",
            ".content",
        ]
    )
    if result.returncode != 0:
        return None
    content = "".join(result.stdout.split())
    return json.loads(base64.b64decode(content).decode("utf-8"))


def load_summary_from_fixture(summary_fixture_dir, day, project):
    if not summary_fixture_dir or not project:
        return None
    path = Path(summary_fixture_dir) / report_path("daily", day.isoformat(), project)
    if not path.is_file():
        return None
    return {"date": day.isoformat(), "path": str(path.relative_to(summary_fixture_dir)), "content": path.read_text()}


def load_summary_from_repo(data_repo, day, project):
    if not data_repo or not project:
        return None
    path = report_path("daily", day.isoformat(), project)
    result = run_gh(["api", f"repos/{data_repo}/contents/{path}", "--jq", ".content"])
    if result.returncode != 0:
        return None
    content = base64.b64decode("".join(result.stdout.split())).decode("utf-8")
    return {"date": day.isoformat(), "path": path, "content": content}


def fetch_gap_snapshot(args, day):
    if not args.repos:
        return None
    command = [
        "./agents/repo-tracker-agent/skills/repo-tracker/scripts/tracker-fetch.py",
        "--repos",
        args.repos,
        "--report-date",
        day.isoformat(),
        "--timezone",
        args.timezone,
    ]
    if args.gap_fill_fixture:
        command.extend(["--fixture", args.gap_fill_fixture])
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode not in (0, 1):
        print(result.stderr or result.stdout, file=sys.stderr)
        return None
    return json.loads(result.stdout)


def merge_counter(target, source):
    for key, value in (source or {}).items():
        target[key] += int(value or 0)


def aggregate_repo(target, repo_data):
    prs = repo_data.get("prs") or {}
    pr_status, key_prs = build_pr_status_and_key_prs(
        prs.get("opened") or [],
        prs.get("merged") or [],
        prs.get("closed_unmerged") or [],
        prs.get("updated_open") or [],
    )
    repo_data = dict(repo_data)
    repo_data["pr_status"] = pr_status
    repo_data["key_prs"] = key_prs
    target["prs"]["opened_count"] += count_value(prs.get("opened"))
    target["prs"]["updated_open_count"] += count_value(prs.get("updated_open"))
    target["prs"]["merged_count"] += count_value(prs.get("merged"))
    target["prs"]["closed_unmerged_count"] += count_value(prs.get("closed_unmerged"))
    pr_status = repo_data.get("pr_status") or {}
    for status in ["draft", "open", "closed_unmerged", "merged"]:
        target["pr_status_counts"][status] += count_value(pr_status.get(status))

    for key_pr in repo_data.get("key_prs") or []:
        key = key_pr.get("number")
        if key is None:
            continue
        existing = target["key_prs_by_number"].get(key)
        if not existing or int(key_pr.get("importance_score") or 0) > int(existing.get("importance_score") or 0):
            target["key_prs_by_number"][key] = key_pr

    commits = repo_data.get("commits") or {}
    target["commits"]["count"] += int(commits.get("count") or 0)
    target["commits"]["loc_added"] += int(commits.get("loc_added") or 0)
    target["commits"]["loc_removed"] += int(commits.get("loc_removed") or 0)
    target["commits"]["files_changed"] += int(commits.get("files_changed") or 0)
    merge_counter(target["commits"]["by_type"], commits.get("by_type"))
    merge_counter(target["commits"]["by_module"], commits.get("by_module"))

    releases = repo_data.get("releases") or []
    target["releases_count"] += count_value(releases)

    for contributor in repo_data.get("contributors_active") or []:
        target["contributors_active"].add(contributor)


def finalize_repo(repo_data):
    repo_data["commits"]["by_type"] = dict(repo_data["commits"]["by_type"])
    repo_data["commits"]["by_module"] = dict(repo_data["commits"]["by_module"])
    repo_data["contributors_active"] = sorted(repo_data["contributors_active"])
    repo_data["contributors_count"] = len(repo_data["contributors_active"])
    repo_data["pr_status_counts"] = dict(repo_data["pr_status_counts"])
    repo_data["key_prs"] = sorted(
        repo_data["key_prs_by_number"].values(),
        key=lambda value: int(value.get("importance_score") or 0),
        reverse=True,
    )[:15]
    del repo_data["key_prs_by_number"]
    return repo_data


def empty_repo_aggregate():
    return {
        "prs": {
            "opened_count": 0,
            "updated_open_count": 0,
            "merged_count": 0,
            "closed_unmerged_count": 0,
        },
        "pr_status_counts": Counter(),
        "key_prs_by_number": {},
        "commits": {
            "count": 0,
            "loc_added": 0,
            "loc_removed": 0,
            "files_changed": 0,
            "by_type": Counter(),
            "by_module": Counter(),
        },
        "releases_count": 0,
        "contributors_active": set(),
    }


def main():
    parser = argparse.ArgumentParser(description="Aggregate tracker daily snapshots")
    parser.add_argument("--data-repo", help="GitHub owner/repo for tracker data")
    parser.add_argument("--type", choices=["weekly", "monthly"], required=True)
    parser.add_argument("--end-date", required=True, help="Inclusive end date YYYY-MM-DD")
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--fixture-dir", help="Read local daily JSON files instead of GitHub")
    parser.add_argument("--summary-fixture-dir", help="Read persisted daily Markdown summaries from local fixture repo")
    parser.add_argument("--project", help="Project path segment for persisted Markdown summaries")
    parser.add_argument("--repos", help="Comma-separated repos for gap fill")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="Timezone for gap fill")
    parser.add_argument("--gap-fill", action="store_true", help="Fetch missing daily snapshots")
    parser.add_argument("--gap-fill-fixture", help="Fixture JSON used by tracker-fetch during gap fill")
    args = parser.parse_args()

    if not args.fixture_dir and not args.data_repo and not args.summary_fixture_dir:
        print("ERROR: --data-repo is required without --fixture-dir or --summary-fixture-dir", file=sys.stderr)
        return 2

    end_date = date.fromisoformat(args.end_date)
    start_date = end_date - timedelta(days=args.days - 1)
    expected_dates = [day for day in daterange(start_date, end_date)]
    loaded = []
    missing_dates = []
    gap_filled_dates = []
    daily_summaries = []
    missing_summary_dates = []
    errors = []
    repos = defaultdict(empty_repo_aggregate)
    timezone = None

    for day in expected_dates:
        if args.summary_fixture_dir:
            summary = load_summary_from_fixture(args.summary_fixture_dir, day, args.project)
        else:
            summary = load_summary_from_repo(args.data_repo, day, args.project)
        if summary is None:
            missing_summary_dates.append(day.isoformat())
        else:
            daily_summaries.append(summary)

        if args.fixture_dir:
            snapshot = load_snapshot_from_fixture(args.fixture_dir, day)
        else:
            snapshot = load_snapshot_from_repo(args.data_repo, day)
        if snapshot is None:
            if args.gap_fill:
                snapshot = fetch_gap_snapshot(args, day)
                if snapshot is not None:
                    gap_filled_dates.append(day.isoformat())
            if snapshot is None:
                missing_dates.append(day.isoformat())
                continue
        loaded.append(day.isoformat())
        timezone = timezone or snapshot.get("timezone")
        for repo, repo_data in (snapshot.get("repos") or {}).items():
            aggregate_repo(repos[repo], repo_data)
        for error in snapshot.get("errors") or []:
            errors.append(error)

    finalized_repos = {
        repo: finalize_repo(repo_data)
        for repo, repo_data in sorted(repos.items())
    }
    output = {
        "type": args.type,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "timezone": timezone or "unknown",
        "coverage": {
            "actual_days": len(loaded),
            "expected_days": len(expected_dates),
            "coverage_ratio": round(len(loaded) / len(expected_dates), 4) if expected_dates else 0,
            "loaded_dates": loaded,
            "missing_dates": missing_dates,
            "gap_filled_dates": gap_filled_dates,
            "summary_days": len(daily_summaries),
            "missing_summary_dates": missing_summary_dates,
        },
        "errors": errors,
        "daily_summaries": daily_summaries,
        "repos": finalized_repos,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
