#!/usr/bin/env python3
"""Mechanical checks for the knowledge architecture.

Exit 1 if any error. Warnings print but do not fail unless --strict.

Vendored copies: this file embeds VERSION. Re-vendor from PIN_URL
(`curl -fsSL -o scripts/lint_knowledge.py <PIN_URL>`) and run --version.
There is no auto-update. A copy without a matching VERSION is stale by definition.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import unquote

VERSION = "0.1.1"
PIN_URL = (
    "https://raw.githubusercontent.com/AndysTMC/knowledge-architecture/"
    "v0.1.1/scripts/lint_knowledge.py"
)

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

# Conventional homes from the spec. Untyped files outside these paths stay a human review.
PATH_TYPE_EXACT = {
    "docs/identity.md": "identity",
    "docs/now.md": "now",
    "docs/log.md": "log",
    "docs/architecture.md": "belief",
    "docs/schema.md": "belief",
    "docs/glossary.md": "belief",
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
UPDATED = re.compile(r"^updated:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CUSTOM_ID = re.compile(r"\{#([A-Za-z0-9._:-]+)\}\s*$")
HTML_ID = re.compile(r"<(?:a|h[1-6])\s+[^>]*(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)
INDEX_ROW = re.compile(
    r"^\|\s*(\d{4})\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
)
SUP_FIELD = re.compile(r"^Supersedes:\s*(.+)\s*$", re.MULTILINE | re.IGNORECASE)
SUP_BY_FIELD = re.compile(r"^Superseded-by:\s*(.+)\s*$", re.MULTILINE | re.IGNORECASE)
STATUS_LINE = re.compile(r"^Status\s*:\s*(.+)\s*$", re.MULTILINE | re.IGNORECASE)
DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE | re.IGNORECASE)
DECISION_DIFF_PATH = re.compile(r"(?:^|/)(?:docs/)?(?:decisions|adr)/[^/]+\.md$")
STATUS_DELTA = re.compile(r"^([+-])Status\s*:\s*(.+)\s*$", re.IGNORECASE)
DIFF_GIT = re.compile(r"^diff --git a/(.+) b/(.+)$")
RENAME_FROM = re.compile(r"^rename from (.+)$")
RENAME_TO = re.compile(r"^rename to (.+)$")
NULL_PATHS = {"/dev/null", "dev/null"}
PROTECTED_STATUS = frozenset({"accepted", "superseded"})
FENCE_OPEN = re.compile(r"^([ \t]{0,3})(`{3,}|~{3,})")
BLANK_ID = re.compile(r"^(?:—|--|-|none|n/a)?$", re.IGNORECASE)
LINE_ANCHOR = re.compile(r"^L\d+(?:-L\d+)?$")

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


def expected_type(rel: Path) -> str | None:
    key = rel.as_posix()
    if key in PATH_TYPE_EXACT:
        return PATH_TYPE_EXACT[key]
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "docs" and rel.suffix.lower() == ".md":
        if parts[1] == "decisions":
            if rel.name.startswith("_"):
                return None
            return "decision"
        if parts[1] == "wiki" and len(parts) >= 4:
            if parts[2] == "raw":
                return "source"
            if parts[2] == "pages":
                return "knowledge"
        if parts[1] == "skills":
            return "work"
        if parts[1] == "capture":
            return "capture"
    return None


def prose_without_fences(text: str) -> str:
    """Drop fenced code. Nested shorter fences and ~~~ fences stay inside the opener."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = FENCE_OPEN.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        marker = m.group(2)
        ch = marker[0]
        n = len(marker)
        close = re.compile(rf"^[ \t]{{0,3}}{re.escape(ch)}{{{n},}}[ \t]*$")
        i += 1
        while i < len(lines):
            if close.match(lines[i].rstrip("\r\n")):
                i += 1
                break
            i += 1
    return "".join(out)


def github_slug(heading: str) -> str:
    # github-slugger: drop punctuation, then each whitespace becomes one hyphen.
    # Do not collapse the resulting "--" (e.g. "ritual + mechanics" → "ritual--mechanics").
    text = CUSTOM_ID.sub("", heading).strip().lower()
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s", "-", text)


def heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for line in text.splitlines():
        m = HEADING.match(line)
        if not m:
            continue
        raw = m.group(2).strip()
        custom = CUSTOM_ID.search(raw)
        slug = custom.group(1) if custom else github_slug(raw)
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        slugs.add(f"{slug}-{n}" if n else slug)
        if custom:
            slugs.add(custom.group(1))
    for m in HTML_ID.finditer(text):
        slugs.add(m.group(1))
    return slugs


