# CODEX BRIEF — Phase 2: Obsidian Sync + Skill Creator + Approval Gate

## Your Job
Extend the existing code-reviewer-agent system with three new capabilities:
1. A pending/ approval folder so Edison approves all new skills before they run
2. A skill-creator meta-skill so the agent can draft new skills itself
3. A skills-registry.json so skills are tracked and searchable

Work top to bottom. Create every file exactly as shown.
Do not skip steps. Do not modify existing skill files unless told to.

---

## STEP 1 — Confirm working directory

```bash
pwd
ls
```

Expected: inside `code-reviewer-agent/` with CLAUDE.md, skills/, agents/, scripts/ visible.
If not, cd into it first.

---

## STEP 2 — Create the pending/ folder

```bash
mkdir -p skills/pending
```

Create a placeholder file so git tracks the folder:

```bash
cat > skills/pending/.gitkeep << 'EOF'
# Skills in this folder are PENDING APPROVAL.
# Edison must move a file from here to skills/ to activate it.
# The agent will never use skills from this folder.
EOF
```

---

## STEP 3 — Create skills-registry.json

Create `agents/skills-registry.json` with exactly this content.
This is the source of truth for all available skills.

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
    }
  ],
  "pending": []
}
```

---

## STEP 4 — Create the skill-creator meta-skill

Create `skills/skill-creator.md` with exactly this content:

```markdown
# Skill: skill-creator

## Goal
When the agent is asked to do something and no matching skill exists,
draft a new skill file and save it to skills/pending/ for Edison to review.
The agent must NEVER use a pending skill — it must wait for approval.

---

## When to trigger this skill
Trigger this skill when:
- The user asks for a task and no skill in skills-registry.json covers it
- run search_skills.py returns no relevant match
- The user explicitly says "create a new skill for X"

Do NOT trigger this skill if an existing skill can handle the task even partially.

---

## Inputs
- {task_description} — what the user wants the agent to do
- {context} — any relevant details about the task

---

## Steps

1. Run the skill search to double-check nothing exists:
   python scripts/search_skills.py --query "{task_description}"
   If a match is returned, use that skill instead and stop.

2. Analyse the task and define the new skill:
   - What is the goal in one sentence?
   - What are the inputs?
   - What are the steps (be as specific as possible)?
   - What scripts will it need? (list them — create stubs if needed)
   - What is the output?
   - What errors should it handle?

3. Name the skill using lowercase-hyphenated format:
   e.g. dockerfile-reviewer, dependency-checker, test-generator

4. Run the creation script:
   python scripts/create_skill.py --name {skill-name} --description "{one sentence description}" --tags "{tag1},{tag2},{tag3}"

   This will:
   - Create the skill file template at skills/pending/{skill-name}.md
   - Add it to agents/skills-registry.json under "pending"

5. Open the created file and fill in all sections completely:
   - Goal
   - Inputs
   - Steps (detailed, no vague instructions)
   - Scripts needed
   - Output
   - Error handling

6. Save the completed skill file.

7. Tell Edison:
   "New skill drafted: skills/pending/{skill-name}.md
   Open it in Obsidian or any editor, review it, and move it to skills/ to activate.
   I will not use this skill until you approve it."

---

## Rules
- NEVER save new skills directly to skills/ — always skills/pending/ first
- NEVER use a skill from skills/pending/ — pending means not approved
- Always fill in every section of the skill template completely
- If a new skill needs a Python script that does not exist, create a stub
  at scripts/{script-name}.py with a TODO comment explaining what it should do

---

## Output
- skills/pending/{skill-name}.md (new skill file, awaiting approval)
- agents/skills-registry.json updated with pending entry
```

---

## STEP 5 — Create scripts/create_skill.py

Create `scripts/create_skill.py` with exactly this content:

```python
"""
create_skill.py
Creates a new skill file in skills/pending/ and registers it in skills-registry.json.
Called by the skill-creator meta-skill.

Usage:
  python scripts/create_skill.py --name dockerfile-reviewer \
    --description "Reviews Dockerfile for security and best practices" \
    --tags "docker,security,review"
"""

import argparse
import json
import os
from datetime import date

REGISTRY_PATH = "agents/skills-registry.json"
PENDING_DIR   = "skills/pending"

