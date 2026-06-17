# Data Contracts

## Repository Identifier

Repos are always passed as:

```text
owner/repo
```

For filenames, use `repo_slug(repo)`, which replaces `/` with `_`:

```text
owner/repo -> owner_repo
```

## `.env`

Expected variables:

```env
GITHUB_TOKEN=your_github_token_here
DEFAULT_REPO=owner/your-repo-name
```

`GITHUB_TOKEN`:

- required for private repo access.
- required for posting PR comments.
- optional for public fetches but recommended to avoid low rate limits.

`DEFAULT_REPO`:

- documented in `.env.example`.
- not currently consumed by the scripts after the latest hardening pass.
- may be used by future CLI wrappers.

## `agents/schedule.json`

Shape:

```json
{
  "tasks": [
    {
      "name": "Review Latest PR",
      "skill": "fetch-pr -> code-reviewer -> report-writer",
      "cadence_days": 1,
      "last_run": "2026-06-09",
      "repo": "owner/repo"
    }
  ]
}
```

Field meanings:

- `name`: display name used by briefing.
- `skill`: human-readable pipeline label.
- `cadence_days`: review frequency.
- `last_run`: ISO date string, `YYYY-MM-DD`.
- `repo`: GitHub repo identifier.

Consumers:

- `scripts/briefing.py`
- `scripts/update_schedule.py`

## `agents/review_state.json`

Shape:

```json
{
  "repos": [
    {
      "repo": "owner/repo",
      "last_pr_reviewed": 1,
      "last_run": "2026-06-09",
      "status": "reviewed"
    }
  ],
  "review_history": [
    {
      "repo": "owner/repo",
      "pr": 1,
      "date": "2026-06-09",
      "status": "reviewed"
    }
  ]
}
```

Allowed status values for update script:

- `reviewed`
- `skipped`
- `failed`

Consumers:

- `scripts/briefing.py`
- `scripts/update_schedule.py`

Important invariant: `scripts/update_schedule.py` requires the repo to exist in
both `schedule.json` and `review_state.json`. It exits with status 1 otherwise.

## `agents/skills-registry.json`

Shape:

```json
{
  "active": [
    {
      "name": "code-reviewer",
      "file": "skills/code-reviewer.md",
      "description": "Reviews a fetched PR diff for bugs, security issues, and style problems",
      "tags": ["review", "code", "bugs", "security", "quality"]
    }
  ],
  "pending": []
}
```

Active skill fields:

- `name`: normalized lowercase hyphenated skill id.
- `file`: repo-relative markdown file path.
- `description`: one-sentence semantic search summary.
- `tags`: list of search terms.

Pending skill entries may additionally include:

- `created`
- `status`

Approval removes pending-only metadata before moving to `active`.

## Fetched PR Diff JSON

Created by:

```text
python scripts/fetch_github.py --repo owner/repo --pr 42
```

Path:

```text
outputs/reviews/{owner}_{repo}_pr{number}_diff.json
```

Shape:

```json
{
  "repo": "owner/repo",
  "pr_number": 42,
  "pr_title": "Title",
  "pr_author": "username",
  "pr_url": "https://github.com/owner/repo/pull/42",
  "base_branch": "main",
  "head_branch": "feature",
  "fetched_date": "2026-06-11",
  "files_changed": [
    {
      "filename": "path/to/file.py",
      "status": "modified",
      "additions": 10,
      "deletions": 2,
      "patch": "@@ ..."
    }
  ],
  "commits": [
    {
      "sha": "abcdef1",
      "message": "commit subject",
      "author": "Author Name",
      "date": "2026-06-11T00:00:00Z"
    }
  ]
}
```

Notes:

- `files_changed` comes from GitHub PR files API.
- `commits` comes from GitHub PR commits API.
- Both collections are paginated through `github_client.get_all_pages`.
- `patch` may be empty for binary files or very large diffs.

## Review Markdown Report

Expected path:

```text
outputs/reviews/{owner}_{repo}_pr{number}_review.md
```

Expected report structure from `skills/report-writer.md`:

```markdown
# Code Review - {repo} PR #{pr_number}

**Reviewed by:** Code Reviewer Agent
**Date:** {today}
**Author:** {pr_author}
**PR Title:** {pr_title}

---

## Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| Warning | {n} |
| Suggestion | {n} |

---

## Findings

### {filename}

**[CRITICAL]** {description}
Line {line_number}: `{code_snippet}`
-> {recommended_fix}

---

## Overall Assessment
{assessment}
```

`scripts/post_review_comment.py` reads this exact file path and posts its entire
content as a GitHub issue comment on the PR.