def resolve_link(src: Path, raw: str, root: Path) -> tuple[Path | None, str | None]:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target:
        return None, None
    fragment: str | None = None
    if "#" in target:
        path_part, frag = target.split("#", 1)
        fragment = unquote(frag.split("?", 1)[0].strip()) or None
        target = path_part
    else:
        target = target.split("?", 1)[0]
    target = target.strip()
    if target.startswith(("http://", "https://", "mailto:", "irc:")):
        return None, None
    if not target:
        return src, fragment
    path = Path(target)
    resolved = (src.parent / path).resolve() if not path.is_absolute() else path
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return resolved, fragment
    return resolved, fragment


def parse_id_list(value: str) -> list[str]:
    value = value.strip()
    if BLANK_ID.match(value):
        return []
    return re.findall(r"\d{4}", value)


def parse_status(text: str) -> str:
    m = STATUS_LINE.search(text)
    if not m:
        return ""
    return m.group(1).strip().lower()


def status_token(status: str) -> str:
    status = status.strip().lower()
    if not status:
        return ""
    if status.startswith("superseded"):
        return "superseded"
    return re.split(r"[\s,/|]+", status, maxsplit=1)[0]


def wiki_page_has_source(text: str) -> bool:
    if text.startswith("---\n"):
        rest = text[4:]
        end = re.search(r"^---\s*$", rest, re.MULTILINE)
        if end:
            block = rest[: end.start()]
            if re.search(r"^(?:source|sources):", block, re.MULTILINE | re.IGNORECASE):
                return True
    prose = prose_without_fences(text)
    for raw in MD_LINK.findall(prose):
        dest = raw.strip()
        if dest.startswith(("http://", "https://")):
            return True
        if re.search(r"(?:^|/)raw(?:/|$)", dest) or "/wiki/raw/" in dest:
            return True
    return False


