"""Validate targets of inline repository-local Markdown links without network access.

External destinations, reference-style links and fragment-anchor correctness
are intentionally outside this check's scope.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

_INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)")
_EXTERNAL_SCHEMES = frozenset({"http", "https", "mailto", "data"})


def broken_local_links(source: str, document: Path, repo_root: Path) -> list[str]:
    """Return missing, unsafe, or escaping local targets in inline links."""
    document = document.resolve()
    root = repo_root.resolve()
    problems: list[str] = []
    for matched in _INLINE_LINK.finditer(source):
        target = matched.group(1).strip("<>")
        if target.startswith("#"):
            continue
        parsed = urlsplit(target)
        if parsed.scheme.lower() in _EXTERNAL_SCHEMES or parsed.netloc:
            continue
        if parsed.scheme or parsed.path.startswith("/"):
            problems.append(f"unsupported absolute/local URI: {target}")
            continue
        pathname = unquote(parsed.path)
        if not pathname:
            continue
        resolved = (document.parent / pathname).resolve()
        if not resolved.is_relative_to(root):
            problems.append(f"link escapes repository: {target}")
        elif not resolved.exists():
            problems.append(f"missing local target: {target}")
    return problems


def main() -> int:
    markdown = Path(sys.argv[1] if len(sys.argv) > 1 else "README.md")
    if not markdown.is_file():
        print(f"Missing Markdown file: {markdown}", file=sys.stderr)
        return 1
    findings = broken_local_links(markdown.read_text(encoding="utf-8"), markdown, Path.cwd())
    for issue in findings:
        print(issue, file=sys.stderr)
    if findings:
        print(f"README local-link integrity: {len(findings)} issue(s)", file=sys.stderr)
        return 1
    print("README local-link integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
