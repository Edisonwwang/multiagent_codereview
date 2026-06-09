# Multiagent Code Reviewer

A multi-agent system that reviews GitHub pull requests using Claude Code,
with a pixel-art office UI via [pixtuoid](https://ivanwng97.github.io/pixtuoid/).

---

## What It Does

Three agents work in sequence to review any GitHub PR:

| Agent | Skill File | Job |
|---|---|---|
| Fetcher | `skills/fetch-pr.md` | Pulls the PR diff from GitHub API |
| Reviewer | `skills/code-reviewer.md` | Analyses diff for bugs, security issues, style |
| Reporter | `skills/report-writer.md` | Writes a structured report, optionally posts as PR comment |

---

## Folder Structure

```
code-reviewer-agent/
├── CLAUDE.md                  ← Claude Code reads this on startup
├── .env                       ← your tokens (never committed)
│
├── skills/
│   ├── fetch-pr.md            ← Agent 1: fetch PR diff from GitHub
│   ├── code-reviewer.md       ← Agent 2: review the code
│   └── report-writer.md       ← Agent 3: write + post the report
│
├── agents/
│   ├── schedule.json          ← what repos to review and how often
│   └── review_state.json      ← memory: what has been reviewed
│
├── scripts/
│   ├── briefing.py            ← startup: prints what is due today
│   ├── fetch_github.py        ← calls GitHub API, saves diff as JSON
│   ├── post_review_comment.py ← posts report as GitHub PR comment
│   └── update_schedule.py     ← updates state after a review
│
└── outputs/
    └── reviews/               ← diffs and reports saved here (git-ignored)
```

---

## Setup

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Install pixtuoid
```bash
npm install -g pixtuoid
pixtuoid install-hooks
```

### 3. Configure environment
```bash
cp .env.example .env
# Add your GITHUB_TOKEN to .env
# Create token at: github.com/settings/tokens
# Scopes: public_repo (public) or repo (private)
```

### 4. Set your target repo
Edit `agents/schedule.json` and `agents/review_state.json` —
replace `owner/your-repo` with the repo you want to review.

---

## Running

```bash
# Terminal 1 — pixel office UI
pixtuoid run

# Terminal 2 — the agent
cd code-reviewer-agent
claude
```

Claude Code reads `CLAUDE.md`, runs the daily briefing, and waits.

Then type:
```
run full review on owner/repo
```

The three agents run in sequence and save a markdown report to `outputs/reviews/`.

---

## How It Works

Each "agent" is Claude Code reading a skill file — a markdown SOP that tells it
exactly what to do, in what order, with what rules. Python scripts handle
deterministic operations (API calls, file writes, state updates) so the AI only
does what actually needs judgment.

```
CLAUDE.md     = the job description (read on startup)
Skill files   = step-by-step SOPs per role
Python scripts = exact, repeatable tool calls
State JSON    = memory between sessions
```

---

## Roadmap

- [x] Phase 1 — Core review pipeline (fetch → review → report)
- [ ] Phase 2 — Obsidian vault sync + self-expanding skill library
- [ ] Phase 3 — Human approval gate for new auto-generated skills
- [ ] Phase 4 — Vector DB (Chroma) for semantic skill retrieval at scale