def lint(root: Path, stale_days: int = 14, strict: bool = False, fix: bool = False) -> LintResult:
    root = root.resolve()
    result = LintResult()
    files = list(iter_files(root))

    def err(msg: str) -> None:
        result.errors.append(msg)

    def warn(msg: str) -> None:
        if strict:
            result.errors.append(msg)
        else:
            result.warnings.append(msg)

    now = root / "docs" / "now.md"

    for path in files:
        if path.name in ANTI_FILES:
            err(f"anti-file present: {path.relative_to(root)}")

    names = {p.name for p in files}
    if "TODO.md" in names and "BACKLOG.md" in names:
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
            elif rel == "docs/decisions" and all(p.name.startswith("_") for p in inhabitants):
                err(f"empty ceremony: {rel}/ has only index/underscore files")

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
            listed = data.get("context", {}).get("fileName")
            if isinstance(listed, list) and "AGENTS.md" in listed and "GEMINI.md" in listed:
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
    records: dict[str, dict[str, object]] = {}
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
            status = parse_status(text)
            date_m = DATE_LINE.search(text)
            records[did] = {
                "path": path,
                "status": status,
                "date": date_m.group(1) if date_m else "",
                "supersedes": parse_id_list(SUP_FIELD.search(text).group(1) if SUP_FIELD.search(text) else ""),
                "superseded_by": parse_id_list(SUP_BY_FIELD.search(text).group(1) if SUP_BY_FIELD.search(text) else ""),
            }
            if not status_token(status):
                err(f"decision missing Status: {path.name}")
            if "accepted" in status.lower() and not re.search(r"^##\s+Assumptions\b", text, re.MULTILINE):
                err(f"accepted decision missing ## Assumptions: {path.name}")

        for did, rec in records.items():
            for other in rec["supersedes"]:  # type: ignore[union-attr]
                if other == did:
                    err(f"decision {did} supersedes itself")
                    continue
                peer = records.get(other)
                if peer is None:
                    err(f"decision {did} supersedes missing {other}")
                    continue
                if did not in peer["superseded_by"]:  # type: ignore[operator]
                    err(f"decision {did} supersedes {other}, but {other} does not list Superseded-by: {did}")
            for other in rec["superseded_by"]:  # type: ignore[union-attr]
                if other == did:
                    err(f"decision {did} superseded-by itself")
                    continue
                peer = records.get(other)
                if peer is None:
                    err(f"decision {did} superseded-by missing {other}")
                    continue
                if did not in peer["supersedes"]:  # type: ignore[operator]
                    err(f"decision {did} lists Superseded-by: {other}, but {other} does not list Supersedes: {did}")
            if status_token(str(rec["status"])) == "superseded" and not rec["superseded_by"]:
                err(f"superseded decision {did} missing Superseded-by")

        index = decisions / "_index.md"
        if ids and not index.is_file():
            err("docs/decisions/_index.md missing while decision files exist")
        elif index.is_file():
            index_rows: dict[str, tuple[str, str, str]] = {}
            for line in read_text(index).splitlines():
                row = INDEX_ROW.match(line)
                if not row:
                    continue
                index_rows[row.group(1)] = (
                    row.group(3).strip(),
                    row.group(4).strip(),
                    row.group(5).strip(),
                )
            for did in ids:
                if did not in index_rows:
                    err(f"docs/decisions/_index.md missing {did}")
            for did, (idx_status, idx_date, idx_sup) in index_rows.items():
                if did not in ids:
                    err(f"docs/decisions/_index.md lists {did} but there is no decision file")
                    continue
                rec = records[did]
                file_tok = status_token(str(rec["status"]))
                idx_tok = status_token(idx_status)
                if not file_tok and idx_tok:
                    err(
                        f"docs/decisions/_index.md status for {did} is {idx_tok!r}, file has no parseable Status:"
                    )
                elif file_tok and idx_tok and file_tok != idx_tok:
                    err(f"docs/decisions/_index.md status for {did} is {idx_tok!r}, file is {file_tok!r}")
                file_date = str(rec["date"])
                idx_date_norm = "" if BLANK_ID.match(idx_date) else idx_date
                if file_date and idx_date_norm and file_date != idx_date_norm:
                    err(
                        f"docs/decisions/_index.md date for {did} is {idx_date_norm!r}, file is {file_date!r}"
                    )
                elif file_date and not idx_date_norm:
                    err(f"docs/decisions/_index.md missing date for {did}")
                file_sup = list(rec["supersedes"])  # type: ignore[arg-type]
                idx_sup_ids = parse_id_list(idx_sup)
                if sorted(file_sup) != sorted(idx_sup_ids):
                    err(
                        f"docs/decisions/_index.md supersedes for {did} is {idx_sup_ids}, file is {file_sup}"
                    )

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

    wiki_pages = root / "docs" / "wiki" / "pages"
    if wiki_pages.is_dir():
        for path in sorted(wiki_pages.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            try:
                text = read_text(path)
            except UnicodeDecodeError:
                continue
            if not wiki_page_has_source(text):
                err(f"wiki page missing source pointer: {path.relative_to(root)}")

    slug_cache: dict[Path, set[str]] = {}
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        rel = path.relative_to(root)
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            err(f"undecodable markdown (not utf-8): {rel}")
            continue
        kind = frontmatter_type(text)
        expect = expected_type(rel)
        if expect:
            if not kind:
                err(f"missing type: {expect} in {rel}")
            elif kind != expect:
                err(f"{rel} type: {kind} (expected {expect})")
        if kind and kind not in KNOWN_TYPES:
            err(f"unknown type {kind!r} in {rel}")
        for raw in MD_LINK.findall(prose_without_fences(text)):
            dest, fragment = resolve_link(path, raw, root)
            if dest is None:
                continue
            if not dest.exists():
                err(f"broken link in {rel}: {raw}")
                continue
            if not fragment or LINE_ANCHOR.match(fragment) or not dest.is_file():
                continue
            if dest.suffix.lower() != ".md":
                continue
            if dest not in slug_cache:
                try:
                    slug_cache[dest] = heading_slugs(read_text(dest))
                except UnicodeDecodeError:
                    slug_cache[dest] = set()
            if fragment not in slug_cache[dest]:
                err(f"missing anchor in {rel}: {raw}")

    return result


def is_decision_diff_path(path: str) -> bool:
    path = path.strip()
    if path in NULL_PATHS:
        return False
    name = Path(path).name
    if name.startswith("_") or name == "0000-template.md":
        return False
    return bool(DECISION_DIFF_PATH.search(path.replace("\\", "/")))


def _diff_path(raw: str) -> str:
    raw = raw.strip().strip('"')
    if raw.startswith(("a/", "b/")):
        raw = raw[2:]
    return raw


@dataclass
class GateEvent:
    kind: str  # "promotion" | "deletion"
    message: str


def gate_events_in_diff(diff_text: str) -> list[GateEvent]:
    """Promotions onto accepted, and removals of accepted/superseded decisions."""
    events: list[GateEvent] = []
    origin = ""
    dest = ""
    removed: list[str] = []
    added: list[str] = []

    def flush() -> None:
        add_toks = [status_token(s) for s in added if status_token(s)]
        rem_toks = [status_token(s) for s in removed if status_token(s)]
        origin_dec = is_decision_diff_path(origin)
        dest_dec = is_decision_diff_path(dest)
        if origin_dec and not dest_dec:
            last = rem_toks[-1] if rem_toks else ""
            # No token (pure rename/delete hunk-less) is treated as protected:
            # false-positive needs a label; a miss would delete a constraint.
            if last in PROTECTED_STATUS or not last:
                label = last or "protected"
                events.append(GateEvent("deletion", f"{origin}: deleted {label} decision"))
            return
        if dest_dec and "accepted" in add_toks and "accepted" not in rem_toks:
            if rem_toks:
                events.append(GateEvent("promotion", f"{dest}: Status {rem_toks[0]} → accepted"))
            else:
                events.append(GateEvent("promotion", f"{dest}: new decision landed as accepted"))

    def start_file(src: str, dst: str) -> None:
        nonlocal origin, dest, removed, added
        flush()
        origin, dest = src, dst
        removed, added = [], []

    for line in diff_text.splitlines():
        git = DIFF_GIT.match(line)
        if git:
            start_file(git.group(1), git.group(2))
            continue
        renamed_from = RENAME_FROM.match(line)
        if renamed_from:
            origin = renamed_from.group(1).strip()
            continue
        renamed_to = RENAME_TO.match(line)
        if renamed_to:
            dest = renamed_to.group(1).strip()
            continue
        if line.startswith("--- "):
            origin = _diff_path(line[4:])
            continue
        if line.startswith("+++ "):
            dest = _diff_path(line[4:])
            continue
        m = STATUS_DELTA.match(line)
        if not m:
            continue
        if m.group(1) == "-":
            removed.append(m.group(2))
        else:
            added.append(m.group(2))
    flush()
    return events


def promotions_in_diff(diff_text: str) -> list[str]:
    return [e.message for e in gate_events_in_diff(diff_text) if e.kind == "promotion"]


def deletions_in_diff(diff_text: str) -> list[str]:
    return [e.message for e in gate_events_in_diff(diff_text) if e.kind == "deletion"]


def git_decision_diff(root: Path, base: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), "diff", base, "--", "."],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git diff {base} failed")
    return proc.stdout


