import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import common
import create_skill
import update_schedule


class CommonTests(unittest.TestCase):
    def test_atomic_write_json_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"

            common.atomic_write_json(path, {"ok": True})

            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True})


class UpdateScheduleTests(unittest.TestCase):
    def test_unknown_repo_exits_without_mutating_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            schedule_path = tmp_path / "schedule.json"
            state_path = tmp_path / "review_state.json"
            schedule = {
                "tasks": [
                    {
                        "name": "Review Latest PR",
                        "repo": "owner/repo",
                        "cadence_days": 1,
                        "last_run": "2026-06-01",
                    }
                ]
            }
            state = {
                "repos": [
                    {
                        "repo": "owner/repo",
                        "last_pr_reviewed": 1,
                        "last_run": "2026-06-01",
                        "status": "reviewed",
                    }
                ],
                "review_history": [],
            }
            schedule_path.write_text(json.dumps(schedule), encoding="utf-8")
            state_path.write_text(json.dumps(state), encoding="utf-8")

            with patch.object(update_schedule, "SCHEDULE_PATH", schedule_path), patch.object(
                update_schedule, "STATE_PATH", state_path
            ), patch.object(
                sys,
                "argv",
                [
                    "update_schedule.py",
                    "--repo",
                    "owner/missing",
                    "--pr",
                    "2",
                    "--status",
                    "reviewed",
                ],
            ):
                with self.assertRaises(SystemExit) as raised:
                    update_schedule.main()

            self.assertEqual(raised.exception.code, 1)
            self.assertEqual(json.loads(schedule_path.read_text(encoding="utf-8")), schedule)
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), state)


class CreateSkillTests(unittest.TestCase):
    def test_create_skill_uses_clean_template_and_relative_registry_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pending_dir = tmp_path / "skills" / "pending"
            registry_path = tmp_path / "agents" / "skills-registry.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text(
                json.dumps({"active": [], "pending": []}),
                encoding="utf-8",
            )

            with patch.object(create_skill, "PENDING_SKILLS_DIR", pending_dir), patch.object(
                create_skill, "REGISTRY_PATH", registry_path
            ), patch.object(create_skill, "display_path", lambda path: Path(path).as_posix()), patch.object(
                sys,
                "argv",
                [
                    "create_skill.py",
                    "--name",
                    "Review Stuff",
                    "--description",
                    "Reviews stuff",
                    "--tags",
                    "review,stuff",
                ],
            ):
                create_skill.main()

            skill_path = pending_dir / "review-stuff.md"
            content = skill_path.read_text(encoding="utf-8")
            registry = json.loads(registry_path.read_text(encoding="utf-8"))

            self.assertIn("- {input_1} - describe what this skill needs to run", content)
            self.assertNotIn("\u9225", content)
            self.assertNotIn("\u95b3", content)
            self.assertEqual(registry["pending"][0]["name"], "review-stuff")
            self.assertEqual(registry["pending"][0]["file"], skill_path.as_posix())


if __name__ == "__main__":
    unittest.main()
