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


class FenceAndAnchorTests(unittest.TestCase):
    def test_tilde_fences_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"README.md": "~~~\nSee [x](does-not-exist.md)\n~~~\n"},
            )
            result = lk.lint(root)
            self.assertFalse(any("broken link" in e for e in result.errors))

    def test_nested_shorter_fence_does_not_close_outer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"README.md": "````md\n```\nSee [x](does-not-exist.md)\n```\n````\n"},
            )
            result = lk.lint(root)
            self.assertFalse(any("broken link" in e for e in result.errors))

    def test_link_after_nested_fence_is_still_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"README.md": "````md\n```\nok\n```\n````\n\nSee [x](does-not-exist.md)\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("broken link" in e for e in result.errors))

    def test_missing_anchor_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/a.md": "# Hello\n\nSee [nope](b.md#missing-heading)\n",
                    "docs/b.md": "# Present\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("missing anchor" in e for e in result.errors))

    def test_valid_anchor_and_same_file_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/a.md": "# Hello There\n\nSee [self](#hello-there) and [b](b.md#present)\n",
                    "docs/b.md": "# Present\n",
                },
            )
            result = lk.lint(root)
            self.assertFalse(any("missing anchor" in e or "broken link" in e for e in result.errors))


class KindAndDecisionGraphTests(unittest.TestCase):
    def test_missing_type_on_conventional_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"docs/identity.md": "# Who\n"})
            result = lk.lint(root)
            self.assertTrue(any("missing type: identity" in e for e in result.errors))

    def test_wrong_type_on_conventional_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/now.md": "---\ntype: belief\nupdated: 2099-01-01\n---\n# Now\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("expected now" in e for e in result.errors))

    def test_index_must_list_each_decision(self) -> None:
        body = (
            "---\ntype: decision\n---\n\n# 0001. X\n\nStatus: accepted\n\n## Assumptions\n\n- a\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-x.md": body,
                    "docs/decisions/_index.md": "# Decisions\n\n| ID | Title | Status |\n|---|---|---|\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("_index.md missing 0001" in e for e in result.errors))

    def test_index_status_must_match_file(self) -> None:
        body = (
            "---\ntype: decision\n---\n\n# 0001. X\n\nStatus: accepted\n\n## Assumptions\n\n- a\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-x.md": body,
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | X | proposed | — | — |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("status for 0001" in e for e in result.errors))

    def test_supersede_must_be_bidirectional(self) -> None:
        older = (
            "---\ntype: decision\n---\n\n# 0001. Old\n\n"
            "Status: superseded by 0002\nSupersedes: —\nSuperseded-by: —\n"
        )
        newer = (
            "---\ntype: decision\n---\n\n# 0002. New\n\n"
            "Status: accepted\nSupersedes: 0001\nSuperseded-by: —\n\n## Assumptions\n\n- a\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-old.md": older,
                    "docs/decisions/0002-new.md": newer,
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | Old | superseded | — | — |\n"
                        "| 0002 | New | accepted | — | 0001 |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("does not list Superseded-by: 0002" in e for e in result.errors))

    def test_reserved_template_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"docs/decisions/0000-template.md": "# template\n"},
            )
            result = lk.lint(root)
            self.assertTrue(any("0000-template.md" in e for e in result.errors))

    def test_index_date_must_match_file(self) -> None:
        body = (
            "---\ntype: decision\n---\n\n# 0001. X\n\n"
            "Status: accepted\nDate: 2026-08-17\nSupersedes: —\n\n## Assumptions\n\n- a\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-x.md": body,
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | X | accepted | 2020-01-01 | — |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("date for 0001" in e for e in result.errors))

    def test_index_supersedes_must_match_file(self) -> None:
        older = (
            "---\ntype: decision\n---\n\n# 0001. Old\n\n"
            "Status: superseded by 0002\nDate: 2026-08-01\n"
            "Supersedes: —\nSuperseded-by: 0002\n"
        )
        newer = (
            "---\ntype: decision\n---\n\n# 0002. New\n\n"
            "Status: accepted\nDate: 2026-08-17\n"
            "Supersedes: 0001\nSuperseded-by: —\n\n## Assumptions\n\n- a\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-old.md": older,
                    "docs/decisions/0002-new.md": newer,
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | Old | superseded | 2026-08-01 | — |\n"
                        "| 0002 | New | accepted | 2026-08-17 | — |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("supersedes for 0002" in e for e in result.errors))

    def test_wiki_page_requires_source_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/wiki/SCHEMA.md": "# schema\n",
                    "docs/wiki/pages/entity.md": "---\ntype: knowledge\n---\n\n# Entity\n\nA claim.\n",
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("wiki page missing source pointer" in e for e in result.errors))

    def test_wiki_page_with_raw_link_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/wiki/SCHEMA.md": "# schema\n",
                    "docs/wiki/raw/paper.md": "---\ntype: source\n---\n\n# Paper\n",
                    "docs/wiki/pages/entity.md": (
                        "---\ntype: knowledge\nsource: ../raw/paper.md\n---\n\n"
                        "# Entity\n\nFrom [paper](../raw/paper.md).\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertFalse(any("source pointer" in e for e in result.errors))


class InitTests(unittest.TestCase):
    def test_init_scaffolds_kernel_not_rings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--init",
                    "--test",
                    "pytest",
                    "--install",
                    "pip install -e .",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"], payload)
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertTrue((root / "CLAUDE.md").is_file())
            self.assertTrue((root / ".github" / "copilot-instructions.md").is_file())
            self.assertTrue((root / "scripts" / "lint_knowledge.py").is_file())
            self.assertFalse((root / "docs" / "decisions").exists())
            self.assertFalse((root / "docs" / "wiki").exists())
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("pytest", agents)
            self.assertNotIn("___", agents)

    def test_init_refuses_without_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", tmp, "--init", "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertTrue(any("cannot infer" in e for e in payload["errors"]))

    def test_init_does_not_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"AGENTS.md": "# keep me\n"})
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--init",
                    "--test",
                    "go test ./...",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), "# keep me\n")
            payload = json.loads(proc.stdout)
            self.assertTrue(any("skipped existing AGENTS.md" in w for w in payload["warnings"]))

    def test_init_infers_npm_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {"package.json": '{"scripts": {"test": "vitest", "lint": "eslint ."}}\n'},
            )
            result = lk.init_kernel(root)
            self.assertTrue(result.ok, result.errors)
            text = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("npm test", text)
            self.assertIn("npm run lint", text)


