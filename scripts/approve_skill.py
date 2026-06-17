"""
approve_skill.py
Moves a pending skill into the active skills folder and updates the registry.

Usage:
  python scripts/approve_skill.py --name skill-name
"""

import argparse
import os
import sys

from common import (
    CHROMA_DIR,
    PENDING_SKILLS_DIR,
    REGISTRY_PATH,
    SKILLS_DIR,
    atomic_write_json,
    display_path,
    load_json,
    normalize_skill_name,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="pending skill name without .md")
    args = parser.parse_args()

    try:
        skill_name = normalize_skill_name(args.name)
    except ValueError as e:
        parser.error(str(e))
    pending_path = PENDING_SKILLS_DIR / f"{skill_name}.md"
    active_path = SKILLS_DIR / f"{skill_name}.md"

    if not pending_path.exists():
        print(f"[ERROR] Pending skill not found: {display_path(pending_path)}", file=sys.stderr)
        sys.exit(1)

    registry = load_json(REGISTRY_PATH)

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

    if active_path.exists():
        print(f"[ERROR] Active skill file already exists: {display_path(active_path)}", file=sys.stderr)
        sys.exit(1)

    pending_file = entry.get("file")
    entry["file"] = display_path(active_path)
    entry.pop("created", None)
    entry.pop("status", None)
    new_entry = entry
    active.append(entry)

    registry["pending"] = remaining_pending
    registry["active"] = active

    os.replace(pending_path, active_path)
    try:
        atomic_write_json(REGISTRY_PATH, registry)
    except Exception:
        if active_path.exists() and not pending_path.exists():
            os.replace(active_path, pending_path)
        entry["file"] = pending_file
        raise

    print(f"[OK] Approved skill '{skill_name}'")
    print(f"     Moved {display_path(pending_path)} -> {display_path(active_path)}")
    print(f"     Updated {display_path(REGISTRY_PATH)}")

    # Auto-index the newly approved skill into Chroma
    try:
        import chromadb
        client     = chromadb.PersistentClient(path=str(CHROMA_DIR))
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
