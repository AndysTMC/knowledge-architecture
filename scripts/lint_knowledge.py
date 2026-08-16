#!/usr/bin/env python3
"""Mechanical checks for the knowledge architecture.

Exit 1 if any error. Warnings print but do not fail unless --strict.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

KNOWN_TYPES = {
    "identity",
    "map",
    "now",
    "log",
    "decision",
    "knowledge",
    "belief",
    "source",
    "work",
    "output",
    "capture",
    "protocol",
}

ANTI_FILES = (
    "FILES.md",
    "hot-cache.md",
    "MAP.md",
    "AI_CONTEXT.md",
    "NOTES.md",
    "ACTIVE_TASK.md",
    "SCRATCHPAD.md",
)

SKIP_DIR_NAMES = {".git", "node_modules", ".venv", "venv", "__pycache__"}
SKIP_TOP_DIRS = {"tests"}  # fixtures live here; do not lint them as the project

POINTER_MAX_LINES = 15
AGENTS_MAX_LINES = 200
README_WARN_LINES = 150

DECISION_TITLE = re.compile(r"^#\s+(\d{4})\.\s+", re.MULTILINE)
DECISION_FILENAME = re.compile(r"^(\d{4})-.+\.md$")
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"```.*?```", re.DOTALL)
UPDATED = re.compile(r"^updated:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)

# --format json contract (stable for v0.1.x):
# { "ok": bool, "errors": [str], "warnings": [str], "fixed": [str] }


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def iter_files(root: Path):
    skip_tests = (root / "scripts" / "lint_knowledge.py").is_file()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        if skip_tests and rel.parts and rel.parts[0] in SKIP_TOP_DIRS:
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_count(text: str) -> int:
    return len(text.splitlines())


def frontmatter_type(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    rest = text[4:]
    end = re.search(r"^---\s*$", rest, re.MULTILINE)
    if not end:
        return None
    block = rest[: end.start()]
    m = re.search(r"^type:\s*(\S+)\s*$", block, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else None


def prose_without_fences(text: str) -> str:
    return FENCE.sub("", text)


def resolve_link(src: Path, raw: str, root: Path) -> Path | None:
    target = raw.strip()
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "irc:")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    path = Path(target)
    resolved = (src.parent / path).resolve() if not path.is_absolute() else path
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return resolved
    return resolved


def lint(root: Path, stale_days: int = 14, strict: bool = False, fix: bool = False) -> LintResult:
    root = root.resolve()
    result = LintResult()

    def err(msg: str) -> None:
        result.errors.append(msg)

    def warn(msg: str) -> None:
        if strict:
            result.errors.append(msg)
        else:
            result.warnings.append(msg)

    now = root / "docs" / "now.md"

    for path in iter_files(root):
        if path.name in ANTI_FILES:
            err(f"anti-file present: {path.relative_to(root)}")

    todo = any(p.name == "TODO.md" for p in iter_files(root))
    backlog = any(p.name == "BACKLOG.md" for p in iter_files(root))
    if todo and backlog:
        extra = " + docs/now.md" if now.is_file() else ""
        err(f"too many working memories: TODO.md + BACKLOG.md{extra}")

    tmpl = root / "docs" / "decisions" / "0000-template.md"
    if tmpl.is_file():
        err("empty ceremony: docs/decisions/0000-template.md")

    for rel in ("docs/decisions", "docs/wiki", "docs/skills"):
        d = root / rel
        if d.is_dir():
            inhabitants = [p for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep"]
            if not inhabitants:
                err(f"empty ring (birth rule): {rel}/")

    agents = root / "AGENTS.md"
    if agents.is_file():
        n = line_count(read_text(agents))
        if n > AGENTS_MAX_LINES:
            err(f"AGENTS.md is {n} lines (max {AGENTS_MAX_LINES})")
    else:
        warn("AGENTS.md missing (ok only if no agent will work here)")

    readme = root / "README.md"
    if readme.is_file() and line_count(read_text(readme)) > README_WARN_LINES:
        warn(f"README.md is {line_count(read_text(readme))} lines (door becoming a wiki)")

    for p in (
        root / "CLAUDE.md",
        root / "GEMINI.md",
        root / ".github" / "copilot-instructions.md",
    ):
        if not p.is_file():
            continue
        text = read_text(p)
        n = line_count(text)
        if n > POINTER_MAX_LINES:
            err(f"pointer too long ({n} lines): {p.relative_to(root)}")
        if "AGENTS.md" not in text:
            err(f"pointer does not mention AGENTS.md: {p.relative_to(root)}")

    if (root / "CLAUDE.md").is_file() and (root / ".claude" / "CLAUDE.md").is_file():
        err("both CLAUDE.md and .claude/CLAUDE.md exist (Claude concatenates both)")

    settings = root / ".gemini" / "settings.json"
    if settings.is_file() and (root / "GEMINI.md").is_file():
        try:
            data = json.loads(read_text(settings))
            names = data.get("context", {}).get("fileName")
            if isinstance(names, list) and "AGENTS.md" in names and "GEMINI.md" in names:
                err("Gemini would load AGENTS.md twice (settings fileName lists both and GEMINI.md exists)")
        except json.JSONDecodeError:
            warn("could not parse .gemini/settings.json")

    if now.is_file():
        text = read_text(now)
        m = UPDATED.search(text)
        if not m:
            err("docs/now.md missing updated: YYYY-MM-DD")
        else:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d").date()
            if date.today() - updated > timedelta(days=stale_days):
                msg = f"docs/now.md is stale ({updated}, >{stale_days} days)"
                if fix:
                    today = date.today().isoformat()
                    now.write_text(UPDATED.sub(f"updated: {today}", text, count=1), encoding="utf-8")
                    result.fixed.append(f"docs/now.md updated: → {today}")
                else:
                    err(msg) if strict else warn(msg)
        kind = frontmatter_type(text)
        if kind and kind != "now":
            err(f"docs/now.md type: {kind} (expected now)")

    decisions = root / "docs" / "decisions"
    ids: dict[str, Path] = {}
    if decisions.is_dir():
        for path in sorted(decisions.glob("*.md")):
            if path.name.startswith("_"):
                continue
            text = read_text(path)
            fn = DECISION_FILENAME.match(path.name)
            title = DECISION_TITLE.search(text)
            if not title:
                if fn:
                    warn(f"decision filename looks numbered but title is not '# NNNN. …': {path.name}")
                continue
            did = title.group(1)
            if did == "0000":
                err(f"decision id 0000 is reserved: {path.name}")
                continue
            if fn and fn.group(1) != did:
                err(f"decision id mismatch: file {path.name} vs title {did}")
            if did in ids:
                err(f"duplicate decision id {did}: {ids[did].name} and {path.name}")
            ids[did] = path
            status_m = re.search(r"^Status:\s*(\S+)", text, re.MULTILINE | re.IGNORECASE)
            status = (status_m.group(1).lower() if status_m else "")
            if "accepted" in status and not re.search(r"^##\s+Assumptions\b", text, re.MULTILINE):
                err(f"accepted decision missing ## Assumptions: {path.name}")

    spec = root / "docs" / "knowledge-architecture.md"
    if spec.is_file():
        head = read_text(spec)[:2000]
        if not re.search(r"\*\*Version:\*\*", head):
            warn("full spec has no Version field")
        review = re.search(r"Tool table review-by:\*\*\s*(\d{4}-\d{2}-\d{2})", head)
        if review:
            until = datetime.strptime(review.group(1), "%Y-%m-%d").date()
            if date.today() > until:
                warn(f"§18 tool table past review-by ({until})")

    for path in iter_files(root):
        if path.suffix.lower() != ".md":
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            err(f"undecodable markdown (not utf-8): {path.relative_to(root)}")
            continue
        kind = frontmatter_type(text)
        if kind and kind not in KNOWN_TYPES:
            err(f"unknown type {kind!r} in {path.relative_to(root)}")
        for raw in MD_LINK.findall(prose_without_fences(text)):
            dest = resolve_link(path, raw, root)
            if dest is None:
                continue
            if not dest.exists():
                err(f"broken link in {path.relative_to(root)}: {raw}")

    return result


def emit(result: LintResult, fmt: str) -> int:
    if fmt == "json":
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "fixed": result.fixed,
                },
                indent=2,
            )
        )
    else:
        for w in result.warnings:
            print(f"warning: {w}")
        for e in result.errors:
            print(f"error: {e}")
        for f in result.fixed:
            print(f"fixed: {f}")
        if result.errors:
            print(f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        else:
            print(f"ok ({len(result.warnings)} warning(s))")
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: parent of scripts/)")
    parser.add_argument("--stale-days", type=int, default=14)
    parser.add_argument("--strict", action="store_true", help="treat warnings (including stale now.md) as errors")
    parser.add_argument("--fix", action="store_true", help="refresh docs/now.md updated: to today")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="text or json. JSON shape (v0.1.x): {ok, errors, warnings, fixed}",
    )
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "check":
        argv = argv[1:]
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else repo_root()
    return emit(lint(root, args.stale_days, args.strict, args.fix), args.format)


if __name__ == "__main__":
    sys.exit(main())
