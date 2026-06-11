"""
search_skills.py
Searches skills-registry.json for skills matching a query.
Text-based for now 鈥?will be replaced with Chroma vector search in Phase 3.

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

    # Only search active skills 鈥?never suggest pending ones
    results = [
        (score(skill, args.query), skill)
        for skill in registry["active"]
    ]
    results.sort(key=lambda x: x[0], reverse=True)
    results = [(s, sk) for s, sk in results if s > 0]

    if not results:
        print(f"[NO MATCH] No active skills found for: '{args.query}'")
        print("  鈫?Consider running the skill-creator to draft a new skill.")
        return

    print(f"\nTop {min(args.top, len(results))} skill(s) for '{args.query}':\n")
    for i, (sc, skill) in enumerate(results[:args.top], 1):
        print(f"  {i}. {skill['name']}  (score: {sc})")
        print(f"     {skill['description']}")
        print(f"     File: {skill['file']}")
        print()

if __name__ == "__main__":
    main()
