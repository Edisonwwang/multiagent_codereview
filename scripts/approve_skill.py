"""
approve_skill.py
Moves a pending skill into the active skills folder and updates the registry.

Usage:
  python scripts/approve_skill.py --name skill-name
"""

import argparse
import json
import os
import sys

REGISTRY_PATH = "agents/skills-registry.json"
PENDING_DIR = "skills/pending"
ACTIVE_DIR = "skills"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="pending skill name without .md")
    args = parser.parse_args()

    skill_name = args.name.lower().replace(" ", "-")
    pending_path = os.path.join(PENDING_DIR, f"{skill_name}.md")
    active_path = os.path.join(ACTIVE_DIR, f"{skill_name}.md")

    if not os.path.exists(pending_path):
        print(f"[ERROR] Pending skill not found: {pending_path}", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    pending = registry.get("pending", [])
    active = registry.get("active", [])

    entry = None
    remaining_pending = []
    for skill in pending:
        if skill.get("name") == skill_name:
            entry = skill
        else:
            remaining_pending.append(skill)

    if entry is None:
        print(f"[ERROR] Skill '{skill_name}' not found in registry pending[]", file=sys.stderr)
        sys.exit(1)

    if any(skill.get("name") == skill_name for skill in active):
        print(f"[ERROR] Skill '{skill_name}' already exists in registry active[]", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(active_path):
        print(f"[ERROR] Active skill file already exists: {active_path}", file=sys.stderr)
        sys.exit(1)

    os.replace(pending_path, active_path)

    entry["file"] = active_path.replace("\\", "/")
    entry.pop("created", None)
    entry.pop("status", None)
    new_entry = entry
    active.append(entry)

    registry["pending"] = remaining_pending
    registry["active"] = active

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    print(f"[OK] Approved skill '{skill_name}'")
    print(f"     Moved {pending_path} -> {active_path}")
    print("     Updated agents/skills-registry.json")

    # Auto-index the newly approved skill into Chroma
    try:
        import chromadb
        client     = chromadb.PersistentClient(path=".chroma")
        collection = client.get_or_create_collection("skills")
        doc = f"{skill_name}. {new_entry['description']}. tags: {' '.join(new_entry.get('tags', []))}"
        collection.upsert(
            ids=[skill_name],
            documents=[doc],
            metadatas=[{"file": new_entry["file"], "name": skill_name}]
        )
        print(f"[OK] Indexed into Chroma automatically.")
    except Exception as e:
        print(f"[WARN] Chroma auto-index failed: {e}  run index_skills.py manually.")


if __name__ == "__main__":
    main()
