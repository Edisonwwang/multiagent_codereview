"""
Small GitHub API client used by the review scripts.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from common import ROOT

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

API_ROOT = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def headers(extra=None):
    base = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        base["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    if extra:
        base.update(extra)
    return base


def request_json(url, method="GET", payload=None, extra_headers=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers(extra_headers),
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            if not body:
                return None, resp.headers
            return json.loads(body), resp.headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] GitHub API {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[ERROR] GitHub API request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_json(url):
    data, _ = request_json(url)
    return data


def has_next_page(link_header):
    return any('rel="next"' in part for part in link_header.split(","))


def get_all_pages(url, params=None):
    params = dict(params or {})
    params["per_page"] = 100

    items = []
    page = 1
    while True:
        params["page"] = page
        page_url = f"{url}?{urllib.parse.urlencode(params)}"
        data, response_headers = request_json(page_url)
        items.extend(data or [])
        if not has_next_page(response_headers.get("Link", "")):
            return items
        page += 1


def post_json(url, payload):
    data, _ = request_json(
        url,
        method="POST",
        payload=payload,
        extra_headers={"Content-Type": "application/json"},
    )
    return data
