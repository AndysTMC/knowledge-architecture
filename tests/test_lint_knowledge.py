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


if __name__ == "__main__":
    unittest.main()
