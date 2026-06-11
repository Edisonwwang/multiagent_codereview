# Code Reviewer Agent Standard Context

This folder is the repo context pack for another AI or maintainer. Read these
files before changing behavior:

1. `01-overview.md` - purpose, mental model, and non-goals.
2. `02-repository-map.md` - folder-by-folder and file-by-file map.
3. `03-runtime-architecture.md` - how scripts, skills, state, Chroma, and GitHub fit together.
4. `04-data-contracts.md` - JSON schemas, generated artifact names, and required fields.
5. `05-script-reference.md` - command reference and implementation notes for every script.
6. `06-skill-system.md` - active skills, approval gate, registry, and skill lifecycle.
7. `07-workflows.md` - setup, review, report posting, and skill creation workflows.
8. `08-quality-and-maintenance.md` - testing, known constraints, coding standards, and future hardening.
9. `09-ai-operating-guide.md` - rules for future AI agents working in this repo.

Current repo state reflected here: local workspace as of 2026-06-11 after the
production-hardening pass that introduced shared helpers, dependency files, and
unit tests.

Core purpose: this is a local multi-agent code review workspace. Python scripts
perform deterministic operations such as GitHub API calls, state updates, skill
indexing, and comment posting. Codex or Claude performs judgment-heavy review
work by reading markdown skills under `skills/`.
