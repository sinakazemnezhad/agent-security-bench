from __future__ import annotations

import ast
import re
from typing import Any


def _parse(text: str) -> ast.AST | None:
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def _call_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
                # also dotted form when base is Name
                if isinstance(func.value, ast.Name):
                    names.add(f"{func.value.id}.{func.attr}")
    return names


def _name_ids(tree: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}


def _attr_chains(tree: ast.AST) -> set[str]:
    chains: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.AST = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
                chains.add(".".join(reversed(parts)))
    return chains


def run_check(check: dict[str, Any], text: str) -> tuple[bool, str]:
    """Return (passed, detail). Deterministic only."""
    ctype = check["type"]

    if ctype == "contains":
        ok = check["pattern"] in text
        return ok, f"contains:{check['pattern']!r}={ok}"

    if ctype == "not_contains":
        ok = check["pattern"] not in text
        return ok, f"not_contains:{check['pattern']!r}={ok}"

    if ctype == "contains_any":
        patterns = check["patterns"]
        hit = next((p for p in patterns if p in text), None)
        return hit is not None, f"contains_any:hit={hit!r}"

    if ctype == "regex":
        flags = re.MULTILINE
        if check.get("ignore_case"):
            flags |= re.IGNORECASE
        m = re.search(check["pattern"], text, flags=flags)
        return m is not None, f"regex:matched={bool(m)}"

    if ctype == "python_parses":
        tree = _parse(text)
        return tree is not None, "python_parses:ok" if tree else "python_parses:syntax_error"

    if ctype == "ast_has_call":
        tree = _parse(text)
        if tree is None:
            return False, "ast_has_call:syntax_error"
        names = _call_names(tree) | _attr_chains(tree)
        wanted = set(check.get("names") or ([check["name"]] if "name" in check else []))
        hit = sorted(names & wanted)
        return bool(hit), f"ast_has_call:hit={hit}"

    if ctype == "ast_lacks_call":
        tree = _parse(text)
        if tree is None:
            return False, "ast_lacks_call:syntax_error"
        names = _call_names(tree) | _attr_chains(tree)
        forbidden = set(check.get("names") or ([check["name"]] if "name" in check else []))
        hit = sorted(names & forbidden)
        return not hit, f"ast_lacks_call:hit={hit}"

    if ctype == "ast_has_name":
        tree = _parse(text)
        if tree is None:
            return False, "ast_has_name:syntax_error"
        ids = _name_ids(tree)
        wanted = set(check.get("names") or ([check["name"]] if "name" in check else []))
        hit = sorted(ids & wanted)
        return bool(hit), f"ast_has_name:hit={hit}"

    if ctype == "ast_assign_name":
        tree = _parse(text)
        if tree is None:
            return False, "ast_assign_name:syntax_error"
        targets: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        targets.add(t.id)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets.add(node.target.id)
        name = check["name"]
        ok = name in targets
        return ok, f"ast_assign_name:{name}={ok}"

    if ctype == "line_count_max":
        n = len(text.splitlines())
        lim = int(check["max"])
        ok = n <= lim
        return ok, f"line_count:{n}<={lim}"

    return False, f"unknown_check_type:{ctype}"