SKILL_TEMPLATE = """# Skill: {name}

## Goal
{description}

---

## Inputs
- {{input_1}} — describe what this skill needs to run

---

## Steps

1. [Step 1 — describe exactly what to do]

2. [Step 2 — be specific, no vague instructions]

3. [Step 3 — include exact script calls where needed]
   python scripts/[script-name].py --arg value

4. Tell the user what happened and what the output is.

---

## Scripts Needed
- scripts/[script-name].py — [what it does]

---

## Output
- [describe what file or result this skill produces]

---

## Error Handling
- [error type] → [what to do]
- [error type] → [what to do]
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name",        required=True,  help="skill name in lowercase-hyphenated format")
    parser.add_argument("--description", required=True,  help="one sentence description")
    parser.add_argument("--tags",        required=True,  help="comma-separated tags")
    args = parser.parse_args()

    skill_name = args.name.lower().replace(" ", "-")
    tags       = [t.strip() for t in args.tags.split(",")]
    filepath   = os.path.join(PENDING_DIR, f"{skill_name}.md")

    # -- Write skill file --------------------------------------------------
    os.makedirs(PENDING_DIR, exist_ok=True)

    if os.path.exists(filepath):
        print(f"[WARN] Skill already exists at {filepath} — skipping file creation.")
    else:
        content = SKILL_TEMPLATE.format(name=skill_name, description=args.description)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"[OK] Skill file created → {filepath}")

    # -- Update registry ---------------------------------------------------
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    # Check not already registered
    all_names = [s["name"] for s in registry["active"] + registry["pending"]]
    if skill_name in all_names:
        print(f"[WARN] {skill_name} already in registry — skipping registry update.")
    else:
        registry["pending"].append({
            "name":        skill_name,
            "file":        filepath,
            "description": args.description,
            "tags":        tags,
            "created":     str(date.today()),
            "status":      "pending_approval"
        })
        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2)
        print(f"[OK] Registered in skills-registry.json under pending")

    print(f"\n  Next: open {filepath}, fill in all sections,")
    print(f"        then move to skills/ to activate.")

if __name__ == "__main__":
    main()
```

---

## STEP 6 — Create scripts/search_skills.py

Create `scripts/search_skills.py` with exactly this content:

```python
"""
search_skills.py
Searches skills-registry.json for skills matching a query.
Text-based for now — will be replaced with Chroma vector search in Phase 3.

Usage:
  python scripts/search_skills.py --query "review docker files"
  python scripts/search_skills.py --query "post github comment" --top 3