def infer_commands(root: Path) -> dict[str, str]:
    cmds: dict[str, str] = {}
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            scripts = (json.loads(read_text(pkg)).get("scripts") or {})
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            scripts = {}
        cmds.setdefault("install", "npm install")
        if "test" in scripts:
            cmds.setdefault("test", "npm test")
        if "lint" in scripts:
            cmds.setdefault("lint", "npm run lint")
        if "dev" in scripts:
            cmds.setdefault("dev", "npm run dev")
        elif "start" in scripts:
            cmds.setdefault("dev", "npm start")
    if (root / "Cargo.toml").is_file():
        cmds.setdefault("test", "cargo test")
    if (root / "go.mod").is_file():
        cmds.setdefault("test", "go test ./...")
    pyproject = root / "pyproject.toml"
    setup = root / "setup.py"
    if pyproject.is_file() or setup.is_file() or (root / "pytest.ini").is_file():
        cmds.setdefault("install", "pip install -e .")
        blob = ""
        if pyproject.is_file():
            try:
                blob = read_text(pyproject)
            except (OSError, UnicodeDecodeError):
                blob = ""
        if "pytest" in blob or (root / "pytest.ini").is_file():
            cmds.setdefault("test", "pytest")
        else:
            cmds.setdefault("test", "python3 -m unittest")
    makefile = root / "Makefile"
    if makefile.is_file():
        try:
            mk = read_text(makefile)
        except (OSError, UnicodeDecodeError):
            mk = ""
        if re.search(r"^test:", mk, re.MULTILINE):
            cmds.setdefault("test", "make test")
        if re.search(r"^lint:", mk, re.MULTILINE):
            cmds.setdefault("lint", "make lint")
    return cmds


