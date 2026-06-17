# Skill System

## Mental Model

Skills are markdown SOPs for AI behavior. They are not Python modules and are
not executed directly. The AI reads them, follows their steps, and uses scripts
when the skill says to.

The registry, not the filesystem alone, defines which skills exist.

```text
agents/skills-registry.json active[] = approved usable skills
agents/skills-registry.json pending[] = drafts, not usable
skills/*.md = approved skill instructions
skills/pending/*.md = draft skill instructions
```

## Approval Gate

Pending skills must not be used. This is an explicit repo rule.

Lifecycle:

1. Search active skills with `scripts/search_skills.py`.
2. If there is no match, tell the user no skill exists yet.
3. Ask whether to draft one.
4. Draft with `scripts/create_skill.py`.
5. Human reviews/edits pending markdown.
6. Approve with `scripts/approve_skill.py`.
7. Approved skill moves to `skills/` and registry `active[]`.
8. Chroma is updated automatically if possible, for optional semantic search.

## Active Skills

### `fetch-pr`

File: `skills/fetch-pr.md`

Purpose: fetch latest or specified PR diff and metadata from GitHub.

Primary script: `scripts/fetch_github.py`.

### `code-reviewer`

File: `skills/code-reviewer.md`

Purpose: review fetched PR diff for bugs, security issues, style, and quality.

Expected input: fetched diff JSON from `outputs/reviews/`.

Output: structured findings in AI memory.

### `report-writer`

File: `skills/report-writer.md`

Purpose: write a markdown review report and optionally post it.

Primary scripts:

- `scripts/update_schedule.py`
- `scripts/post_review_comment.py`

### `skill-creator`

File: `skills/skill-creator.md`

Purpose: draft new pending skills when no active skill matches a task.

Primary script: `scripts/create_skill.py`.

### `dependency-checker`

File: `skills/dependency-checker.md`

Purpose: review dependency files for version changes, outdated packages, and
known vulnerable packages.

### `test-coverage-checker`

File: `skills/test-coverage-checker.md`

Purpose: check whether new code in a PR has corresponding test coverage.

### `pr-summary-writer`

File: `skills/pr-summary-writer.md`

Purpose: write a plain-English PR summary and merge readiness assessment.

### `security-scanner`

File: `skills/security-scanner.md`

Purpose: deeper review for secrets, injection vulnerabilities, and OWASP-style
issues.

### `code-complexity-analyzer`

File: `skills/code-complexity-analyzer.md`

Purpose: flag overly long, nested, or complex functions and technical debt.

### `documentation-checker`

File: `skills/documentation-checker.md`

Purpose: inspect changed functions/classes for missing docs, JSDoc/docstrings,
or misleading comments.

### `performance-reviewer`

File: `skills/performance-reviewer.md`

Purpose: identify N+1 queries, inefficient loops, memory leaks, and other
performance risks.

### `commit-message-reviewer`

File: `skills/commit-message-reviewer.md`

Purpose: review commit messages for clarity and conventional-commit style.

### `changelog-updater`

File: `skills/changelog-updater.md`

Purpose: generate Keep a Changelog style entries for PRs.

### `docker-reviewer`

File: `skills/docker-reviewer.md`

Purpose: review Dockerfile and docker-compose changes for security and best
practices.

## Skill Search

Always search before deciding no skill exists:

```bash
python scripts/search_skills.py --query "{task description}"
```

Search uses:

- keyword matching by default.
- Chroma only when `--semantic` is passed.

## Skill Registry Consistency Rules

For every active skill:

- `name` should match the markdown filename without `.md`.
- `file` should be repo-relative, e.g. `skills/code-reviewer.md`.
- `description` should be one sentence and useful for semantic retrieval.
- `tags` should include domain terms and user phrasing variants.

For pending skills:

- Keep file under `skills/pending/`.
- Keep registry entry under `pending[]`.
- Do not use until approved.

## Chroma Indexing Rules

Run:

```bash
python scripts/index_skills.py
```

after:

- manually editing active skill metadata.
- deleting `.chroma/`.
- seeing stale or incorrect semantic results.

Approving a skill attempts to upsert just that skill automatically.
