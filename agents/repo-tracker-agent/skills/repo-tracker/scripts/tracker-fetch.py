#!/usr/bin/env python3
"""Fetch GitHub repo activity and emit a daily tracker snapshot JSON."""

import argparse
import copy
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


def eprint(message):
    print(message, file=sys.stderr)


def parse_dt(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def iso_dt(value):
    return value.isoformat(timespec="seconds")


def parse_repos(value):
    repos = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [repo for repo in repos if repo.count("/") != 1 or not all(repo.split("/", 1))]
    if invalid:
        raise ValueError(f"invalid repo format: {', '.join(invalid)}")
    return repos


def infer_window(args):
    tz_name = args.timezone
    if ZoneInfo is None:
        tz = timezone.utc
        tz_name = "UTC"
    else:
        tz = ZoneInfo(tz_name)

    if args.since and args.until:
        since = parse_dt(args.since)
        until = parse_dt(args.until)
        report_date = since.astimezone(tz).date()
        return report_date.isoformat(), tz_name, since, until

    if args.report_date:
        report_date = date.fromisoformat(args.report_date)
    else:
        report_date = datetime.now(tz).date() - timedelta(days=1)

    since = datetime.combine(report_date, time.min, tzinfo=tz)
    until = since + timedelta(days=1)
    return report_date.isoformat(), tz_name, since, until


def gh_api(endpoint):
    result = subprocess.run(
        ["gh", "api", endpoint],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout)


def gh_api_pages(endpoint, since=None, date_field="updated_at"):
    items = []
    for page in range(1, 101):
        separator = "&" if "?" in endpoint else "?"
        page_endpoint = f"{endpoint}{separator}per_page=100&page={page}"
        page_items = gh_api(page_endpoint)
        if not isinstance(page_items, list):
            raise RuntimeError(f"expected list response from {page_endpoint}")
        items.extend(page_items)
        if len(page_items) < 100:
            break
        if since and page_items:
            oldest = page_items[-1].get(date_field)
            if oldest and parse_dt(oldest) < since:
                break
    return items


def endpoint(path, params):
    return f"{path}?{urlencode(params)}"


def classify_commit(message):
    first = (message or "").splitlines()[0].lower()
    if first.startswith("feat:") or first.startswith("feature:"):
        return "feature"
    if first.startswith("fix:"):
        return "fix"
    if first.startswith("refactor:"):
        return "refactor"
    if first.startswith("docs:"):
        return "docs"
    if first.startswith("ci:") or first.startswith("build:"):
        return "ci"
    return "chore"


def infer_module(filename):
    if not filename:
        return "root"
    parts = [part for part in filename.split("/") if part]
    if not parts:
        return "root"
    if len(parts) == 1:
        return "root"
    if parts[0] in {".github", "src", "lib", "app", "packages"} and len(parts) > 1:
        return parts[1]
    return parts[0]


def truncate(value, limit=1200):
    value = value or ""
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def in_window(value, since, until):
    if not value:
        return False
    parsed = parse_dt(value)
    return since <= parsed < until


def pr_summary(pr, detail=None):
    source = detail or pr
    created_at = source.get("created_at")
    merged_at = source.get("merged_at")
    review_time = None
    if created_at and merged_at:
        review_time = round((parse_dt(merged_at) - parse_dt(created_at)).total_seconds() / 3600, 2)
    return {
        "number": source.get("number"),
        "title": source.get("title"),
        "state": source.get("state"),
        "user": ((source.get("user") or {}).get("login")),
        "created_at": created_at,
        "updated_at": source.get("updated_at"),
        "merged_at": merged_at,
        "closed_at": source.get("closed_at"),
        "additions": source.get("additions"),
        "deletions": source.get("deletions"),
        "changed_files": source.get("changed_files"),
        "labels": [label.get("name") for label in source.get("labels", []) if label.get("name")],
        "draft": bool(source.get("draft")),
        "current_status": pr_current_status(source),
        "review_time_hours": review_time,
        "content_signals": build_content_signals(source),
    }


def build_content_signals(pr_detail):
    files = pr_detail.get("files") or []
    changed_files = [
        {
            "filename": item.get("filename"),
            "status": item.get("status"),
            "additions": item.get("additions"),
            "deletions": item.get("deletions"),
            "changes": item.get("changes"),
        }
        for item in files[:50]
    ]
    modules = sorted({infer_module(item.get("filename")) for item in files if item.get("filename")})
    commit_subjects = [
        (((item.get("commit") or {}).get("message")) or "").splitlines()[0]
        for item in (pr_detail.get("commits_data") or [])[:20]
    ]
    commit_subjects = [subject for subject in commit_subjects if subject]
    summary_parts = []
    if pr_detail.get("body"):
        summary_parts.append("PR body")
    if changed_files:
        summary_parts.append(f"{len(changed_files)} changed files")
    if commit_subjects:
        summary_parts.append(f"{len(commit_subjects)} commits")
    return {
        "body_excerpt": truncate(pr_detail.get("body") or "", 1200),
        "changed_files": changed_files,
        "modules": modules,
        "commit_subjects": commit_subjects,
        "summary_basis": summary_parts,
    }


def enrich_pr_detail(repo, pr):
    detail = gh_api(f"repos/{repo}/pulls/{pr['number']}")
    try:
        detail["files"] = gh_api_pages(f"repos/{repo}/pulls/{pr['number']}/files")
    except Exception as exc:
        detail["files"] = []
        detail.setdefault("content_errors", []).append(f"files unavailable: {exc}")
    try:
        detail["commits_data"] = gh_api_pages(f"repos/{repo}/pulls/{pr['number']}/commits")
    except Exception as exc:
        detail["commits_data"] = []
        detail.setdefault("content_errors", []).append(f"commits unavailable: {exc}")
    return detail


def source_updated_at(pr, detail=None):
    source = detail or pr
    return source.get("updated_at")


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
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    changed_files = int(pr.get("changed_files") or 0)
    labels = pr.get("labels") or []
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
        "content_signals": pr.get("content_signals") or build_content_signals(pr),
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

    for status_prs in pr_status.values():
        status_prs.sort(key=pr_sort_score, reverse=True)

    key_prs = [
        key_pr_summary(item["pr"], item["event_types"])
        for item in sorted(by_number.values(), key=lambda value: pr_sort_score(value["pr"]), reverse=True)[:10]
    ]
    return pr_status, key_prs


def fetch_repo(repo, since, until):
    repo_meta = gh_api(f"repos/{repo}")
    default_branch = repo_meta.get("default_branch") or "main"

    opened = []
    updated_open = []
    merged = []
    closed_unmerged = []
    contributors = set()
    errors = []

    pulls = gh_api_pages(
        endpoint(
            f"repos/{repo}/pulls",
            {"state": "all", "sort": "updated", "direction": "desc"},
        ),
        since=since,
        date_field="updated_at",
    )
    for pr in pulls:
        if not any(
            in_window(pr.get(field), since, until)
            for field in ("created_at", "merged_at", "closed_at")
        ):
            continue
        detail = None
        try:
            detail = enrich_pr_detail(repo, pr)
        except Exception as exc:  # degraded detail fetch
            errors.append(f"PR #{pr.get('number')} detail unavailable: {exc}")

        summary = pr_summary(pr, detail)
        if in_window(summary.get("created_at"), since, until):
            opened.append(summary)
        elif summary.get("current_status") in {"draft", "open"} and in_window(source_updated_at(pr, detail), since, until):
            updated_open.append(summary)
        if in_window(summary.get("merged_at"), since, until):
            merged.append(summary)
            if summary.get("user"):
                contributors.add(summary["user"])
        if in_window(summary.get("closed_at"), since, until) and not summary.get("merged_at"):
            closed_unmerged.append(summary)

    commits_raw = gh_api_pages(
        endpoint(
            f"repos/{repo}/commits",
            {
                "sha": default_branch,
                "since": since.isoformat(),
                "until": until.isoformat(),
            },
        )
    )
    commit_items = []
    type_counts = Counter()
    module_counts = Counter()
    loc_added = 0
    loc_removed = 0
    files_changed = 0
    seen_shas = set()

    for item in commits_raw:
        sha = item.get("sha")
        if not sha or sha in seen_shas:
            continue
        seen_shas.add(sha)
        detail = None
        try:
            detail = gh_api(f"repos/{repo}/commits/{sha}")
        except Exception as exc:
            errors.append(f"commit {sha[:7]} detail unavailable: {exc}")
        source = detail or item
        message = ((source.get("commit") or {}).get("message")) or ""
        commit_type = classify_commit(message)
        type_counts[commit_type] += 1
        stats = source.get("stats") or {}
        loc_added += int(stats.get("additions") or 0)
        loc_removed += int(stats.get("deletions") or 0)
        files = source.get("files") or []
        files_changed += len(files)
        for file_info in files:
            module_counts[infer_module(file_info.get("filename"))] += 1
        author_login = ((source.get("author") or {}).get("login"))
        if author_login:
            contributors.add(author_login)
        commit_items.append(
            {
                "sha": sha,
                "message": message.splitlines()[0],
                "author": author_login or ((source.get("commit") or {}).get("author") or {}).get("name"),
                "date": ((source.get("commit") or {}).get("author") or {}).get("date"),
                "type": commit_type,
                "files_changed": len(files),
                "additions": int(stats.get("additions") or 0),
                "deletions": int(stats.get("deletions") or 0),
            }
        )

    releases_raw = gh_api_pages(f"repos/{repo}/releases")
    releases = []
    for release in releases_raw:
        if release.get("draft"):
            continue
        if not in_window(release.get("published_at"), since, until):
            continue
        releases.append(
            {
                "tag": release.get("tag_name"),
                "name": release.get("name"),
                "published_at": release.get("published_at"),
                "prerelease": bool(release.get("prerelease")),
                "body": (release.get("body") or "")[:500],
            }
        )

    pr_status, key_prs = build_pr_status_and_key_prs(opened, merged, closed_unmerged, updated_open)
    repo_data = {
        "default_branch": default_branch,
        "prs": {
            "opened": opened,
            "updated_open": updated_open,
            "merged": merged,
            "closed_unmerged": closed_unmerged,
        },
        "pr_status": pr_status,
        "key_prs": key_prs,
        "commits": {
            "count": len(commit_items),
            "items": commit_items[:50],
            "loc_added": loc_added,
            "loc_removed": loc_removed,
            "files_changed": files_changed,
            "by_type": dict(type_counts),
            "by_module": dict(module_counts),
        },
        "releases": releases,
        "contributors_active": sorted(contributors),
    }
    return repo_data, errors


def load_fixture(path, repos, report_date, timezone_name, since, until):
    data = json.loads(Path(path).read_text())
    data["report_date"] = report_date
    data["timezone"] = timezone_name
    data["window"] = {"since": iso_dt(since), "until": iso_dt(until)}
    data.setdefault("triggered_at", iso_dt(datetime.now(since.tzinfo)))
    data.setdefault("autopilot_run_id", "")
    data.setdefault("coverage", "full")
    data.setdefault("errors", [])
    fixture_repos = data.get("repos", {})
    if not fixture_repos:
        data["repos"] = {}
        return data
    first_value = copy.deepcopy(next(iter(fixture_repos.values())))
    data["repos"] = {}
    for repo in repos:
        repo_data = copy.deepcopy(fixture_repos.get(repo, first_value))
        prs = repo_data.get("prs") or {}
        pr_status, key_prs = build_pr_status_and_key_prs(
            prs.get("opened") or [],
            prs.get("merged") or [],
            prs.get("closed_unmerged") or [],
            prs.get("updated_open") or [],
        )
        repo_data["pr_status"] = pr_status
        repo_data["key_prs"] = key_prs
        data["repos"][repo] = repo_data
    return data


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub repo tracker data")
    parser.add_argument("--repos", required=True, help="Comma-separated owner/repo values")
    parser.add_argument("--since", help="Inclusive ISO datetime")
    parser.add_argument("--until", help="Exclusive ISO datetime")
    parser.add_argument("--report-date", help="Natural report date YYYY-MM-DD")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="IANA timezone")
    parser.add_argument("--fixture", help="Read a fixture JSON instead of calling GitHub")
    args = parser.parse_args()

    try:
        repos = parse_repos(args.repos)
        report_date, timezone_name, since, until = infer_window(args)
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 2

    if args.fixture:
        data = load_fixture(args.fixture, repos, report_date, timezone_name, since, until)
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0

    all_errors = []
    repo_results = {}
    success_count = 0
    for repo in repos:
        try:
            repo_data, repo_errors = fetch_repo(repo, since, until)
            repo_results[repo] = repo_data
            success_count += 1
            for error in repo_errors:
                all_errors.append({"repo": repo, "error": "partial", "message": error})
        except Exception as exc:
            message = str(exc)
            eprint(f"WARN: {repo} skipped - {message}")
            all_errors.append({"repo": repo, "error": "fetch_failed", "message": message})

    if success_count == 0:
        snapshot = {
            "report_date": report_date,
            "timezone": timezone_name,
            "window": {"since": iso_dt(since), "until": iso_dt(until)},
            "triggered_at": iso_dt(datetime.now(since.tzinfo)),
            "autopilot_run_id": "",
            "coverage": "failed",
            "errors": all_errors,
            "repos": {},
        }
        print(json.dumps(snapshot, indent=2, sort_keys=True))
        return 2

    coverage = "full" if success_count == len(repos) and not all_errors else "partial"
    snapshot = {
        "report_date": report_date,
        "timezone": timezone_name,
        "window": {"since": iso_dt(since), "until": iso_dt(until)},
        "triggered_at": iso_dt(datetime.now(since.tzinfo)),
        "autopilot_run_id": "",
        "coverage": coverage,
        "errors": all_errors,
        "repos": repo_results,
    }
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0 if coverage == "full" else 1


if __name__ == "__main__":
    sys.exit(main())
