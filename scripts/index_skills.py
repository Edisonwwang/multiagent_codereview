"""
index_skills.py
Indexes all active skills from skills-registry.json into Chroma.
Run once to build the index, and again whenever skills are added manually.
New skills approved via approve_skill.py are indexed automatically.

Usage:
  python scripts/index_skills.py
"""

import json
import os
import chromadb

REGISTRY_PATH = "agents/skills-registry.json"
CHROMA_PATH   = ".chroma"

def build_document(skill):
    return f"{skill['name']}. {skill['description']}. tags: {' '.join(skill.get('tags', []))}"

def main():
    client     = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection("skills")

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    skills = registry.get("active", [])
    if not skills:
        print("[WARN] No active skills found in registry.")
        return

    ids       = [s["name"] for s in skills]
    documents = [build_document(s) for s in skills]
    metadatas = [{"file": s["file"], "name": s["name"]} for s in skills]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"[OK] Indexed {len(skills)} skills into Chroma at {CHROMA_PATH}/")
    for s in skills:
        print(f"  - {s['name']}")

if __name__ == "__main__":
    main()
