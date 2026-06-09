"""
post_review_comment.py
Posts the generated review markdown as a comment on the GitHub PR.

Usage:
  python scripts/post_review_comment.py --repo owner/repo --pr 42
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def repo_slug(repo):
    return repo.replace("/", "_")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr",   required=True, type=int)
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set. Cannot post comment.", file=sys.stderr)
        sys.exit(1)

    slug        = repo_slug(args.repo)
    report_path = f"outputs/reviews/{slug}_pr{args.pr}_review.md"

    if not os.path.exists(report_path):
        print(f"[ERROR] Report not found at {report_path}", file=sys.stderr)
        sys.exit(1)

    with open(report_path) as f:
        body = f.read()

    url     = f"https://api.github.com/repos/{args.repo}/issues/{args.pr}/comments"
    payload = json.dumps({"body": body}).encode()
    headers = {
        "Authorization":        f"Bearer {GITHUB_TOKEN}",
        "Accept":               "application/vnd.github.v3+json",
        "Content-Type":         "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"[OK] Comment posted -> {result['html_url']}")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
