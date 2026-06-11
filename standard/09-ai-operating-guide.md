# AI Operating Guide

This file is for future AI agents working in this repo.

## First Principles

This repo is a code review workspace. Do not treat it like a web app or a
library package unless the user explicitly asks to convert it.

Preserve the split:

- scripts handle deterministic work.
- skills guide AI judgment.
- JSON files hold local state.
- generated outputs stay under `outputs/reviews/`.

## Before Running A Review

1. Run:

   ```bash
   python scripts/briefing.py
   ```

2. Search skills:

   ```bash
   python scripts/search_skills.py --query "{user task}"
   ```

3. Read the selected active skill files.

4. Do not use `skills/pending/`.

## Before Changing Code

Read the relevant files first. Most behavior is small and explicit.

Use existing helpers:

- `common.py` for file paths and JSON.
- `github_client.py` for GitHub API.

Do not add new duplicated path constants such as:

```python
"agents/schedule.json"
"outputs/reviews"
".chroma"
```

Use the constants from `common.py` instead.

## Generated Files

Do not commit:

- `.env`
- `.chroma/`
- `outputs/reviews/*.json`
- `outputs/reviews/*.md`
- Python cache files.

The `standard/` folder is source documentation and should be commit-worthy.

## Review Report Rules

When writing a code review report:

- lead with findings.
- include severity.
- include file and line when possible.
- avoid preference-only comments.
- distinguish real bugs from maintainability suggestions.
- save the report before posting anywhere.
- ask before posting to GitHub.

## Skill Rules

Always honor the approval gate:

```text
skills/pending/ = draft only, never use
skills/ = approved and usable
```

If no skill matches:

1. Say no matching skill exists.
2. Ask whether to draft one.
3. Use `scripts/create_skill.py` if the user agrees.
4. Do not use it until approved.

## State Update Rules

After a completed review, run:

```bash
python scripts/update_schedule.py --repo owner/repo --pr {number} --status reviewed
```

Use `failed` or `skipped` only when that status accurately reflects the review
outcome.

If this script errors, report the error. Do not manually edit state unless the
user asks or the fix is clearly part of the task.

## Posting Rules

Only post to GitHub after user confirmation.

Command:

```bash
python scripts/post_review_comment.py --repo owner/repo --pr {number}
```

Posting requires:

- valid `GITHUB_TOKEN`.
- existing markdown report at the expected path.

## Verification Rules

Before telling the user code changes are complete, run:

```bash
python -m unittest discover -s tests
```

For script syntax on PowerShell:

```powershell
Get-ChildItem scripts -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
```

For skill search smoke test:

```bash
python scripts/search_skills.py --query "full code review of this repository"
```

## Common Mistakes To Avoid

- Running `python -m py_compile scripts/*.py` on PowerShell. Python will not
  expand that wildcard.
- Assuming `.env` loads from current working directory. It is loaded from repo
  root by `github_client.py` and `briefing.py`.
- Assuming Chroma is authoritative. The registry is authoritative; Chroma is an
  index.
- Using pending skills.
- Writing outputs outside `outputs/reviews/`.
- Reimplementing GitHub HTTP logic in a script.
- Updating `review_state.json` without also considering `schedule.json`.
