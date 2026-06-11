# Overview

## What This Repo Is

`code-reviewer-agent` is a local code review agent workspace. It is not a hosted
web app and not a complete standalone SaaS product. It is designed to be opened
inside Codex or Claude Code, where the AI can use markdown skills and helper
scripts to review GitHub pull requests.

The system has four major parts:

- `skills/`: markdown standard operating procedures for AI review tasks.
- `scripts/`: deterministic Python scripts for GitHub, state, Chroma indexing,
  and skill lifecycle operations.
- `agents/`: JSON state and registry files that define scheduled repos,
  review history, and active/pending skills.
- `outputs/reviews/`: generated diff JSON files and markdown review reports.

## Intended Use

The normal user flow is:

1. Configure `.env` with `GITHUB_TOKEN`.
2. Install dependencies from `requirements.txt`.
3. Build the Chroma skill index with `python scripts/index_skills.py`.
4. Ask Codex or Claude to review a repo or PR.
5. The AI runs scripts, reads skills, writes a report, and optionally posts it
   to GitHub.

## What The AI Does

The AI should:

- Run `scripts/briefing.py` to understand due reviews.
- Search for relevant skills using `scripts/search_skills.py`.
- Read the selected skill files before acting.
- Use deterministic scripts for GitHub fetches, state updates, skill indexing,
  and comment posting.
- Save review artifacts under `outputs/reviews/`.
- Never use pending skills until approved.

## What The Scripts Do

The scripts handle things that should not be left to model memory:

- API calls to GitHub.
- Pagination for PR files and commits.
- Loading `.env`.
- Atomic JSON state writes.
- Chroma skill indexing and lookup.
- Creating and approving skill files.
- Posting generated markdown reviews as PR comments.

## Non-Goals

This repo does not currently provide:

- A packaged CLI entry point.
- A web server.
- A database beyond local JSON files and local Chroma storage.
- Concurrent multi-user state safety.
- Full integration tests against live GitHub.
- A complete review engine independent of Codex or Claude.

## Production Readiness

The repo is now better hardened than a prototype:

- Shared utilities reduce duplicated path and API logic.
- Scripts resolve project files relative to repo root.
- JSON state writes are atomic.
- Unit tests cover the riskiest state/skill mutation paths.
- Dependencies are declared in `requirements.txt`.

Remaining production gaps are documented in `08-quality-and-maintenance.md`.