class VersionAndPromotionTests(unittest.TestCase):
    def test_cli_version(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--version", "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["version"], lk.VERSION)
        self.assertIn("lint_knowledge.py", payload["pin"])

    def test_cli_version_text(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), lk.VERSION)

    def test_promotion_flip_is_an_error(self) -> None:
        diff = (
            "--- a/docs/decisions/0003-x.md\n"
            "+++ b/docs/decisions/0003-x.md\n"
            "@@ -1,4 +1,4 @@\n"
            "-Status: proposed\n"
            "+Status: accepted\n"
        )
        hits = lk.promotions_in_diff(diff)
        self.assertTrue(any("proposed → accepted" in h for h in hits))

    def test_new_accepted_decision_is_an_error(self) -> None:
        diff = (
            "--- /dev/null\n"
            "+++ b/docs/decisions/0004-y.md\n"
            "@@ -0,0 +1,3 @@\n"
            "+# 0004. Y\n"
            "+Status: accepted\n"
        )
        hits = lk.promotions_in_diff(diff)
        self.assertTrue(any("landed as accepted" in h for h in hits))

    def test_promotion_diff_fails_without_allow(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as handle:
            handle.write(
                "--- a/docs/decisions/0003-x.md\n"
                "+++ b/docs/decisions/0003-x.md\n"
                "@@ -1 +1 @@\n"
                "-Status: proposed\n"
                "+Status: accepted\n"
            )
            path = handle.name
        try:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--promotion-diff", path, "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])

    def test_allow_promotion_exits_zero(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as handle:
            handle.write(
                "--- a/docs/decisions/0003-x.md\n"
                "+++ b/docs/decisions/0003-x.md\n"
                "@@ -1 +1 @@\n"
                "-Status: proposed\n"
                "+Status: accepted\n"
            )
            path = handle.name
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--promotion-diff",
                    path,
                    "--allow-promotion",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["warnings"])

    def test_promotion_uppercase_status(self) -> None:
        diff = (
            "--- a/docs/decisions/0003-x.md\n"
            "+++ b/docs/decisions/0003-x.md\n"
            "@@ -1 +1 @@\n"
            "-STATUS: proposed\n"
            "+STATUS: accepted\n"
        )
        hits = lk.promotions_in_diff(diff)
        self.assertTrue(any("proposed → accepted" in h for h in hits), hits)

    def test_promotion_space_before_colon(self) -> None:
        diff = (
            "--- a/docs/decisions/0003-x.md\n"
            "+++ b/docs/decisions/0003-x.md\n"
            "@@ -1 +1 @@\n"
            "-Status : proposed\n"
            "+Status : accepted\n"
        )
        hits = lk.promotions_in_diff(diff)
        self.assertTrue(any("proposed → accepted" in h for h in hits), hits)

    def test_promotion_flip_in_renamed_file(self) -> None:
        diff = (
            "diff --git a/docs/decisions/0003-old.md b/docs/decisions/0003-new.md\n"
            "similarity index 80%\n"
            "rename from docs/decisions/0003-old.md\n"
            "rename to docs/decisions/0003-new.md\n"
            "--- a/docs/decisions/0003-old.md\n"
            "+++ b/docs/decisions/0003-new.md\n"
            "@@ -1,4 +1,4 @@\n"
            "-Status: proposed\n"
            "+Status: accepted\n"
        )
        hits = lk.promotions_in_diff(diff)
        self.assertTrue(any("0003-new.md" in h and "proposed → accepted" in h for h in hits), hits)

    def test_tree_parses_odd_status_spellings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-x.md": (
                        "---\ntype: decision\n---\n\n# 0001. X\n\n"
                        "STATUS : accepted\n\n## Assumptions\n\n- a\n"
                    ),
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | X | accepted | — | — |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertFalse(any("missing Status" in e for e in result.errors), result.errors)
            self.assertFalse(any("no parseable Status" in e for e in result.errors), result.errors)

    def test_delete_accepted_is_an_error(self) -> None:
        diff = (
            "diff --git a/docs/decisions/0002-mit-license.md b/docs/decisions/0002-mit-license.md\n"
            "deleted file mode 100644\n"
            "--- a/docs/decisions/0002-mit-license.md\n"
            "+++ /dev/null\n"
            "@@ -1,4 +0,0 @@\n"
            "-# 0002. License\n"
            "-Status: accepted\n"
        )
        hits = lk.deletions_in_diff(diff)
        self.assertTrue(any("deleted accepted decision" in h for h in hits), hits)
        self.assertEqual(lk.promotions_in_diff(diff), [])

    def test_delete_superseded_is_an_error(self) -> None:
        diff = (
            "--- a/docs/decisions/0001-old.md\n"
            "+++ /dev/null\n"
            "@@ -1 +0,0 @@\n"
            "-Status: superseded\n"
        )
        hits = lk.deletions_in_diff(diff)
        self.assertTrue(any("deleted superseded decision" in h for h in hits), hits)

    def test_delete_proposed_is_allowed(self) -> None:
        diff = (
            "--- a/docs/decisions/0009-draft.md\n"
            "+++ /dev/null\n"
            "@@ -1 +0,0 @@\n"
            "-Status: proposed\n"
        )
        self.assertEqual(lk.deletions_in_diff(diff), [])
        self.assertEqual(lk.promotions_in_diff(diff), [])

    def test_delete_accepted_odd_spelling(self) -> None:
        diff = (
            "--- a/docs/decisions/0002-x.md\n"
            "+++ /dev/null\n"
            "@@ -1 +0,0 @@\n"
            "-STATUS : accepted\n"
        )
        hits = lk.deletions_in_diff(diff)
        self.assertTrue(any("deleted accepted decision" in h for h in hits), hits)

    def test_rename_accepted_out_of_ring(self) -> None:
        diff = (
            "diff --git a/docs/decisions/0002-x.md b/docs/archive/0002-x.md\n"
            "similarity index 100%\n"
            "rename from docs/decisions/0002-x.md\n"
            "rename to docs/archive/0002-x.md\n"
        )
        hits = lk.deletions_in_diff(diff)
        self.assertTrue(any("0002-x.md" in h and "deleted" in h for h in hits), hits)

    def test_allow_deletion_exits_zero(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as handle:
            handle.write(
                "--- a/docs/decisions/0002-x.md\n"
                "+++ /dev/null\n"
                "@@ -1 +0,0 @@\n"
                "-Status: accepted\n"
            )
            path = handle.name
        try:
            blocked = subprocess.run(
                [sys.executable, str(SCRIPT), "--promotion-diff", path, "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
            allowed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--promotion-diff",
                    path,
                    "--allow-deletion",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            promo_only = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--promotion-diff",
                    path,
                    "--allow-promotion",
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertEqual(allowed.returncode, 0, allowed.stdout)
        self.assertTrue(json.loads(allowed.stdout)["ok"])
        self.assertNotEqual(promo_only.returncode, 0)

    def test_missing_status_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(
                Path(tmp),
                {
                    "docs/decisions/0001-x.md": "---\ntype: decision\n---\n\n# 0001. X\n\nNo status.\n",
                    "docs/decisions/_index.md": (
                        "| ID | Title | Status | Date | Supersedes |\n"
                        "|---|---|---|---|---|\n"
                        "| 0001 | X | accepted | — | — |\n"
                    ),
                },
            )
            result = lk.lint(root)
            self.assertTrue(any("missing Status" in e for e in result.errors), result.errors)
            self.assertTrue(any("no parseable Status" in e for e in result.errors), result.errors)



class ReviewRegressionTests(unittest.TestCase):
    def cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd,
                              capture_output=True, text=True, check=False)

    def test_downloaded_bootstrap_default_root_and_force_preserves_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            root.mkdir()
            bootstrap = root / "lint_knowledge.py"
            bootstrap.write_text(SCRIPT.read_text())
            (root / "README.md").write_text("# Valuable quickstart\n")
            proc = subprocess.run([sys.executable, str(bootstrap), "--init", "--test", "true"],
                                  cwd=parent, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse((parent / "AGENTS.md").exists())
            installed = root / "scripts" / "lint_knowledge.py"
            self.assertTrue(installed.is_file())
            proc = subprocess.run([sys.executable, str(installed), "--init", "--force", "--test", "true"],
                                  cwd=parent, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual((root / "README.md").read_text(), "# Valuable quickstart\n")

    def test_no_compat_and_conflicting_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.cli("--root", tmp, "--init", "--test", "true", "--no-compat")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse((Path(tmp) / "CLAUDE.md").exists())
            result = self.cli("--root", tmp, "--init", "--version", "--format", "json")
            self.assertFalse(json.loads(result.stdout)["ok"])

    def test_traversal_prunes_dependencies_and_only_marked_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {
                "scripts/lint_knowledge.py": "", "tests/guide.md": "# Test guide\n",
                "tests/fixtures/.knowledge-fixtures": "", "tests/fixtures/FILES.md": "",
                "node_modules/pkg/FILES.md": "", "dist/FILES.md": "",
            })
            files = {p.relative_to(root).as_posix() for p in lk.iter_files(root)}
            self.assertIn("tests/guide.md", files)
            self.assertFalse(any(p.endswith("FILES.md") for p in files))
            (root / "tests" / "FILES.md").write_text("")
            self.assertTrue(any("tests/FILES.md" in e for e in lk.lint(root).errors))

    def test_malformed_input_returns_findings_not_tracebacks(self):
        for files in (
            {"AGENTS.md": b"\xff"}, {"README.md": b"\xff"},
            {"docs/now.md": "---\ntype: now\nupdated: 2026-99-99\n---\n"},
            {".gemini/settings.json": "[]", "GEMINI.md": "@AGENTS.md\n"},
            {".gemini/settings.json": '{"context": "wrong"}', "GEMINI.md": "@AGENTS.md\n"},
        ):
            with self.subTest(files=files), tempfile.TemporaryDirectory() as tmp:
                root = write_tree(Path(tmp), files)
                proc = self.cli("--root", str(root), "--strict", "--format", "json")
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertFalse(json.loads(proc.stdout)["ok"])
                self.assertNotIn("Traceback", proc.stderr)

    def test_markdown_destinations_and_phantom_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {
                "AGENTS.md": "# p\n",
                "README.md": '# R\n[x](docs/a%20b.md "title")\n![image](pic.png)\n'
                             '[root](/docs/a%20b.md#real)\n[ref][one]\n[one]: docs/a%20b.md\n'
                             '`[example](missing.md)`\n[tel](tel:123)\n[x](//example.com/x)\n'
                             '[paren](docs/a(b).md)\n',
                "docs/a b.md": "# Real ##\n```sh\n# Imaginary\n```\n",
                "docs/a(b).md": "# P\n", "pic.png": b"image",
            })
            self.assertEqual(lk.lint(root).errors, [])
            with (root / "README.md").open("a") as handle:
                handle.write("[bad](docs/a%20b.md#imaginary)\n![bad](missing.png)\n")
            errors = lk.lint(root).errors
            self.assertTrue(any("missing anchor" in e for e in errors))
            self.assertTrue(any("missing.png" in e for e in errors))
        self.assertEqual(lk.github_slug("ritual + mechanics"), "ritual--mechanics")
        self.assertIn("custom", lk.heading_slugs("# Heading {#custom}\n"))
        self.assertIn("html", lk.heading_slugs('<a id="html"></a>\n'))

    def test_links_cannot_read_outside_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            (parent / "outside.md").write_text("# Outside\n")
            root = write_tree(parent / "project", {"README.md": "[escape](../outside.md#outside)\n"})
            self.assertTrue(any("escapes repository" in e for e in lk.lint(root).errors))

    def test_sources_must_be_nonempty_and_local_paths_exist(self):
        for value in ("", "[]", "null", '""', "''"):
            self.assertFalse(lk.wiki_page_has_source(f"---\ntype: knowledge\nsource: {value}\n---\n# X\n"))
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {"docs/wiki/pages/x.md":
                "---\ntype: knowledge\nsource: ../raw/missing.md\n---\n# X\n"})
            self.assertTrue(any("missing.md" in e for e in lk.lint(root).errors))

    def decision(self, did="0001", status="proposed", extra=""):
        return f"---\ntype: decision\n---\n# {did}. Choice\nStatus: {status}\n{extra}\n## Assumptions\n- A\n"

    def test_alternative_decision_paths_status_conflicts_and_unknown_status(self):
        for directory in lk.DECISION_DIRS:
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as tmp:
                root = write_tree(Path(tmp), {f"{directory}/0001-x.md": self.decision(status="banana")})
                errors = lk.lint(root).errors
                self.assertTrue(any("invalid Status" in e for e in errors))
                self.assertTrue(any("_index.md missing" in e for e in errors))
                (root / directory / "0001-x.md").write_text(self.decision(extra="status: accepted"))
                self.assertTrue(any("conflicting Status" in e for e in lk.lint(root).errors))
        self.assertFalse(lk.is_decision_diff_path("tests/fixtures/docs/decisions/0001-x.md"))

    def test_supersession_cycles_and_live_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {
                "docs/decisions/0001-a.md": self.decision("0001", "accepted", "Supersedes: 0002\nSuperseded-by: 0002"),
                "docs/decisions/0002-b.md": self.decision("0002", "accepted", "Supersedes: 0001\nSuperseded-by: 0001"),
            })
            errors = lk.lint(root).errors
            self.assertTrue(any("cycle" in e for e in errors))
            self.assertTrue(any("not marked superseded" in e for e in errors))
        self.assertEqual(lk.parse_id_list("0002 (2026-01-15)"), ["0002"])

    def test_reordered_index_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {
                "docs/decisions/0001-a.md": self.decision(),
                "docs/decisions/_index.md": "| Title | ID | Supersedes | Date | Status |\n"
                                           "|---|---|---|---|---|\n| Choice | 0001 | — | — | proposed |\n",
            })
            self.assertEqual(lk.lint(root).errors, [])

    def test_command_inference(self):
        for files, expected in (
            ({"Cargo.toml": ""}, {"test": "cargo test"}),
            ({"go.mod": ""}, {"test": "go test ./..."}),
            ({"pytest.ini": ""}, {"test": "pytest"}),
            ({"pyproject.toml": "[tool.pytest.ini_options]\n"}, {"install": "pip install -e .", "test": "pytest"}),
            ({"Makefile": "test:\n\ttrue\nlint:\n\ttrue\n"}, {"test": "make test", "lint": "make lint"}),
            ({"package.json": '{"scripts":{"test":"x"}}', "pnpm-lock.yaml": ""}, {"install": "pnpm install", "test": "pnpm test"}),
        ):
            with self.subTest(files=files), tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(lk.infer_commands(write_tree(Path(tmp), files)), expected)

    def test_plain_multifile_diff_and_header_like_content(self):
        diff = "--- a/docs/decisions/0001-x.md\n+++ /dev/null\n@@ -1 +0,0 @@\n-Status: accepted\n" \
               "--- /dev/null\n+++ b/docs/decisions/0002-y.md\n@@ -0,0 +1 @@\n+Status: proposed\n"
        self.assertEqual([e.kind for e in lk.gate_events_in_diff(diff)], ["deletion"])
        diff = "--- a/docs/decisions/0001-x.md\n+++ b/docs/decisions/0001-x.md\n@@ -1,2 +1,2 @@\n" \
               " Status: accepted\n--- misleading content\n+replacement\n"
        self.assertEqual([e.kind for e in lk.gate_events_in_diff(diff)], ["edit"])

    def test_edits_demotions_and_separate_allowance(self):
        diff = "--- a/docs/decisions/0001-x.md\n+++ b/docs/decisions/0001-x.md\n@@ -1 +1 @@\n" \
               "-Status: accepted\n+Status: proposed\n"
        self.assertEqual([e.kind for e in lk.gate_events_in_diff(diff)], ["edit"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "change.diff"
            path.write_text(diff)
            self.assertEqual(self.cli("--promotion-diff", str(path), "--allow-promotion").returncode, 1)
            self.assertEqual(self.cli("--promotion-diff", str(path), "--allow-edit").returncode, 0)
        partial = "--- a/adr/0001-x.md\n+++ b/adr/0001-x.md\n@@ -20 +20 @@\n-old\n+new\n"
        self.assertEqual([e.kind for e in lk.gate_events_in_diff(partial)], ["edit"])

    def test_real_git_diff_stale_branch_merge_checkout_and_uncommitted_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                proc = subprocess.run(["git", "-C", tmp, *args], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                return proc.stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            write_tree(root, {"README.md": "# R\n", "adr/0001-with space.md": self.decision(status="accepted")})
            git("add", ".")
            git("commit", "-m", "initial")
            git("checkout", "-b", "feature")
            (root / "README.md").write_text("# Feature\n")
            git("commit", "-am", "feature")
            git("checkout", "main")
            write_tree(root, {"adr/0002-new.md": self.decision("0002", "accepted")})
            git("add", ".")
            git("commit", "-m", "main advances")
            git("checkout", "feature")
            self.assertEqual(lk.gate_events_in_diff(lk.git_decision_diff(root, "main")), [])
            git("merge", "--no-edit", "main")
            self.assertEqual(lk.gate_events_in_diff(lk.git_decision_diff(root, "main")), [])
            with (root / "adr/0001-with space.md").open("a") as handle:
                handle.write("Changed rationale.\n")
            self.assertEqual([e.kind for e in lk.gate_events_in_diff(lk.git_decision_diff(root, "main"))], ["edit"])
            with self.assertRaises(ValueError):
                lk.git_decision_diff(root, "--output=unsafe")


class ArtifactContractTests(unittest.TestCase):
    def test_versions_and_published_pin_are_explicit(self):
        for rel in ("README.md", "docs/kernel.md", "docs/knowledge-architecture.md", "CHANGELOG.md"):
            with self.subTest(rel=rel):
                self.assertIn(lk.VERSION, (ROOT / rel).read_text())
        if ".dev" in lk.VERSION:
            self.assertNotIn(lk.VERSION, lk.PIN_URL)
        else:
            self.assertIn(f"v{lk.VERSION}/scripts/lint_knowledge.py", lk.PIN_URL)

    def test_generated_pointers_match_spec_and_init_is_strict_clean(self):
        import re
        spec = (ROOT / "docs/knowledge-architecture.md").read_text().split("### Compatibility pack", 1)[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lk.init_kernel(root, test="python3 -m unittest")
            for rel in ("CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md"):
                match = re.search(r"\*\*`" + re.escape(rel) + r"`\*\*\s+```markdown\n(.*?)```", spec, re.S)
                self.assertIsNotNone(match, rel)
                self.assertEqual((root / rel).read_text(), match.group(1))
            self.assertEqual(lk.lint(root, strict=True).errors, [])

    def test_init_preflight_rejects_escaping_symlink_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            outside = Path(tmp) / "outside.md"
            outside.write_text("preserve")
            (root / "AGENTS.md").symlink_to(outside)
            result = lk.init_kernel(root, test="true", force=True)
            self.assertFalse(result.ok)
            self.assertFalse((root / "README.md").exists())
            self.assertEqual(outside.read_text(), "preserve")

    def test_init_preflight_rejects_file_as_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {".github": "not a directory"})
            result = lk.init_kernel(root, test="true")
            self.assertFalse(result.ok)
            self.assertFalse((root / "README.md").exists())

    def test_gemini_duplicate_context_and_date_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_tree(Path(tmp), {
                "AGENTS.md": "# Protocol\n", "GEMINI.md": "@AGENTS.md\n",
                ".gemini/settings.json": '{"context":{"fileName":["AGENTS.md","GEMINI.md"]}}',
            })
            self.assertTrue(any("twice" in e for e in lk.lint(root).errors))
            (root / ".gemini/settings.json").unlink()
            write_tree(root, {"docs/now.md": "---\ntype: now\nupdated: 2020-01-01\n---\nKeep content.\n"})
            proc = subprocess.run([sys.executable, str(SCRIPT), "--root", tmp, "--touch-now", "--format", "json"],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Keep content.", (root / "docs/now.md").read_text())
            self.assertIn("content not reviewed", json.loads(proc.stdout)["fixed"][0])

    def test_binary_protected_edit_is_conservative(self):
        diff = "diff --git a/adr/0001-x.md b/adr/0001-x.md\nBinary files a/adr/0001-x.md and b/adr/0001-x.md differ\n"
        self.assertEqual([e.kind for e in lk.gate_events_in_diff(diff)], ["edit"])


if __name__ == "__main__":
    unittest.main()
