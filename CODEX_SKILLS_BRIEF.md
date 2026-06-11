# CODEX BRIEF — Inflate Skills Library (10 New Skills)

## Your Job
Add 10 new skill files to the code-reviewer-agent system.
Create each file exactly as shown. Update skills-registry.json with all new entries.
These go directly into skills/ (not pending/) — Edison has explicitly approved them.
Work top to bottom. Do not skip any skill.

---

## STEP 1 — Confirm working directory

```bash
pwd && ls skills/
```

Expected: inside code-reviewer-agent/ with existing skill files visible.

---

## STEP 2 — Create all 10 skill files

---

### FILE: skills/dependency-checker.md

```markdown
# Skill: dependency-checker

## Goal
Scan dependency files in a PR diff for outdated packages, known vulnerabilities,
and suspicious version changes.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look for any of these files in files_changed:
   - package.json / package-lock.json
   - requirements.txt / Pipfile / pyproject.toml
   - Gemfile / Cargo.toml / go.mod
   If none of these files were changed, print "No dependency files changed" and stop.

2. For each dependency file changed, extract:
   - Packages that were added (new dependencies)
   - Packages that were removed
   - Packages whose versions changed

3. Flag the following as WARNING:
   - Any package pinned to an exact old version (e.g. lodash@4.0.0 when latest is 4.17.x)
   - Any package added without a version pin (e.g. "requests" with no version)
   - Version downgrades (version went lower than before)

4. Flag the following as CRITICAL:
   - Any package known to have published malicious versions in the past
     (event-stream, ua-parser-js, colors, faker — check if version matches known bad versions)
   - Private package names that look like dependency confusion attacks
     (internal name with a public registry version suddenly appearing)

5. Flag the following as SUGGESTION:
   - More than 5 new dependencies added in one PR (suggest splitting)
   - Dev dependencies being added to production dependencies list

6. Print summary and store findings for report-writer.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- No dependency files in PR → print notice and stop cleanly
- Cannot parse dependency file format → note it as unreadable and skip that file
```

---

### FILE: skills/test-coverage-checker.md

```markdown
# Skill: test-coverage-checker

## Goal
Check whether new code added in a PR has corresponding test coverage.
Flag untested functions, classes, and critical paths.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Separate files into two buckets:
   - Source files: .py, .js, .ts, .jsx, .tsx, .rb, .go, .java, .cs
   - Test files: any file with test, spec, __tests__ in the name or path

2. For each source file with additions:
   - Extract new function and class definitions from the patch
   - Check if a corresponding test file exists in files_changed
   - Check if the test file references the new function/class names

3. Flag as WARNING:
   - New public functions with no corresponding test file changed
   - New classes with no constructor test visible in the diff

4. Flag as SUGGESTION:
   - New private/internal helpers with no tests (lower priority)
   - Test file exists but new function name does not appear in it

5. Flag as CRITICAL:
   - New authentication, authorisation, or payment-related code with zero tests

6. If no source files were changed, print "No source files changed" and stop.

7. Print summary: X new functions found, Y have tests, Z are untested.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Binary files or minified files → skip, note as unanalysable
- No source files in diff → stop cleanly with notice
```

---

### FILE: skills/pr-summary-writer.md

```markdown
# Skill: pr-summary-writer

## Goal
Write a plain English summary of what a PR does — what changed, why it matters,
and whether it looks ready to merge. Useful for non-technical reviewers and
for auto-generating PR descriptions.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Collect:
   - PR title and author
   - All filenames changed and their status (added/modified/removed)
   - The patch content of each file

2. Infer the purpose of the PR from the changes:
   - What problem does this solve?
   - What is the main change?
   - Are there side effects or related changes?

3. Write a summary using this structure:

   ## What this PR does
   [2-3 sentences explaining the change in plain English.
    No jargon. Write as if explaining to a product manager.]

   ## Files changed
   - {filename} — [one line: what changed and why]
   (one line per file, max 10 files, group similar ones)

   ## Risk level
   [Low / Medium / High]
   [One sentence explaining the risk assessment]

   ## Ready to merge?
   [Yes / Needs work / Needs review]
   [One sentence explaining why]

4. Save the summary to:
   outputs/reviews/{repo_slug}_pr{pr_number}_summary.md

---

## Output
- outputs/reviews/{repo_slug}_pr{pr_number}_summary.md

---

## Error Handling
- Empty diff → note PR has no file changes and stop
```

