"""
post_review_comment.py
Posts the generated review markdown as a comment on the GitHub PR.

Usage:
  python scripts/post_review_comment.py --repo owner/repo --pr 42
"""

import argparse
import sys

from common import REVIEWS_DIR, display_path, read_text, repo_slug
from github_client import API_ROOT, GITHUB_TOKEN, post_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr",   required=True, type=int)
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set. Cannot post comment.", file=sys.stderr)
        sys.exit(1)

    slug = repo_slug(args.repo)
    report_path = REVIEWS_DIR / f"{slug}_pr{args.pr}_review.md"

    if not report_path.exists():
        print(f"[ERROR] Report not found at {display_path(report_path)}", file=sys.stderr)
        sys.exit(1)

    url = f"{API_ROOT}/repos/{args.repo}/issues/{args.pr}/comments"
    result = post_json(url, {"body": read_text(report_path)})
    print(f"[OK] Comment posted -> {result['html_url']}")

if __name__ == "__main__":
    main()
