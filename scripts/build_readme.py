#!/usr/bin/env python3
"""Generate README.md from the bundles. Never hand-edit the index.

An index maintained by hand is an index that drifts, and a catalogue whose index disagrees with its
contents is worse than one with no index — a reader trusts it exactly once. So the index is built
from the same YAML the runtime reads, and CI fails if the committed README is not what this
produces.

    python3 scripts/build_readme.py            # write
    python3 scripts/build_readme.py --check    # fail if stale
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

STATE_MARK = {"verified": "✅", "unverifiable": "🔑", "broken": "❌", "unverified": "⬜"}
STATE_WORD = {
    "verified": "the server started and every tool below was present, on the date shown",
    "unverifiable": "needs a credential public CI does not have — nobody has checked it for you",
    "broken": "a tool it names is gone; see the linked issue",
    "unverified": "not yet checked",
}


def _bundles() -> list[dict]:
    out = []
    for path in sorted(SKILLS.glob("*/bundle.yaml")):
        bundle = yaml.safe_load(path.read_text())
        bundle["_dir"] = path.parent.name
        bundle["_skills"] = [
            yaml.safe_load(p.read_text())
            for p in sorted((path.parent / "skills").glob("*.yaml"))
        ]
        out.append(bundle)
    return out


def render() -> str:
    bundles = _bundles()
    total_skills = sum(len(b["_skills"]) for b in bundles)
    lines: list[str] = []
    a = lines.append

    a("# SwarmKit skills")
    a("")
    a("Pre-wired MCP servers and the skills that use them, for [SwarmKit](https://github.com/delivstat/swarmkit).")
    a("")
    a("**The point is not the list — it is that each entry has been started and asked.** A curated list")
    a("nobody re-checks becomes an awesome-list, and those rot in months: a server renames a tool, changes")
    a("an argument, or disappears, and the entry keeps claiming it works. A nightly job starts every server")
    a("here and asks whether the tool each skill names still exists, so *verified* carries a date rather")
    a("than a promise.")
    a("")
    a(f"**{len(bundles)} bundles · {total_skills} skills.**")
    a("")
    a("## How an entry is checked")
    a("")
    a("Four questions, because *the tool exists* is the weakest of them and the easiest to mistake for")
    a("the others.")
    a("")
    a("| | question | when |")
    a("| --- | --- | --- |")
    a("| **liveness** | does the tool this skill names still exist? | nightly |")
    a("| **schema** | is every skill a valid SwarmKit Skill, and does the example workspace load? | per push |")
    a("| **governance** | under `permission: readonly`, does the runtime's own gate allow the reads and deny the writes? | per push |")
    a("| **invocation** | called for real, does the tool answer — and does the server's own `readOnlyHint` agree with the effects we declared? | per push |")
    a("")
    a("The last one matters most. Everything else compares a bundle against itself, so an effects map")
    a("that simply lies — `write_file: read` — passes them all; the gate's job is to believe the")
    a("declaration. The server's own hint is the one independent opinion available, and it is checked")
    a("against every declared effect on every server that publishes one.")
    a("")
    a("[`examples/repo-report/`](examples/repo-report/) is a runnable workspace assembled only from")
    a("bundle blocks, pasted unchanged. It is the showcase and the fixture: CI loads it with the real")
    a("runtime, so a block SwarmKit cannot parse fails here rather than in your terminal.")
    a("")
    a("## What you get for the paste")
    a("")
    a("The hard part of adopting an MCP server is never the server. It is the `mcp_servers` block with the")
    a("right command and env, a `permission` tier, an `effects` map so `readonly` means something, an")
    a("`iam.required_scopes` that is neither too broad nor missing, and the argument shape the tool actually")
    a("wants. Every entry here has that already written down and checked.")
    a("")
    a("## Index")
    a("")
    a("| | bundle | skills | needs | verified |")
    a("| --- | --- | --- | --- | --- |")
    for b in bundles:
        v = b.get("verification") or {}
        state = v.get("state", "unverified")
        checked = v.get("checked_at") or "—"
        a(
            f"| {STATE_MARK.get(state, '⬜')} | [{b['metadata']['name']}](skills/{b['_dir']}/) | "
            f"{len(b['_skills'])} | `{b.get('provenance', {}).get('upstream', '')}` | {checked} |"
        )
    a("")
    a("| mark | meaning |")
    a("| --- | --- |")
    for state, word in STATE_WORD.items():
        a(f"| {STATE_MARK[state]} | {word} |")
    a("")
    a("`🔑` is not a lesser badge for a worse entry — it is an honest one. Roughly three in five of the")
    a("most-wanted MCP servers need somebody's account, and a green tick that meant *we did not look*")
    a("would be worth less than no tick at all.")
    a("")
    a("## Using one")
    a("")
    a("Copy the `mcp_servers` entry from a bundle's page into your `workspace.yaml`, copy its skill files")
    a("into `skills/`, and grant them:")
    a("")
    a("```yaml")
    a("skills:")
    a("  - pack:git          # every READ skill in the bundle, now and later")
    a("  - fs-write-file     # a write, named — bulk grants never carry one")
    a("```")
    a("")
    a("A `pack:` grant carries reads only. Adding a read skill to a bundle reaches everyone holding it;")
    a("adding a write reaches nobody, so a bundle can never silently widen an agent that already has it.")
    a("")
    a("## The bundles")
    a("")
    for b in bundles:
        meta = b["metadata"]
        v = b.get("verification") or {}
        a(f"### {STATE_MARK.get(v.get('state', 'unverified'), '⬜')} [{meta['name']}](skills/{b['_dir']}/)")
        a("")
        a(meta.get("description", ""))
        a("")
        a(f"Needs swarmkit-runtime `{b.get('requires_runtime', '—')}` · upstream `{b.get('provenance', {}).get('upstream', '')}`")
        a("")
        a("| skill | tool | effects |")
        a("| --- | --- | --- |")
        effects = (b.get("server") or {}).get("effects") or {}
        for s in b["_skills"]:
            tool = s["implementation"]["tool"]
            a(f"| [`{s['metadata']['id']}`](skills/{b['_dir']}/README.md) | `{tool}` | {effects.get(tool, 'write')} |")
        a("")
    a("## Contributing")
    a("")
    a("See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: a bundle must declare `effects` for every")
    a("tool, carry a `requires_runtime` floor, and pass the liveness check — or say honestly why it cannot.")
    a("")
    a("<sub>This file is generated by `scripts/build_readme.py`. Edit the bundles, not this.</sub>")
    return "\n".join(lines) + "\n"


def main() -> int:
    body = render()
    target = ROOT / "README.md"
    if "--check" in sys.argv:
        current = target.read_text() if target.exists() else ""
        if current != body:
            print("README.md is stale — run `python3 scripts/build_readme.py` and commit the result.")
            return 1
        print("README.md is current.")
        return 0
    target.write_text(body)
    print(f"wrote README.md ({len(body.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
