"""
search_skills.py
Semantic skill search using Chroma vector DB.
Falls back to text search if Chroma index does not exist yet.

Usage:
  python scripts/search_skills.py --query "review docker files"
  python scripts/search_skills.py --query "check dependencies" --top 3
"""

import argparse
import json
import os

REGISTRY_PATH = "agents/skills-registry.json"
CHROMA_PATH   = ".chroma"

def text_search(skills, query, top):
    """Fallback: simple keyword match."""
    q_words = query.lower().split()
    def score(skill):
        text = skill["name"] + " " + skill["description"] + " " + " ".join(skill.get("tags", []))
        return sum(1 for w in q_words if w in text.lower())
    results = sorted(skills, key=score, reverse=True)
    results = [s for s in results if score(s) > 0]
    return results[:top]

def chroma_search(query, top):
    """Semantic search via Chroma."""
    import chromadb
    client     = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection("skills")
    if collection.count() == 0:
        return None
    results = collection.query(query_texts=[query], n_results=min(top, collection.count()))
    skills  = []
    for i, meta in enumerate(results["metadatas"][0]):
        skills.append({
            "name":     meta["name"],
            "file":     meta["file"],
            "distance": results["distances"][0][i],
        })
    return skills

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--top",   type=int, default=3)
    args = parser.parse_args()

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    active = registry.get("active", [])

    # Try Chroma first
    use_chroma = os.path.exists(CHROMA_PATH)
    results    = None

    if use_chroma:
        try:
            results = chroma_search(args.query, args.top)
        except Exception as e:
            print(f"[WARN] Chroma search failed ({e}), falling back to text search.")

    if not results:
        # Fallback to text search
        matched = text_search(active, args.query, args.top)
        if not matched:
            print(f"[NO MATCH] No skills found for: '{args.query}'")
            print("  -> Consider running skill-creator to draft a new skill.")
            return
        print(f"\n[text search] Top {len(matched)} result(s) for '{args.query}':\n")
        for s in matched:
            skill_meta = next((x for x in active if x["name"] == s["name"]), s)
            print(f"  - {s['name']}")
            print(f"    {skill_meta.get('description', '')}")
            print(f"    File: {skill_meta.get('file', s.get('file', ''))}\n")
        return

    # Chroma results
    print(f"\n[semantic search] Top {len(results)} result(s) for '{args.query}':\n")
    for r in results:
        skill_meta = next((x for x in active if x["name"] == r["name"]), {})
        print(f"  - {r['name']}  (distance: {r['distance']:.4f})")
        print(f"    {skill_meta.get('description', '')}")
        print(f"    File: {r['file']}\n")

if __name__ == "__main__":
    main()
