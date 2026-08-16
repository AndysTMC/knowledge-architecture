#!/usr/bin/env python3
"""Tests for scripts/lint_knowledge.py using fixture trees and temp repos."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lint_knowledge.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(ROOT / "scripts"))
import lint_knowledge as lk  # noqa: E402


def write_tree(base: Path, files: dict[str, str | bytes]) -> Path:
    for rel, body in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body, encoding="utf-8")
    return base


class FixtureTests(unittest.TestCase):
    def test_clean_fixture_ok(self) -> None:
        result = lk.lint(FIXTURES / "clean", stale_days=3650)
        self.assertEqual(result.errors, [], result.errors)
        self.assertTrue(result.ok)

    def test_this_repo_ok(self) -> None:
        result = lk.lint(ROOT, stale_days=14)
        self.assertEqual(result.errors, [], result.errors)


class ViolationTests(unittest.TestCase):
    def test_nested_anti_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "README.md": "# x\n",
                    "src/pkg/FILES.md": "nope\n",
                },
            )
            result = lk.lint(root)
            self.assertFalse(result.ok)
            self.assertTrue(any("anti-file" in e and "FILES.md" in e for e in result.errors))

    def test_empty_ring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "decisions").mkdir(parents=True)
            (root / "README.md").write_text("# x\n", encoding="utf-8")
            result = lk.lint(root)
            self.assertTrue(any("empty ring" in e for e in result.errors))

    def test_duplicate_decision_ids(self) -> None:
        body = "# 0001. Same\n\nStatus: proposed\n\n## Assumptions\n\n- a\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-a.md": body,
                    "docs/decisions/0001-b.md": body,
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("duplicate decision id 0001" in e for e in result.errors))

    def test_year_heading_is_not_a_decision_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "README.md": "# 2024 Was Fine\n",
                    "docs/notes.md": "# 2024 Retrospective\n",
                    "docs/decisions/0007-real.md": (
                        "# 0007. Use Postgres\n\nStatus: accepted\n\n## Assumptions\n\n- a\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertFalse(any("2024" in e and "duplicate" in e for e in result.errors))
            self.assertFalse(any("decision id 2024" in e for e in result.errors))

    def test_accepted_missing_assumptions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/decisions/0001-x.md": "# 0001. X\n\nStatus: accepted\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("Assumptions" in e for e in result.errors))

    def test_broken_relative_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/identity.md": "See [missing](nope.md)\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("broken link" in e for e in result.errors))

    def test_http_link_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"README.md": "See [x](https://example.com/nope)\n"},
            )
            result = lk.lint(root)
            self.assertFalse(any("broken link" in e for e in result.errors))

    def test_dual_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "CLAUDE.md": "@AGENTS.md\n",
                    ".claude/CLAUDE.md": "@AGENTS.md\n",
                    "AGENTS.md": "# p\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("both CLAUDE.md" in e for e in result.errors))

    def test_undecodable_markdown_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"docs/bad.md": b"\xff\xfe not utf-8"})
            result = lk.lint(root)
            self.assertTrue(any("undecodable" in e for e in result.errors))

    def test_unknown_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/x.md": "---\ntype: banana\n---\n\n# X\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("unknown type" in e for e in result.errors))

    def test_four_working_memories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "TODO.md": "- a\n",
                    "BACKLOG.md": "- b\n",
                    "docs/now.md": "---\ntype: now\nupdated: 2099-01-01\n---\n# Now\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("TODO.md + BACKLOG.md" in e for e in result.errors))

    def test_stale_now_is_warning_unless_strict(self) -> None:
        old = (date.today() - timedelta(days=30)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/now.md": f"---\ntype: now\nupdated: {old}\n---\n# Now\n"},
            )
            loose = lk.lint(root, stale_days=14, strict=False)
            self.assertTrue(loose.ok)
            self.assertTrue(any("stale" in w for w in loose.warnings))
            hard = lk.lint(root, stale_days=14, strict=True)
            self.assertFalse(hard.ok)
            self.assertTrue(any("stale" in e for e in hard.errors))

    def test_fix_refreshes_now_date(self) -> None:
        old = (date.today() - timedelta(days=30)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "AGENTS.md": "# p\n",
                    "docs/now.md": f"---\ntype: now\nupdated: {old}\n---\n# Now\n",
                },
            )
            result = lk.lint(root, stale_days=14, strict=True, fix=True)
            self.assertTrue(result.ok)
            self.assertTrue(result.fixed)
            text = (root / "docs" / "now.md").read_text(encoding="utf-8")
            self.assertIn(f"updated: {date.today().isoformat()}", text)


class SizeAndPointerTests(unittest.TestCase):
    def test_agents_over_line_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"AGENTS.md": "# p\n" + ("x\n" * 200)})
            result = lk.lint(root)
            self.assertTrue(any("AGENTS.md is" in e and "max 200" in e for e in result.errors))

    def test_readme_over_line_limit_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"README.md": "# r\n" + ("x\n" * 160)})
            loose = lk.lint(root, strict=False)
            self.assertTrue(loose.ok)
            self.assertTrue(any("README.md is" in w for w in loose.warnings))
            hard = lk.lint(root, strict=True)
            self.assertFalse(hard.ok)
            self.assertTrue(any("README.md is" in e for e in hard.errors))

    def test_pointer_too_long(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "AGENTS.md": "# p\n",
                    "CLAUDE.md": "@AGENTS.md\n" + ("note\n" * 20),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("pointer too long" in e and "CLAUDE.md" in e for e in result.errors))

    def test_todo_backlog_without_now(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"TODO.md": "- a\n", "BACKLOG.md": "- b\n"})
            result = lk.lint(root)
            self.assertTrue(any("TODO.md + BACKLOG.md" in e for e in result.errors))

    def test_reserved_decision_id_0000(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/decisions/0000-oops.md": "# 0000. Not A Template\n\nStatus: proposed\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("0000" in e for e in result.errors))

    def test_links_inside_fences_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"README.md": "```md\nSee [x](does-not-exist.md)\n```\n"},
            )
            result = lk.lint(root)
            self.assertFalse(any("broken link" in e for e in result.errors))

    def test_pointer_must_mention_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "AGENTS.md": "# p\n",
                    "GEMINI.md": "Just do the right thing.\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("does not mention AGENTS.md" in e for e in result.errors))


class CliTests(unittest.TestCase):
    def test_json_format(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(FIXTURES / "clean"), "--format", "json", "--stale-days", "3650"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])

    def test_warnings_only_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"README.md": "# r\n" + ("x\n" * 160)})
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_cli_stale_days(self) -> None:
        old = (date.today() - timedelta(days=3)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "AGENTS.md": "# p\n",
                    "docs/now.md": f"---\ntype: now\nupdated: {old}\n---\n# Now\n",
                },
            )
            loose = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--stale-days", "14", "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(loose.returncode, 0, loose.stdout)
            tight = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--stale-days",
                    "1",
                    "--strict",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(tight.returncode, 0)
            self.assertTrue(any("stale" in e for e in json.loads(tight.stdout)["errors"]))

    def test_cli_fails_on_anti_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_tree(Path(tmp), {"FILES.md": "x\n"})
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", tmp, "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