def render_agents(commands: dict[str, str], routes: list[tuple[str, str]]) -> str:
    labels = (("install", "Install"), ("dev", "Dev"), ("test", "Test"), ("lint", "Lint / format"))
    cmd_lines = [f"- {label}: `{commands[key]}`" for key, label in labels if commands.get(key)]
    rows = "\n".join(f"| {need} | {path} |" for need, path in routes)
    return (
        "# Agent protocol\n\n"
        "## Commands\n\n"
        + "\n".join(cmd_lines)
        + "\n\n"
        "## Hard rules\n\n"
        "- Do not add a dependency, edit generated code, or change a migration without an explicit ask.\n"
        "- Do not commit secrets, credentials, or `.env` values.\n"
        "- Minimal diffs. Touch only what the task requires.\n"
        "- For work that will edit more than two files, write `PLAN.md` first.\n"
        "- Run the targeted test before calling the task done.\n"
        "- Do not silently flip a draft decision to accepted.\n\n"
        "## Authority\n\n"
        "- Level 0 (not facts): `PLAN.md`, chat\n"
        "- Level 2 (constraints): accepted files in `docs/decisions/` when that ring exists\n"
        "- Level 3 (prefer over prose): generated schemas and types\n"
        "- Level 4 (do not edit unless asked): this file, `docs/identity.md`, `LICENSE`\n\n"
        "## Write permissions\n\n"
        "- `PLAN.md`, capture: write.\n"
        "- Proposed decisions: create, leave status `proposed`.\n"
        "- Accepted decisions, architecture, `docs/now.md`: propose a patch. Do not apply silently.\n"
        "- Generated artifacts: never hand-edit.\n"
        "- This file, identity, license: do not change unless asked.\n"
        "- `Status: proposed` → `accepted`: a named human only. On GitHub, the PR needs the `human-accepted` label.\n"
        "- Do not delete an accepted or superseded decision; supersede it. A deletion PR needs the `human-removed` label.\n\n"
        "## Where to read\n\n"
        "| Need | File |\n"
        "|---|---|\n"
        + rows
        + "\n\n"
        "## After you finish\n\n"
        "Propose, do not silently apply: a docs/now.md patch, a decision draft if you chose something, "
        "a one-line history note if git will not explain it.\n"
    )


def init_kernel(
    root: Path,
    *,
    name: str | None = None,
    install: str | None = None,
    dev: str | None = None,
    test: str | None = None,
    lint_command: str | None = None,
    force: bool = False,
    compat: bool = True,
) -> LintResult:
    """Scaffold the Tier 1 kernel. Never creates empty rings."""
    root = root.resolve()
    result = LintResult()
    commands = infer_commands(root)
    if install:
        commands["install"] = install
    if dev:
        commands["dev"] = dev
    if test:
        commands["test"] = test
    if lint_command:
        commands["lint"] = lint_command
    if not commands:
        result.errors.append(
            "cannot infer install/test/lint; pass --install, --test, --dev, and/or --lint-command"
        )
        return result

    title = name or root.name or "project"
    readme = root / "README.md"
    if not readme.exists() or force:
        existed = readme.exists()
        readme.write_text(
            f"# {title}\n\nSee [AGENTS.md](AGENTS.md) for agent commands.\n",
            encoding="utf-8",
        )
        result.fixed.append(f"{'replaced' if existed else 'created'}: README.md")
    else:
        result.warnings.append("init skipped existing README.md")

    routes: list[tuple[str, str]] = []
    if (root / "README.md").is_file():
        routes.append(("What this is", "README.md"))
    routes.append(("How to operate", "AGENTS.md"))
    if (root / "docs" / "now.md").is_file():
        routes.append(("What we are doing now", "docs/now.md"))
    if (root / "docs" / "identity.md").is_file():
        routes.append(("Scope and non-goals", "docs/identity.md"))
    if (root / "docs" / "decisions").is_dir():
        routes.append(("Why a choice was made", "docs/decisions/"))

    agents = root / "AGENTS.md"
    body = render_agents(commands, routes)
    if agents.exists() and not force:
        result.warnings.append("init skipped existing AGENTS.md")
    else:
        existed = agents.exists()
        agents.write_text(body, encoding="utf-8")
        result.fixed.append(f"{'replaced' if existed else 'created'}: AGENTS.md")

    if compat:
        pointers = {
            root / "CLAUDE.md": "@AGENTS.md\n",
            root / "GEMINI.md": (
                "@AGENTS.md\n\nAll operational instructions live in AGENTS.md. Follow that file.\n"
            ),
            root / ".github" / "copilot-instructions.md": (
                "Refer to [AGENTS.md](../AGENTS.md) for all repository agent instructions. "
                "That file is the source of truth for commands, conventions, authority, and routing.\n"
            ),
        }
        for path, text in pointers.items():
            rel = path.relative_to(root).as_posix()
            if path.exists() and not force:
                result.warnings.append(f"init skipped existing {rel}")
                continue
            existed = path.exists()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            result.fixed.append(f"{'replaced' if existed else 'created'}: {rel}")

    src = Path(__file__).resolve()
    dest = (root / "scripts" / "lint_knowledge.py").resolve()
    if src != dest:
        if dest.exists() and not force:
            result.warnings.append("init skipped existing scripts/lint_knowledge.py")
        else:
            existed = dest.exists()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            result.fixed.append(
                f"{'replaced' if existed else 'created'}: scripts/lint_knowledge.py"
            )

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


