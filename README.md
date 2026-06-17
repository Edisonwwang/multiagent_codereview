# Multiagent Code Reviewer

A multi-agent code review workspace for reviewing GitHub pull requests with
Codex or Claude Code. It fetches PR diffs and commit metadata, selects the
right review skill through semantic search, writes markdown reports, and can
post those reports back to GitHub when a token is configured.

The optional pixel-art office UI is provided by
[pixtuoid](https://ivanwng97.github.io/pixtuoid/). Pixtuoid is installed
separately; this repository contains the review agent workspace, not the UI
source code.

---

## What It Does

The system uses a self-expanding skill library tracked in
`agents/skills-registry.json`. Active skills live in `skills/`; new generated
skills are drafted into `skills/pending/` and must be approved before use.

Core pipeline skills:

| Skill | File | Job |
|---|---|---|
| `fetch-pr` | `skills/fetch-pr.md` | Fetches PR diff and commit metadata from GitHub |
| `code-reviewer` | `skills/code-reviewer.md` | Reviews changed lines for bugs, security, quality, and style |
| `report-writer` | `skills/report-writer.md` | Writes a structured report and can post it as a PR comment |
| `skill-creator` | `skills/skill-creator.md` | Drafts new pending skills when no active skill matches |

Specialized review skills cover dependencies, tests, summaries, security,
complexity, documentation, performance, commit messages, changelogs, and Docker.

---

## Folder Structure

```text
code-reviewer-agent/
|-- CLAUDE.md                    # Claude Code startup instructions
|-- .env.example                 # Environment template
|-- .env                         # Local tokens, never committed
|-- requirements.txt             # Runtime Python dependencies
|-- requirements-dev.txt         # Developer dependency entry point
|
|-- agents/
|   |-- schedule.json            # What repos to review and how often
|   |-- review_state.json        # Memory of what has been reviewed
|   `-- skills-registry.json     # Active and pending skill registry
|
|-- skills/
|   |-- pending/                 # Approval gate: not used until approved
|   |-- fetch-pr.md
|   |-- code-reviewer.md
|   |-- report-writer.md
|   |-- skill-creator.md
|   `-- *.md                     # Other active review skills
|
|-- scripts/
|   |-- briefing.py              # Startup briefing and token warning
|   |-- common.py                # Shared repo paths and JSON/text helpers
|   |-- fetch_github.py          # Calls GitHub API and saves diff JSON
|   |-- github_client.py         # Shared GitHub REST client and pagination
|   |-- orchestrator.py          # Fetches PR data, tracks review outputs, aggregates report
|   |-- search_skills.py         # Semantic Chroma search with text fallback
|   |-- index_skills.py          # Rebuilds the Chroma skill index
|   |-- create_skill.py          # Drafts pending skill templates
|   |-- approve_skill.py         # Promotes pending skills and auto-indexes them
|   |-- post_review_comment.py   # Posts report as GitHub PR comment
|   `-- update_schedule.py       # Updates state after a review
|
|-- tests/
|   `-- test_scripts.py          # Unit tests for script behavior
|
|-- .chroma/                     # Local Chroma vector DB, git-ignored
`-- outputs/
    `-- reviews/                 # Generated diffs and reports, git-ignored
```

---

## One-Time Setup

Run these once on a machine.

### 1. Install Codex

Install Codex using the current official instructions for your environment.
After installation, confirm it is available:

```bash
codex --version
```

### 2. Install Python Dependencies

Chroma powers semantic skill search:

```bash
pip install -r requirements.txt
```

For development and test work, install the development dependency entry point:

```bash
pip install -r requirements-dev.txt
```

### 3. Build the Skill Index

Run this once after setup, and again whenever active skills are changed manually:

```bash
python scripts/index_skills.py
```

Expected output includes:

```text
[OK] Indexed 14 skills into Chroma at .chroma/
```

`scripts/approve_skill.py` indexes newly approved skills automatically.

### 4. Install pixtuoid

```bash
npm install -g pixtuoid
```

### 5. Install pixtuoid hooks

Pixtuoid hooks are a one-time setup step, not something you run every session.

On macOS/Linux, Codex hooks may be available:

```bash
pixtuoid install-hooks --target codex
```

On Windows, pixtuoid currently reports that Codex hooks are not supported yet.
If you use Claude Code on Windows, install Claude hooks instead:

```bash
pixtuoid install-hooks --target claude
```

If you are unsure which targets are supported on your machine, run:

```bash
pixtuoid install-hooks --target all
```

### 6. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add a GitHub token:

```env
GITHUB_TOKEN=your_github_token_here
```

Token scopes:

| Repo type | Scope |
|---|---|
| Public only | `public_repo` |
| Private repos | `repo` |

Without `GITHUB_TOKEN`, fetching public PRs can still work, but private repo
fetching and posting review comments will fail. `scripts/briefing.py` warns when
the token is missing.

### 7. Set Your Target Repo

Edit both files and replace `owner/your-repo` with your real repo:

```text
agents/schedule.json
agents/review_state.json
```

Example:

```json
"repo": "Edisonwwang/multiagent_codereview"
```

---

## Running Each Session

Run these whenever you want to use the UI and agent.

### Terminal 1: Start the Pixel Office UI

```bash
pixtuoid run
```

Leave this terminal open while you want the UI running. Stop it with `Ctrl+C`.

### Terminal 2: Start Codex in This Workspace

```bash
cd code-reviewer-agent
codex
```

Then ask Codex:

```text
run full review on owner/repo
```

The review pipeline saves markdown reports to:

```text
outputs/reviews/
```

---

## Skill Search and Approval

Search active skills semantically:

```bash
python scripts/search_skills.py --query "docker container security"
```

When `.chroma/` exists, results are shown as `[semantic search]` with distance
scores. Lower distance means a closer match. If the Chroma index is missing or
fails, `search_skills.py` falls back to keyword text search.

Draft a new pending skill:

```bash
python scripts/create_skill.py --name new-skill --description "What it does" --tags "tag1,tag2"
```

Approve a reviewed pending skill:

```bash
python scripts/approve_skill.py --name new-skill
```

Approval moves `skills/pending/new-skill.md` to `skills/new-skill.md`, updates
`agents/skills-registry.json`, and auto-indexes the skill into Chroma.

---

## Manual Pipeline Commands

You can also run the deterministic parts directly.

```bash
python scripts/briefing.py
python scripts/orchestrator.py --repo owner/repo --pr 1
python scripts/fetch_github.py --repo owner/repo
python scripts/search_skills.py --query "review this pull request"
python scripts/update_schedule.py --repo owner/repo --pr 1 --status reviewed
python scripts/post_review_comment.py --repo owner/repo --pr 1
```

The review-writing step is performed by Codex using the skill files and the
fetched diff JSON.
`orchestrator.py` keeps that boundary: it fetches the PR, writes
`outputs/reviews/{owner}_{repo}_pr{number}_state.json`, waits for reviewer
markdown files if `--wait` is passed, aggregates them into the final
`*_review.md`, then updates schedule state.

---

## Testing

Run the unit tests before committing script changes:

```bash
python -m unittest discover -s tests
```

The current tests cover shared JSON writing, update-schedule failure behavior,
and pending skill creation.

---

## Does It Work End to End?

The local review pipeline works when:

- Python is installed.
- `chromadb` is installed.
- The Chroma index has been built with `python scripts/index_skills.py`.
- The repo has an open PR, or you pass `--pr`.
- `scripts/fetch_github.py` can reach the GitHub API.
- Codex reviews the fetched diff and writes the report.
- Unit tests pass with `python -m unittest discover -s tests` after script
  changes.

Posting back to GitHub additionally requires:

- `.env` exists.
- `GITHUB_TOKEN` is set.
- The token has permission to comment on the PR.

Pixtuoid UI integration additionally depends on hook support for your CLI and
operating system. As of the local Windows test for this project, pixtuoid
reported that Codex hooks are not yet supported on Windows.

---

## How It Works

Each skill is a markdown SOP that tells Codex or Claude Code what to do.
Python scripts handle deterministic operations such as API calls, file writes,
skill indexing, approval, and state updates, while the AI performs the
judgment-heavy review step.

```text
CLAUDE.md             = Claude Code startup instructions
skills/*.md           = Step-by-step SOPs per role
agents/skills-registry.json = Active and pending skill source of truth
scripts/common.py           = Shared paths and JSON/text file helpers
scripts/github_client.py    = Shared GitHub REST client
scripts/search_skills.py    = Semantic Chroma search with text fallback
scripts/index_skills.py     = Rebuilds the local vector index
State JSON            = Memory between sessions
```

---

## Roadmap

- [x] Phase 1 - Core review pipeline: fetch, review, report
- [x] Phase 2 - Obsidian vault sync and self-expanding skill library
- [x] Phase 3 - Chroma vector DB for semantic skill retrieval
