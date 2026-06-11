"""
Shared filesystem and JSON helpers for repository scripts.
"""

import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"
OUTPUTS_DIR = ROOT / "outputs"
REVIEWS_DIR = OUTPUTS_DIR / "reviews"
SKILLS_DIR = ROOT / "skills"
PENDING_SKILLS_DIR = SKILLS_DIR / "pending"
CHROMA_DIR = ROOT / ".chroma"

SCHEDULE_PATH = AGENTS_DIR / "schedule.json"
STATE_PATH = AGENTS_DIR / "review_state.json"
REGISTRY_PATH = AGENTS_DIR / "skills-registry.json"


def repo_slug(repo):
    return repo.replace("/", "_")


def display_path(path):
    path = Path(path)
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=".tmp-",
        suffix=".json",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_text(path):
    return Path(path).read_text(encoding="utf-8")