def merge_results(first: LintResult, second: LintResult) -> LintResult:
    return LintResult(
        errors=first.errors + second.errors,
        warnings=first.warnings + second.warnings,
        fixed=first.fixed + second.fixed,
    )


def emit_version(fmt: str) -> int:
    if fmt == "json":
        print(json.dumps({"version": VERSION, "pin": PIN_URL}, indent=2))
    else:
        print(VERSION)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: parent of scripts/)")
    parser.add_argument("--stale-days", type=int, default=14)
    parser.add_argument("--strict", action="store_true", help="treat warnings (including stale now.md) as errors")
    parser.add_argument("--fix", action="store_true", help="refresh docs/now.md updated: to today")
    parser.add_argument("--version", action="store_true", help="print the embedded linter version and exit")
    parser.add_argument(
        "--promotion-diff",
        metavar="FILE",
        default=None,
        help="unified diff to scan for promotions and protected deletions (use - for stdin)",
    )
    parser.add_argument(
        "--promotion-base",
        metavar="GIT_REV",
        default=None,
        help="git rev to diff against (decision files only are considered)",
    )
    parser.add_argument(
        "--allow-promotion",
        action="store_true",
        help="with --promotion-*: do not fail on landing Status: accepted (human-accepted label)",
    )
    parser.add_argument(
        "--allow-deletion",
        action="store_true",
        help="with --promotion-*: do not fail on deleting an accepted/superseded decision (human-removed label)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="scaffold Tier 1 (AGENTS.md + pointers). Does not create empty docs/ rings",
    )
    parser.add_argument("--name", default=None, help="with --init: project title for a missing README")
    parser.add_argument("--install", default=None, help="with --init: install command")
    parser.add_argument("--dev", default=None, help="with --init: dev command")
    parser.add_argument("--test", default=None, help="with --init: test command")
    parser.add_argument("--lint-command", default=None, help="with --init: lint/format command")
    parser.add_argument("--force", action="store_true", help="with --init: overwrite existing kernel files")
    parser.add_argument("--no-compat", action="store_true", help="with --init: skip CLAUDE/GEMINI/Copilot pointers")
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
    if args.version:
        return emit_version(args.format)
    root = args.root.resolve() if args.root else repo_root()
    if args.promotion_diff is not None or args.promotion_base:
        try:
            if args.promotion_base:
                diff_text = git_decision_diff(root, args.promotion_base)
            elif args.promotion_diff == "-":
                diff_text = sys.stdin.read()
            else:
                diff_text = Path(args.promotion_diff).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, RuntimeError) as exc:
            failed = LintResult(errors=[str(exc)])
            return emit(failed, args.format)
        events = gate_events_in_diff(diff_text)
        result = LintResult()
        promo = [e.message for e in events if e.kind == "promotion"]
        dele = [e.message for e in events if e.kind == "deletion"]
        if promo and args.allow_promotion:
            result.warnings.extend(promo)
            result.fixed.append("promotion allowed by --allow-promotion")
        elif promo:
            result.errors.extend(promo)
        if dele and args.allow_deletion:
            result.warnings.extend(dele)
            result.fixed.append("deletion allowed by --allow-deletion")
        elif dele:
            result.errors.extend(dele)
        return emit(result, args.format)
    result = LintResult()
    if args.init:
        result = init_kernel(
            root,
            name=args.name,
            install=args.install,
            dev=args.dev,
            test=args.test,
            lint_command=args.lint_command,
            force=args.force,
            compat=not args.no_compat,
        )
        if not result.ok:
            return emit(result, args.format)
    linted = lint(root, args.stale_days, args.strict, args.fix)
    if args.init:
        linted = merge_results(result, linted)
    return emit(linted, args.format)


if __name__ == "__main__":
    sys.exit(main())
