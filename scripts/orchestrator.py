"""
orchestrator.py
Runs the deterministic PR review steps and aggregates reviewer outputs.

Usage:
  python scripts/orchestrator.py --repo owner/repo --pr 42
  python scripts/orchestrator.py --repo owner/repo --pr 42 --wait 300
"""

import argparse
import subprocess
import sys
import time
from datetime import date

from common import ROOT, REVIEWS_DIR, atomic_write_json, display_path, read_text, repo_slug, write_text

DEFAULT_REVIEWERS = ["security", "style", "performance", "dependency"]


def review_paths(repo, pr, reviewers):
    slug = repo_slug(repo)
    return {
        reviewer: REVIEWS_DIR / f"{slug}_pr{pr}_{reviewer}.md"
        for reviewer in reviewers
    }


def state_path(repo, pr):
    return REVIEWS_DIR / f"{repo_slug(repo)}_pr{pr}_state.json"


def report_path(repo, pr):
    return REVIEWS_DIR / f"{repo_slug(repo)}_pr{pr}_review.md"


def write_state(repo, pr, reviewers, statuses):
    stages = {
        "fetch": {
            "status": "done",
            "output": f"{repo_slug(repo)}_pr{pr}_diff.json",
        }
    }
    for reviewer in reviewers:
        stages[reviewer] = {
            "status": statuses.get(reviewer, "pending"),
            "output": f"{repo_slug(repo)}_pr{pr}_{reviewer}.md",
        }
    stages["report"] = {
        "status": statuses.get("report", "pending"),
        "output": f"{repo_slug(repo)}_pr{pr}_review.md",
    }
    atomic_write_json(state_path(repo, pr), {"repo": repo, "pr": pr, "stages": stages})


def missing_outputs(paths):
    return [name for name, path in paths.items() if not path.exists()]


def aggregate_report(repo, pr, paths):
    parts = [
        f"# Code Review - {repo} PR #{pr}",
        "",
        f"**Reviewed by:** Code Reviewer Agent",
        f"**Date:** {date.today()}",
        "",
        "---",
        "",
    ]
    for name, path in paths.items():
        parts.extend([f"## {name.title()} Review", "", read_text(path).strip(), "", "---", ""])
    write_text(report_path(repo, pr), "\n".join(parts).rstrip() + "\n")


def run_script(script, *args):
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument(
        "--reviewers",
        default=",".join(DEFAULT_REVIEWERS),
        help="comma-separated output names to wait for",
    )
    parser.add_argument("--wait", type=int, default=0, help="seconds to wait for reviewer files")
    args = parser.parse_args()

    reviewers = [item.strip() for item in args.reviewers.split(",") if item.strip()]
    paths = review_paths(args.repo, args.pr, reviewers)

    run_script("fetch_github.py", "--repo", args.repo, "--pr", str(args.pr))
    write_state(args.repo, args.pr, reviewers, {})

    deadline = time.time() + args.wait
    missing = missing_outputs(paths)
    while missing and args.wait and time.time() < deadline:
        time.sleep(5)
        missing = missing_outputs(paths)

    if missing:
        write_state(args.repo, args.pr, reviewers, {name: "done" for name in reviewers if name not in missing})
        print("[WAITING] Create these reviewer outputs, then rerun this command:")
        for name in missing:
            print(f"  - {display_path(paths[name])}")
        print(f"[OK] State -> {display_path(state_path(args.repo, args.pr))}")
        return

    aggregate_report(args.repo, args.pr, paths)
    write_state(args.repo, args.pr, reviewers, {**{name: "done" for name in reviewers}, "report": "done"})
    run_script("update_schedule.py", "--repo", args.repo, "--pr", str(args.pr), "--status", "reviewed")
    print(f"[OK] Report -> {display_path(report_path(args.repo, args.pr))}")


if __name__ == "__main__":
    main()
