# Script Reference

All scripts are meant to be run with Python from the repository. After the
helper refactor, project files are resolved from repo root even when scripts are
invoked by absolute path from another working directory.

## `scripts/briefing.py`

Command:

```bash
python scripts/briefing.py
```

Purpose:

- Warns if `GITHUB_TOKEN` is not loaded.
- Reads `agents/schedule.json`.
- Reads `agents/review_state.json`.
- Prints due reviews and recent review history.

Key behavior:

- Uses `days_since(last_run)` with ISO dates.
- Treats missing dates as very old.

## `scripts/fetch_github.py`

Commands:

```bash
python scripts/fetch_github.py --repo owner/repo --pr 42
python scripts/fetch_github.py --repo owner/repo
```

Purpose:

- Fetch a PR and save normalized diff metadata for AI review.

When `--pr` is omitted:

- Fetches the latest open PR sorted by updated time.
- Exits if no open PR exists.

Fetched endpoints:

- `/repos/{repo}/pulls/{pr_number}`
- `/repos/{repo}/pulls/{pr_number}/files`
- `/repos/{repo}/pulls/{pr_number}/commits`

Pagination:

- Files and commits use `github_client.get_all_pages`.

Output:

```text
outputs/reviews/{owner}_{repo}_pr{number}_diff.json
```

## `scripts/search_skills.py`

Commands:

```bash
python scripts/search_skills.py --query "review docker files"
python scripts/search_skills.py --query "check dependencies" --top 3
```

Purpose:

- Find the best active skills for a task description.

Search order:

1. Chroma semantic search if `.chroma/` exists and collection has entries.
2. Text keyword fallback over active skills.

Text fallback score:

- Counts query words found in `name`, `description`, or `tags`.

Output:

- Prints matching skill names, descriptions, paths, and Chroma distance when
  semantic search is used.

## `scripts/index_skills.py`

Command:

```bash
python scripts/index_skills.py
```

Purpose:

- Index all `active` skills from `agents/skills-registry.json` into Chroma.

Chroma collection:

```text
skills
```

Document text:

```text
{name}. {description}. tags: {tags}
```

Run this:

- after initial dependency setup.
- after manually editing active skill metadata.
- when Chroma appears stale.

## `scripts/create_skill.py`

Command:

```bash
python scripts/create_skill.py --name new-skill --description "What it does" --tags "tag1,tag2"
```

Purpose:

- Draft a new pending skill.

Behavior:

- Normalizes spaces in `--name` to hyphens and lowercases.
- Creates `skills/pending/{skill-name}.md`.
- Adds a matching pending entry to `agents/skills-registry.json`.
- Does not activate or index the skill.

Important:

- Pending skills are not used by the AI.
- A human should edit/review the pending markdown before approval.

## `scripts/approve_skill.py`

Command:

```bash
python scripts/approve_skill.py --name skill-name
```

Purpose:

- Promote a pending skill to active.

Behavior:

- Normalizes name.
- Requires `skills/pending/{skill-name}.md`.
- Requires matching pending registry entry.
- Refuses duplicate active skill names.
- Refuses overwrite if `skills/{skill-name}.md` already exists.
- Moves file into `skills/`.
- Updates registry atomically.
- Attempts Chroma upsert for the approved skill.

If Chroma indexing fails:

- The script warns but does not undo approval.
- Run `python scripts/index_skills.py` manually.

## `scripts/update_schedule.py`

Command:

```bash
python scripts/update_schedule.py --repo owner/repo --pr 42 --status reviewed
```

Allowed statuses:

- `reviewed`
- `skipped`
- `failed`

Purpose:

- Record review completion in schedule and state.

Behavior:

- Requires repo to exist in both `schedule.json` and `review_state.json`.
- Updates schedule task `last_run`.
- Updates repo state `last_pr_reviewed`, `last_run`, and `status`.
- Appends to `review_history`.
- Writes both JSON files atomically.

Failure:

- Unknown repo prints an error and exits 1 before writing changes.

## `scripts/post_review_comment.py`

Command:

```bash
python scripts/post_review_comment.py --repo owner/repo --pr 42
```

Purpose:

- Post an existing markdown review report to the PR as a GitHub issue comment.

Requires:

- `GITHUB_TOKEN` loaded from `.env` or environment.
- Existing report file:

```text
outputs/reviews/{owner}_{repo}_pr{number}_review.md
```

GitHub endpoint:

```text
POST /repos/{repo}/issues/{pr}/comments
```

## `scripts/common.py`

Use this for:

- project paths.
- loading JSON.
- writing JSON atomically.
- reading/writing UTF-8 text.
- formatting repo-relative display paths.

Do not add new hardcoded repo-relative paths to scripts if `common.py` already
has the right constant or helper.

## `scripts/github_client.py`

Use this for:

- GitHub GET requests.
- GitHub POST requests.
- pagination.
- token-aware headers.
- consistent API error handling.

Do not reimplement GitHub request logic inside individual scripts.