---

### FILE: skills/security-scanner.md

```markdown
# Skill: security-scanner

## Goal
Deep security scan of a PR diff. Goes beyond basic code review to specifically
hunt for secrets, injection vulnerabilities, insecure patterns, and OWASP issues.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file and scan every patch for the following.
   Flag ALL matches — do not skip any.

2. CRITICAL — Hardcoded secrets (flag any line matching these patterns):
   - Strings that look like API keys: long alphanumeric strings 20+ chars assigned to a variable
   - Passwords or secrets: variable names containing password, secret, token, key, api_key, auth
     with a hardcoded string value
   - Private keys: -----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----
   - Connection strings with credentials: mongodb://, postgres://, mysql:// with user:pass@
   - AWS keys: AKIA[A-Z0-9]{16}
   - GitHub tokens: ghp_, gho_, ghu_, ghs_, ghr_

3. CRITICAL — Injection vulnerabilities:
   - SQL: string concatenation used to build a query (f"SELECT... {user_input}")
   - Command injection: os.system(), subprocess with shell=True passing user input
   - HTML/JS injection: innerHTML, document.write with unescaped user input
   - Path traversal: file paths built from user input without sanitisation

4. WARNING — Insecure patterns:
   - MD5 or SHA1 used for password hashing
   - HTTP (not HTTPS) hardcoded URLs for external services
   - debug=True or NODE_ENV=development hardcoded in non-test files
   - eval() or exec() called with dynamic input
   - Disabling SSL verification (verify=False, ssl=False, rejectUnauthorized: false)

5. SUGGESTION — Security hygiene:
   - TODO or FIXME comments near security-sensitive code
   - Logging statements that print passwords, tokens, or user PII
   - Overly broad exception handlers that swallow security errors silently

6. Print count of findings per severity.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Binary or minified files → skip
- If no security issues found → explicitly state "No security issues detected"
```

---

### FILE: skills/code-complexity-analyzer.md

```markdown
# Skill: code-complexity-analyzer

## Goal
Identify code that is too complex, too long, or too deeply nested.
Flag it before it becomes technical debt.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Focus only on added lines (lines starting with +).

2. For each file, analyse the new code for:

   ### Function length
   - Count lines per function/method in added code
   - Flag as WARNING if any new function exceeds 40 lines
   - Flag as SUGGESTION if any new function is between 25-40 lines

   ### Nesting depth
   - Count indentation levels in added code
   - Flag as WARNING if nesting exceeds 4 levels (if inside if inside for inside try...)
   - Flag as SUGGESTION at 3 levels

   ### Cognitive complexity indicators
   - More than 5 if/else branches in one function → WARNING
   - Ternary operators nested inside other ternaries → SUGGESTION
   - Boolean expressions with more than 4 conditions → SUGGESTION

   ### Code duplication
   - Identical or near-identical blocks appearing more than once in the diff → SUGGESTION
   - Consider extraction into a shared function

3. Skip test files — complexity rules are relaxed for tests.

4. Print summary: X functions analysed, Y flagged.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot determine function boundaries → note file as unanalysable
- Minified or generated code → skip
```

---

### FILE: skills/documentation-checker.md

```markdown
# Skill: documentation-checker

## Goal
Check that new functions, classes, and modules added in a PR have adequate
documentation — docstrings, JSDoc, inline comments for complex logic.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look at added lines only.

2. For each new function or class definition found in added lines:

   ### Docstrings / JSDoc
   - Python: check if def is followed by a """ docstring
   - JavaScript/TypeScript: check if function is preceded by /** JSDoc block
   - Other languages: check for equivalent doc comment conventions
   - Flag as SUGGESTION if a public function has no doc comment
   - Flag as WARNING if a public function over 20 lines has no doc comment

   ### Inline comments
   - Flag as SUGGESTION if a block of 10+ lines of logic has no comments at all
   - Flag as WARNING if code uses a non-obvious algorithm with no explanation

   ### README / docs updates
   - If new public API endpoints, CLI flags, or config options are added:
     check if any .md or docs/ files were also modified in the PR
   - Flag as SUGGESTION if they were not

3. Skip test files.
4. Skip one-liner functions.

5. Print summary.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot parse file type → skip with note
```

