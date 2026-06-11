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
- {{input_1}} 鈥?describe what this skill needs to run

---

## Steps

1. [Step 1 鈥?describe exactly what to do]

2. [Step 2 鈥?be specific, no vague instructions]

3. [Step 3 鈥?include exact script calls where needed]
   python scripts/[script-name].py --arg value

4. Tell the user what happened and what the output is.

---

## Scripts Needed
- scripts/[script-name].py 鈥?[what it does]

---

## Output
- [describe what file or result this skill produces]

---

## Error Handling
- [error type] 鈫?[what to do]
- [error type] 鈫?[what to do]
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
        print(f"[WARN] Skill already exists at {filepath} 鈥?skipping file creation.")
    else:
        content = SKILL_TEMPLATE.format(name=skill_name, description=args.description)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"[OK] Skill file created 鈫?{filepath}")

    # -- Update registry ---------------------------------------------------
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    # Check not already registered
    all_names = [s["name"] for s in registry["active"] + registry["pending"]]
    if skill_name in all_names:
        print(f"[WARN] {skill_name} already in registry 鈥?skipping registry update.")
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