"""

import argparse
import json

REGISTRY_PATH = "agents/skills-registry.json"

def score(skill: dict, query: str) -> int:
    """Simple keyword match score."""
    q_words = query.lower().split()
    text    = (
        skill["name"].lower() + " " +
        skill["description"].lower() + " " +
        " ".join(skill.get("tags", []))
    )
    return sum(1 for word in q_words if word in text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="what you are looking for")
    parser.add_argument("--top",   type=int, default=3, help="number of results to return")
    args = parser.parse_args()

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    # Only search active skills — never suggest pending ones
    results = [
        (score(skill, args.query), skill)
        for skill in registry["active"]
    ]
    results.sort(key=lambda x: x[0], reverse=True)
    results = [(s, sk) for s, sk in results if s > 0]

    if not results:
        print(f"[NO MATCH] No active skills found for: '{args.query}'")
        print("  → Consider running the skill-creator to draft a new skill.")
        return

    print(f"\nTop {min(args.top, len(results))} skill(s) for '{args.query}':\n")
    for i, (sc, skill) in enumerate(results[:args.top], 1):
        print(f"  {i}. {skill['name']}  (score: {sc})")
        print(f"     {skill['description']}")
        print(f"     File: {skill['file']}")
        print()

if __name__ == "__main__":
    main()
```

---

## STEP 7 — Update CLAUDE.md

Overwrite `CLAUDE.md` with exactly this content:

```markdown
# Code Reviewer Agent System

You are an automated code reviewer with a self-expanding skill library.
Your skills live in skills/ and are tracked in agents/skills-registry.json.

---

## On Startup

1. Run `python scripts/briefing.py` to see what is due today
2. Present the pending list to the user
3. Wait for the user to say which task to run

---

## Finding the Right Skill

Before running any task, search for the right skill:

python scripts/search_skills.py --query "{task description}"

This returns the best matching skill from the active registry.
Read the returned skill file and follow its steps exactly.

---

## If No Skill Exists

If search_skills.py returns NO MATCH:
1. Tell the user: "I don't have a skill for this yet."
2. Ask: "Should I draft one?"
3. If yes: run the skill-creator skill (skills/skill-creator.md)
4. New skill goes to skills/pending/ — NEVER use it until Edison approves it

---

## Approval Gate — CRITICAL RULE

skills/pending/ = NOT approved. Never use these skills.
skills/          = Approved. Safe to use.

Edison approves a skill by moving it from skills/pending/ to skills/.
Until that happens, the skill does not exist as far as you are concerned.

---

## Available Skills (Active)

Loaded dynamically from agents/skills-registry.json.
Run search_skills.py to find the right one for any task.

Core pipeline:
- fetch-pr        → skills/fetch-pr.md
- code-reviewer   → skills/code-reviewer.md
- report-writer   → skills/report-writer.md
- skill-creator   → skills/skill-creator.md (meta — drafts new skills)

---

## Obsidian Sync

The skills/ folder is an Obsidian vault.
Any skill file created here appears in Obsidian automatically.
Edison can read, edit, and approve skills directly in Obsidian.

---

## Rules

- Never modify a source repository unless explicitly told to
- Always save outputs to outputs/reviews/ before posting anywhere
- Update agents/review_state.json after every completed review
- If a script fails, report the error and stop — do not guess
- Never use skills from skills/pending/
- Always run search_skills.py before deciding no skill exists
```

---

## STEP 8 — Verify everything

Run:
```bash
find . -type f | sort
```

Confirm these new files exist:
```
./agents/skills-registry.json
./scripts/create_skill.py
./scripts/search_skills.py
./skills/pending/.gitkeep
./skills/skill-creator.md
```

And CLAUDE.md has been updated (check first line says "self-expanding skill library").

---

## STEP 9 — Run functional tests

### Test 1 — search finds existing skills
```bash
python scripts/search_skills.py --query "review github pull request"
```
Expected: returns fetch-pr and/or code-reviewer with score > 0

### Test 2 — search returns no match for unknown task
```bash
python scripts/search_skills.py --query "send slack notification"
```
Expected: prints NO MATCH and suggests running skill-creator

### Test 3 — create_skill.py drafts a skill correctly
```bash
python scripts/create_skill.py \
  --name "test-skill" \
  --description "A test skill to verify the creation pipeline works" \
  --tags "test,verify,demo"
```
Expected:
- Creates skills/pending/test-skill.md
- Adds entry to agents/skills-registry.json under "pending"
- Prints confirmation

Verify the file exists:
```bash
cat skills/pending/test-skill.md
```

Verify the registry was updated:
```bash
python -c "import json; d=json.load(open('agents/skills-registry.json')); print([s['name'] for s in d['pending']])"
```
Expected: ['test-skill']

### Test 4 — clean up test skill
```bash
rm skills/pending/test-skill.md
```

Then manually remove the test-skill entry from agents/skills-registry.json pending array
so the registry stays clean. Leave it as:
```json
"pending": []
```

---

## STEP 10 — Commit and push

```bash
git add .
git status
```

Confirm:
- skills/pending/.gitkeep is staged
- agents/skills-registry.json is staged
- scripts/create_skill.py is staged
- scripts/search_skills.py is staged
- skills/skill-creator.md is staged
- CLAUDE.md shows as modified
- .env is NOT staged

Then:
```bash
git commit -m "feat: phase 2 - skill registry, skill-creator, and approval gate"
git push origin main
```

If push fails with 403 (known Codex account mismatch), note it and skip.
Edison will push manually.

---

## STEP 11 — Final report

Print this exact summary:

```
PHASE 2 BUILD REPORT
====================
skills/pending/       : CREATED (approval gate active)
agents/skills-registry.json : CREATED (4 active skills registered)
skills/skill-creator.md     : CREATED
scripts/create_skill.py     : CREATED
scripts/search_skills.py    : CREATED
CLAUDE.md             : UPDATED

Tests:
  search (match)      : PASS / FAIL
  search (no match)   : PASS / FAIL
  create_skill.py     : PASS / FAIL
  registry cleanup    : PASS / FAIL

Git push              : PUSHED / NEEDS MANUAL PUSH (403)

Phase 2 complete. To connect to Obsidian:
  Open Obsidian → Add vault → point it at the skills/ folder inside code-reviewer-agent/
  Any skill the agent creates in skills/ or skills/pending/ will appear automatically.

Next: Phase 3 — Chroma vector DB for semantic skill search at scale.
```
