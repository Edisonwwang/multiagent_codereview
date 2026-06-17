# Runtime Architecture

## High-Level Flow

```text
User request
  -> Codex/Claude reads CLAUDE.md and standard context
  -> scripts/briefing.py checks scheduled work
  -> scripts/search_skills.py finds relevant skills
  -> AI reads active skill markdown
  -> scripts/fetch_github.py fetches PR data
  -> AI reviews diff using skills
  -> AI writes markdown report to outputs/reviews/
  -> scripts/update_schedule.py records state
  -> scripts/post_review_comment.py optionally posts to GitHub
```

## Separation Of Responsibilities

### AI Responsibilities

The AI is responsible for judgment:

- interpreting diff patches.
- deciding whether findings are real defects.
- writing review reports.
- deciding which specialized skills apply.
- asking before posting comments when the workflow requires confirmation.

### Script Responsibilities

Scripts are responsible for deterministic side effects:

- reading and writing JSON.
- GitHub API fetch/post calls.
- skill search and optional Chroma indexing/search calls.
- state mutation.
- skill creation and approval mechanics.

## Shared Helper Layer

### `common.py`

All project file paths should flow through `common.py`. This avoids scripts
breaking when run from a working directory other than repo root.

Important constants:

- `ROOT`
- `AGENTS_DIR`
- `OUTPUTS_DIR`
- `REVIEWS_DIR`
- `SKILLS_DIR`
- `PENDING_SKILLS_DIR`
- `CHROMA_DIR`
- `SCHEDULE_PATH`
- `STATE_PATH`
- `REGISTRY_PATH`

Important functions:

- `repo_slug(repo)`: converts `owner/repo` to `owner_repo`.
- `display_path(path)`: returns repo-relative path when possible.
- `load_json(path)`: UTF-8 JSON load.
- `atomic_write_json(path, data)`: temp-file write then replace.
- `write_text(path, content)`: UTF-8 text write with parent creation.
- `read_text(path)`: UTF-8 text read.

### `github_client.py`

All GitHub API calls should flow through `github_client.py`.

It loads `.env` from `ROOT / ".env"`, so scripts work even if invoked by
absolute path from another directory.

Important values/functions:

- `API_ROOT = "https://api.github.com"`
- `GITHUB_TOKEN`
- `headers(extra=None)`
- `request_json(url, method="GET", payload=None, extra_headers=None)`
- `get_json(url)`
- `get_all_pages(url, params=None)`
- `post_json(url, payload)`

Failure behavior: GitHub HTTP/URL failures print a message to stderr and exit
with status 1. This matches the command-line script style in the repo.

## Skill Search

Keyword search over `agents/skills-registry.json` is the default. Chroma is
optional semantic retrieval for skill metadata, not review state or report
storage.

Index source:

```text
agents/skills-registry.json -> active[] -> .chroma/
```

Search flow:

1. `scripts/search_skills.py` keyword-matches active registry entries.
2. If `--semantic` is passed and `.chroma/` exists, it tries Chroma first.
3. If Chroma is empty or fails, it falls back to keyword matching.

Chroma documents are built from skill name, description, and tags. The actual
skill instructions remain in `skills/*.md`.

## State Model

The repo uses JSON files for state:

- `schedule.json`: what should be reviewed and how often.
- `review_state.json`: what was reviewed and when.
- `skills-registry.json`: which skills are active or pending.

State is intentionally simple and local. It is not safe for concurrent writes
from multiple processes. Use it as a single-user local automation workspace.

## Artifact Model

Generated review artifacts live in `outputs/reviews/`:

- Diff JSON: `{owner}_{repo}_pr{number}_diff.json`
- Review markdown: `{owner}_{repo}_pr{number}_review.md`

These files are ignored by git.

## Error Handling Philosophy

Scripts should:

- fail fast on missing required inputs.
- print clear `[ERROR]` messages to stderr.
- exit with non-zero status on failed deterministic operations.
- avoid guessing after script-level failures.
- use atomic writes for tracked JSON state.

The AI should report script errors to the user instead of inventing missing data.
