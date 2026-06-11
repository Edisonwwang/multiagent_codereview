"""
fetch_github.py
Fetches a PR diff from GitHub and saves it as JSON for the review-code skill.

Usage:
  python scripts/fetch_github.py --repo owner/repo --pr 42
  python scripts/fetch_github.py --repo owner/repo
"""

import argparse
import json
import sys
from datetime import date

from common import REVIEWS_DIR, display_path, repo_slug
from github_client import API_ROOT, get_all_pages, get_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr",   type=int,      help="PR number (optional)")
    args = parser.parse_args()

    base = f"{API_ROOT}/repos/{args.repo}"

    if args.pr:
        pr_number = args.pr
    else:
        print(f"No PR number given - fetching latest open PR for {args.repo}...")
        prs = get_json(f"{base}/pulls?state=open&sort=updated&direction=desc&per_page=1")
        if not prs:
            print("[ERROR] No open PRs found.", file=sys.stderr)
            sys.exit(1)
        pr_number = prs[0]["number"]
        print(f"  -> Using PR #{pr_number}")

    pr      = get_json(f"{base}/pulls/{pr_number}")
    files   = get_all_pages(f"{base}/pulls/{pr_number}/files")
    commits = get_all_pages(f"{base}/pulls/{pr_number}/commits")

    files_changed = []
    for f in files:
        files_changed.append({
            "filename":  f["filename"],
            "status":    f["status"],
            "additions": f["additions"],
            "deletions": f["deletions"],
            "patch":     f.get("patch", ""),
        })

    commit_entries = []
    for commit in commits:
        commit_data = commit["commit"]
        author = commit_data.get("author") or {}
        commit_entries.append({
            "sha":     commit["sha"][:7],
            "message": commit_data.get("message", ""),
            "author":  author.get("name", ""),
            "date":    author.get("date", ""),
        })

    output = {
        "repo":          args.repo,
        "pr_number":     pr_number,
        "pr_title":      pr["title"],
        "pr_author":     pr["user"]["login"],
        "pr_url":        pr["html_url"],
        "base_branch":   pr["base"]["ref"],
        "head_branch":   pr["head"]["ref"],
        "fetched_date":  str(date.today()),
        "files_changed": files_changed,
        "commits":       commit_entries,
    }

    slug = repo_slug(args.repo)
    path = REVIEWS_DIR / f"{slug}_pr{pr_number}_diff.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as fp:
        json.dump(output, fp, indent=2)

    print(f"[OK] Saved diff -> {display_path(path)}")
    print(f"     {len(files_changed)} file(s) changed in PR #{pr_number}: {pr['title']}")
    print(f"     {len(commit_entries)} commit(s) included")

if __name__ == "__main__":
    main()
