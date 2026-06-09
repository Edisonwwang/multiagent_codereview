# Multiagent Code Reviewer

A multi-agent code review workspace for reviewing GitHub pull requests with
Codex or Claude Code. It fetches PR diffs, reviews changed lines against a
repeatable checklist, writes a markdown report, and can post that report back to
GitHub when a token is configured.

The optional pixel-art office UI is provided by
[pixtuoid](https://ivanwng97.github.io/pixtuoid/). Pixtuoid is installed
separately; this repository contains the review agent workspace, not the UI
source code.

---

## What It Does

Three agents work in sequence to review any GitHub PR:

| Agent | Skill File | Job |
|---|---|---|
| Fetcher | `skills/fetch-pr.md` | Pulls the PR diff from the GitHub API |
| Reviewer | `skills/code-reviewer.md` | Analyses changed lines for bugs, security issues, quality, and style |
| Reporter | `skills/report-writer.md` | Writes a structured report and can post it as a PR comment |

---

## Folder Structure

```text
code-reviewer-agent/
|-- CLAUDE.md                  # Claude Code startup instructions
|-- .env.example               # Environment template
|-- .env                       # Your local tokens, never committed
|
|-- skills/
|   |-- fetch-pr.md            # Agent 1: fetch PR diff from GitHub
|   |-- code-reviewer.md       # Agent 2: review the code
|   `-- report-writer.md       # Agent 3: write and post the report
|
|-- agents/
|   |-- schedule.json          # What repos to review and how often
|   `-- review_state.json      # Memory of what has been reviewed
|
|-- scripts/
|   |-- briefing.py            # Startup briefing
|   |-- fetch_github.py        # Calls GitHub API and saves diff JSON
|   |-- post_review_comment.py # Posts report as GitHub PR comment
|   `-- update_schedule.py     # Updates state after a review
|
`-- outputs/
    `-- reviews/               # Generated diffs and reports, git-ignored
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

### 2. Install pixtuoid

```bash
npm install -g pixtuoid
```

### 3. Install pixtuoid hooks

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

### 4. Configure environment

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

Without `GITHUB_TOKEN`, fetching public PRs can still work, but posting review
comments will fail.

### 5. Set your target repo

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

### Terminal 1: Start the pixel office UI

```bash
pixtuoid run
```

Leave this terminal open while you want the UI running. Stop it with `Ctrl+C`.

### Terminal 2: Start Codex in this workspace

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

## Manual Pipeline Commands

You can also run the deterministic parts directly.

```bash
python scripts/briefing.py
python scripts/fetch_github.py --repo owner/repo
python scripts/update_schedule.py --repo owner/repo --pr 1 --status reviewed
python scripts/post_review_comment.py --repo owner/repo --pr 1
```

The review-writing step is performed by Codex using the skill files and the
fetched diff JSON.

---

## Does It Work End to End?

The local review pipeline works when:

- Python is installed.
- The repo has an open PR.
- `scripts/fetch_github.py` can reach the GitHub API.
- Codex reviews the fetched diff and writes the report.

Posting back to GitHub additionally requires:

- `.env` exists.
- `GITHUB_TOKEN` is set.
- The token has permission to comment on the PR.

Pixtuoid UI integration additionally depends on hook support for your CLI and
operating system. As of the local Windows test for this project, pixtuoid
reported that Codex hooks are not yet supported on Windows.

---

## How It Works

Each "agent" is a markdown SOP that tells Codex or Claude Code what to do.
Python scripts handle deterministic operations such as API calls, file writes,
and state updates, while the AI performs the judgment-heavy review step.

```text
CLAUDE.md      = Claude Code startup instructions
Skill files    = Step-by-step SOPs per role
Python scripts = Repeatable tool calls
State JSON     = Memory between sessions
```

---

## Roadmap

- [x] Phase 1 - Core review pipeline: fetch, review, report
- [ ] Phase 2 - Obsidian vault sync and self-expanding skill library
- [ ] Phase 3 - Human approval gate for new auto-generated skills
- [ ] Phase 4 - Vector DB for semantic skill retrieval at scale
