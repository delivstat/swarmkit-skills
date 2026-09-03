#!/usr/bin/env python3
"""Every bundle and skill is well-formed, and says what a reader needs.

Structure only — this runs on every push. Whether the servers still answer is the nightly liveness
check's job, because a third-party outage must never block a merge.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EFFECTS = {"read", "write"}


def main() -> int:
    problems: list[str] = []
    bundles = sorted(ROOT.glob("skills/*/bundle.yaml"))
    if not bundles:
        print("no bundles found — the glob is wrong or the repo is empty")
        return 1

    for path in bundles:
        name = path.parent.name
        b = yaml.safe_load(path.read_text())
        server = b.get("server") or {}
        declared = set(b.get("skills") or [])
        files = {p.stem for p in (path.parent / "skills").glob("*.yaml")}

        if b.get("metadata", {}).get("id") != name:
            problems.append(f"{name}: metadata.id must match the directory")
        if not (b.get("metadata", {}).get("description") or "").strip():
            problems.append(f"{name}: no description — the index would show a blank row")
        if not b.get("requires_runtime"):
            problems.append(f"{name}: no requires_runtime floor; a skill that outgrows a runtime "
                            f"must fail at load, not at call time")
        if not (path.parent / "README.md").exists():
            problems.append(f"{name}: no README — 'what, how and why' is the point of the catalogue")
        if declared != files:
            problems.append(f"{name}: bundle.skills {sorted(declared)} != files {sorted(files)}")

        effects = server.get("effects") or {}
        for p in sorted((path.parent / "skills").glob("*.yaml")):
            s = yaml.safe_load(p.read_text())
            tool = (s.get("implementation") or {}).get("tool")
            if (s.get("implementation") or {}).get("server") != name:
                problems.append(f"{name}/{p.stem}: implementation.server must be {name!r}")
            if tool not in effects:
                problems.append(f"{name}/{p.stem}: tool {tool!r} has no entry in server.effects — "
                                f"`permission: readonly` cannot be enforced against a guess")
            elif effects[tool] not in EFFECTS:
                problems.append(f"{name}/{p.stem}: effects must be read or write")
            if not ((s.get("iam") or {}).get("required_scopes")):
                problems.append(f"{name}/{p.stem}: no iam.required_scopes — scopes are what authorize")
            if not (s.get("provenance") or {}).get("requires_runtime"):
                problems.append(f"{name}/{p.stem}: no provenance.requires_runtime")

    print(f"checked {len(bundles)} bundle(s)")
    if problems:
        print("\nFAIL")
        for p in problems:
            print(f"  {p}")
        return 1
    print("OK — every bundle declares effects, scopes, a floor and a README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