---

### FILE: skills/performance-reviewer.md

```markdown
# Skill: performance-reviewer

## Goal
Spot common performance anti-patterns in added code before they hit production.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Focus on added lines.

2. Scan for these patterns:

   ### Database / query patterns (CRITICAL)
   - N+1 queries: a query inside a loop
   - SELECT * with no LIMIT in production code
   - Missing index hints on large table queries

   ### Memory patterns (WARNING)
   - Loading entire file into memory instead of streaming
   - Unbounded list/array growth inside a loop
   - Large objects stored in session or global state

   ### Loop patterns (WARNING)
   - Nested loops over large collections (O(n²) risk)
   - Repeated expensive calls inside a loop that could be cached outside
   - Array.find() or filter() called repeatedly on the same unchanged array

   ### Network patterns (WARNING)
   - Sequential awaits that could be parallelised with Promise.all()
   - Synchronous HTTP calls in Node.js
   - No timeout set on external HTTP calls

   ### Caching patterns (SUGGESTION)
   - Repeated identical function calls with same args (could be memoised)
   - No cache headers on static asset responses
   - Expensive computation run on every request with no caching

3. Skip test files.

4. Print summary.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot determine data sizes → note as assumption-dependent finding
```

---

### FILE: skills/commit-message-reviewer.md

```markdown
# Skill: commit-message-reviewer

## Goal
Review all commit messages in a PR against conventional commits format.
Good commit messages make the git history useful — bad ones make it useless.

---

## Inputs
- {repo} — GitHub repo in owner/repo format
- {pr_number} — PR number

---

## Steps

1. Fetch the commit list for the PR:
   python scripts/fetch_github.py --repo {repo} --pr {pr_number}
   Read the diff JSON — extract the pr_title and note it.
   For full commit messages, they are visible in the patch context.

2. Evaluate each commit message against conventional commits format:

   Good format:  type(scope): short description
   Types:        feat, fix, docs, style, refactor, test, chore, perf, ci
   Rules:
   - Subject line under 72 characters
   - Type prefix required
   - No capital letter after the colon
   - No full stop at the end of subject line
   - If body exists, blank line between subject and body

3. Flag as WARNING:
   - No type prefix (e.g. just "updated things")
   - Subject line over 72 characters
   - Vague messages: "fix", "update", "changes", "wip", "temp", "test"
   - All caps messages

4. Flag as SUGGESTION:
   - Missing scope (type: desc instead of type(scope): desc)
   - Could be more descriptive

5. Flag as CRITICAL:
   - Commit messages containing profanity or offensive content
   - Messages that contain passwords, tokens, or secrets

6. Print pass/fail per commit and overall score.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot fetch commits → use PR title as the only data point
```

---

### FILE: skills/changelog-updater.md

```markdown
# Skill: changelog-updater

## Goal
Generate a CHANGELOG.md entry for a PR. Saves time and keeps the changelog
consistent across all contributors.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill
- {version} — optional. The version this change belongs to (e.g. 1.2.0)

---

## Steps

1. Read the diff file. Collect:
   - PR title, author, PR number, PR URL
   - All filenames changed
   - The nature of changes (additions, deletions, modifications)

2. Infer the change type:
   - New feature added → Added
   - Bug fixed → Fixed
   - Existing feature changed → Changed
   - Feature removed → Removed
   - Security fix → Security
   - Performance improvement → Performance
   - Documentation only → Docs

3. Write a CHANGELOG entry in Keep a Changelog format:

   ## [{version}] - {today}  (use "Unreleased" if no version given)

   ### {Change Type}
   - {one line description of what changed} ([#{pr_number}]({pr_url})) — @{pr_author}

   (one bullet per logical change — group related file changes into one bullet)

4. Check if CHANGELOG.md exists in the repo (look in diff for it):
   - If it was modified in the PR: append the new entry after the [Unreleased] header
   - If it was NOT modified: save the entry to outputs/reviews/{repo_slug}_pr{pr_number}_changelog.md
     and tell the user to manually add it

5. Print the generated entry.

---

## Output
- Changelog entry printed to screen
- outputs/reviews/{repo_slug}_pr{pr_number}_changelog.md (if not added to existing file)

---

## Error Handling
- No CHANGELOG.md in repo → save to outputs/ and notify
- Cannot determine version → use Unreleased
```

