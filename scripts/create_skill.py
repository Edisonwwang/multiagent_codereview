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
from datetime import date

from common import (
    PENDING_SKILLS_DIR,
    REGISTRY_PATH,
    atomic_write_json,
    display_path,
    load_json,
    write_text,
)

SKILL_TEMPLATE = """# Skill: {name}

## Goal
{description}

---

## Inputs
- {{input_1}} - describe what this skill needs to run

---

## Steps

1. [Step 1 - describe exactly what to do]

2. [Step 2 - be specific, no vague instructions]

3. [Step 3 - include exact script calls where needed]
   python scripts/[script-name].py --arg value

4. Tell the user what happened and what the output is.

---

## Scripts Needed
- scripts/[script-name].py - [what it does]

---

## Output
- [describe what file or result this skill produces]

---

## Error Handling
- [error type] - [what to do]
- [error type] - [what to do]
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="skill name in lowercase-hyphenated format")
    parser.add_argument("--description", required=True, help="one sentence description")
    parser.add_argument("--tags", required=True, help="comma-separated tags")
    args = parser.parse_args()

    skill_name = args.name.lower().replace(" ", "-")
    tags = [tag.strip() for tag in args.tags.split(",")]
    filepath = PENDING_SKILLS_DIR / f"{skill_name}.md"

    # -- Write skill file --------------------------------------------------
    PENDING_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    if filepath.exists():
        print(f"[WARN] Skill already exists at {display_path(filepath)} - skipping file creation.")
    else:
        content = SKILL_TEMPLATE.format(name=skill_name, description=args.description)
        write_text(filepath, content)
        print(f"[OK] Skill file created - {display_path(filepath)}")

    # -- Update registry ---------------------------------------------------
    registry = load_json(REGISTRY_PATH)

    all_names = [skill["name"] for skill in registry["active"] + registry["pending"]]
    if skill_name in all_names:
        print(f"[WARN] {skill_name} already in registry - skipping registry update.")
    else:
        registry["pending"].append({
            "name": skill_name,
            "file": display_path(filepath),
            "description": args.description,
            "tags": tags,
            "created": str(date.today()),
            "status": "pending_approval",
        })
        atomic_write_json(REGISTRY_PATH, registry)
        print("[OK] Registered in skills-registry.json under pending")

    print(f"\n  Next: open {display_path(filepath)}, fill in all sections,")
    print(f"        then run: python scripts/approve_skill.py --name {skill_name}")


if __name__ == "__main__":
    main()
