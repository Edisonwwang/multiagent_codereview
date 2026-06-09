"""
fetch_github.py
Fetches a PR diff from GitHub and saves it as JSON for the review-code skill.

Usage:
  python scripts/fetch_github.py --repo owner/repo --pr 42
  python scripts/fetch_github.py --repo owner/repo
"""

import argparse
import json
import os
import sys
from datetime import date

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

def repo_slug(repo):
    return repo.replace("/", "_")

def get(url):
    import urllib.request
    import urllib.error
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[ERROR] GitHub API {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr",   type=int,      help="PR number (optional)")
    args = parser.parse_args()

    base = f"https://api.github.com/repos/{args.repo}"

    if args.pr:
        pr_number = args.pr
    else:
        print(f"No PR number given - fetching latest open PR for {args.repo}...")
        prs = get(f"{base}/pulls?state=open&sort=updated&direction=desc&per_page=1")
        if not prs:
            print("[ERROR] No open PRs found.", file=sys.stderr)
            sys.exit(1)
        pr_number = prs[0]["number"]
        print(f"  -> Using PR #{pr_number}")

    pr    = get(f"{base}/pulls/{pr_number}")
    files = get(f"{base}/pulls/{pr_number}/files?per_page=100")

    files_changed = []
    for f in files:
        files_changed.append({
            "filename":  f["filename"],
            "status":    f["status"],
            "additions": f["additions"],
            "deletions": f["deletions"],
            "patch":     f.get("patch", ""),
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
    }

    os.makedirs("outputs/reviews", exist_ok=True)
    slug = repo_slug(args.repo)
    path = f"outputs/reviews/{slug}_pr{pr_number}_diff.json"

    with open(path, "w") as fp:
        json.dump(output, fp, indent=2)

    print(f"[OK] Saved diff -> {path}")
    print(f"     {len(files_changed)} file(s) changed in PR #{pr_number}: {pr['title']}")

if __name__ == "__main__":
    main()