---

### FILE: skills/docker-reviewer.md

```markdown
# Skill: docker-reviewer

## Goal
Review Dockerfile and docker-compose changes for security issues,
best practices violations, and image size problems.

---

## Inputs
- {diff_file} — path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look for Dockerfile, docker-compose.yml,
   docker-compose.yaml, .dockerfile files in files_changed.
   If none found, print "No Docker files changed" and stop.

2. For each Docker file changed, scan added lines for:

   ### CRITICAL — Security
   - Running as root: no USER instruction before CMD/ENTRYPOINT
   - Secrets in ENV or ARG: ENV PASSWORD=, ARG API_KEY=
   - ADD used instead of COPY (ADD can fetch remote URLs unexpectedly)
   - curl | bash or wget | sh patterns (piping remote scripts)
   - Privileged mode in docker-compose: privileged: true

   ### WARNING — Best practices
   - Using :latest tag (non-deterministic builds)
   - Multiple RUN apt-get install without --no-install-recommends
   - Not combining RUN commands (creates unnecessary layers)
   - COPY . . before installing dependencies (busts cache unnecessarily)
   - No HEALTHCHECK defined for long-running services
   - Exposed unnecessary ports (exposing 22/SSH in a web service)

   ### SUGGESTION — Image hygiene
   - Not cleaning apt cache: apt-get clean && rm -rf /var/lib/apt/lists/*
   - Dev dependencies installed in production image
   - No .dockerignore file referenced or visible in the PR
   - Base image not pinned to a digest (FROM node:18 vs FROM node:18@sha256:...)

3. Print summary per file.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- No Docker files in diff → stop cleanly with notice
```

---

## STEP 3 — Update skills-registry.json

Overwrite `agents/skills-registry.json` with this complete updated version:

```json
{
  "active": [
    {
      "name": "fetch-pr",
      "file": "skills/fetch-pr.md",
      "description": "Fetches the latest open PR diff from a GitHub repo via the API",
      "tags": ["github", "fetch", "pr", "diff"]
    },
    {
      "name": "code-reviewer",
      "file": "skills/code-reviewer.md",
      "description": "Reviews a fetched PR diff for bugs, security issues, and style problems",
      "tags": ["review", "code", "bugs", "security", "quality"]
    },
    {
      "name": "report-writer",
      "file": "skills/report-writer.md",
      "description": "Writes a structured markdown review report and optionally posts it as a GitHub PR comment",
      "tags": ["report", "markdown", "github", "comment", "publish"]
    },
    {
      "name": "skill-creator",
      "file": "skills/skill-creator.md",
      "description": "Drafts a new skill file when the agent encounters a task with no matching skill",
      "tags": ["meta", "skill", "create", "draft", "new"]
    },
    {
      "name": "dependency-checker",
      "file": "skills/dependency-checker.md",
      "description": "Scans dependency files for outdated packages, version changes, and known vulnerable packages",
      "tags": ["dependencies", "packages", "npm", "pip", "vulnerabilities", "versions"]
    },
    {
      "name": "test-coverage-checker",
      "file": "skills/test-coverage-checker.md",
      "description": "Checks whether new code added in a PR has corresponding test coverage",
      "tags": ["tests", "coverage", "tdd", "unit", "spec"]
    },
    {
      "name": "pr-summary-writer",
      "file": "skills/pr-summary-writer.md",
      "description": "Writes a plain English summary of what a PR does and whether it is ready to merge",
      "tags": ["summary", "plain english", "overview", "merge", "description"]
    },
    {
      "name": "security-scanner",
      "file": "skills/security-scanner.md",
      "description": "Deep security scan for secrets, injection vulnerabilities, and OWASP issues",
      "tags": ["security", "secrets", "injection", "owasp", "vulnerabilities", "tokens", "keys"]
    },
    {
      "name": "code-complexity-analyzer",
      "file": "skills/code-complexity-analyzer.md",
      "description": "Flags functions that are too long, too nested, or too complex",
      "tags": ["complexity", "refactor", "nesting", "functions", "technical debt"]
    },
    {
      "name": "documentation-checker",
      "file": "skills/documentation-checker.md",
      "description": "Checks new functions and classes for missing docstrings, JSDoc, and inline comments",
      "tags": ["documentation", "docstrings", "jsdoc", "comments", "readme"]
    },
    {
      "name": "performance-reviewer",
      "file": "skills/performance-reviewer.md",
      "description": "Spots common performance anti-patterns including N+1 queries, memory leaks, and inefficient loops",
      "tags": ["performance", "optimisation", "n+1", "memory", "loops", "queries"]
    },
    {
      "name": "commit-message-reviewer",
      "file": "skills/commit-message-reviewer.md",
      "description": "Reviews commit messages against conventional commits format for clarity and consistency",
      "tags": ["commits", "git", "conventional commits", "messages", "history"]
    },
    {
      "name": "changelog-updater",
      "file": "skills/changelog-updater.md",
      "description": "Generates a CHANGELOG.md entry for a PR in Keep a Changelog format",
      "tags": ["changelog", "release notes", "versioning", "history", "docs"]
    },
    {
      "name": "docker-reviewer",
      "file": "skills/docker-reviewer.md",
      "description": "Reviews Dockerfile and docker-compose changes for security issues and best practices",
      "tags": ["docker", "dockerfile", "containers", "security", "devops"]
    }
  ],
  "pending": []
}
```

---

## STEP 4 — Verify all files exist

```bash
ls skills/
```

Expected (14 files total):
```
changelog-updater.md
code-complexity-analyzer.md
code-reviewer.md
commit-message-reviewer.md
dependency-checker.md
docker-reviewer.md
documentation-checker.md
fetch-pr.md
performance-reviewer.md
pr-summary-writer.md
report-writer.md
security-scanner.md
skill-creator.md
test-coverage-checker.md
pending/
```

If any file is missing, create it before continuing.

---

## STEP 5 — Test the search across new skills

```bash
python scripts/search_skills.py --query "check dependencies vulnerabilities"
python scripts/search_skills.py --query "docker container security"
python scripts/search_skills.py --query "code too complex nested"
python scripts/search_skills.py --query "missing tests untested"
```

Each should return at least one relevant skill match with score > 0.

---

## STEP 6 — Commit and push

```bash
git add .
git status
```

Confirm .env is NOT staged.

```bash
git commit -m "feat: inflate skills library with 10 new review skills"
git push origin main
```

If push fails with 403, note it — Edison will push manually.

---

## STEP 7 — Final report

```
SKILLS INFLATION REPORT
=======================
Skills before : 4
Skills added  : 10
Skills total  : 14
Registry      : UPDATED (14 active, 0 pending)

New skills:
  dependency-checker       : CREATED
  test-coverage-checker    : CREATED
  pr-summary-writer        : CREATED
  security-scanner         : CREATED
  code-complexity-analyzer : CREATED
  documentation-checker    : CREATED
  performance-reviewer     : CREATED
  commit-message-reviewer  : CREATED
  changelog-updater        : CREATED
  docker-reviewer          : CREATED

Search tests  : PASS / FAIL
Git push      : PUSHED / NEEDS MANUAL PUSH

System now covers: code review, security, performance, testing,
documentation, dependencies, Docker, commits, changelogs, and summaries.

Ready for Phase 3 — Chroma vector DB.
```
