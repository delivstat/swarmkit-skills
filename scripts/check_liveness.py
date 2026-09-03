#!/usr/bin/env python3
"""Start every bundle's server and ask whether the tools its skills name still exist.

This is the whole reason the catalogue is worth having. Anyone can list MCP servers; the claim here
is that each entry **was started and asked**, on a date. Without this the repo is an awesome-list,
and those rot in months.

    python3 scripts/check_liveness.py [bundle]   # one, or all
    python3 scripts/check_liveness.py --write    # record the result into each bundle.yaml

Three states. `verified` and `broken` are what you expect. `unverifiable` means the server needs a
credential this environment does not have — reported honestly rather than passed silently, because
a green tick meaning "we did not look" is worth less than no tick.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT_S = float(os.environ.get("LIVENESS_TIMEOUT", "150"))
_ENV_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class Outcome:
    bundle: str
    state: str
    detail: str = ""
    tools_seen: int = 0


def _blocked(server: dict) -> str:
    """Why this server cannot be checked here, or "" if it can."""
    if server.get("credentials_ref"):
        return f"needs credential '{server['credentials_ref']}'"
    for key, raw in (server.get("env") or {}).items():
        for var in _ENV_VAR.findall(str(raw)):
            if not os.environ.get(var):
                return f"needs ${var} (for {key})"
    return ""


def _argv_with(server: dict, env: dict[str, str]) -> list[str]:
    """Command with ${VAR} expanded. An unset var becomes a temp path rather than an empty string:
    a server handed "" as its root fails for a reason unrelated to whether its tools exist."""
    return [
        _ENV_VAR.sub(lambda m: env.get(m.group(1)) or "/tmp", str(part))
        for part in server.get("command", [])
    ]


async def _check(path: Path) -> Outcome:
    bundle = yaml.safe_load(path.read_text())
    name = path.parent.name
    server = bundle.get("server") or {}
    wanted = {
        yaml.safe_load(p.read_text())["implementation"]["tool"]
        for p in (path.parent / "skills").glob("*.yaml")
    }

    why = _blocked(server)
    if why:
        return Outcome(name, "unverifiable", why)

    # A bundle may declare what verifying it needs — git wants a repository, and a server that
    # fails for want of a fixture is not a broken server. Declared values never override an env
    # var already set, so CI and a laptop can each point it somewhere sensible.
    env = {**os.environ}
    for key, value in ((bundle.get("check") or {}).get("env") or {}).items():
        env.setdefault(key, str(ROOT if value == "." else value))

    argv = _argv_with(server, env)
    params = StdioServerParameters(command=argv[0], args=argv[1:], env=env)
    try:
        async with contextlib.AsyncExitStack() as stack:
            transport = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(*transport))
            await asyncio.wait_for(session.initialize(), timeout=TIMEOUT_S)
            listed = await asyncio.wait_for(session.list_tools(), timeout=TIMEOUT_S)
            names = {t.name for t in listed.tools}
    except TimeoutError:
        return Outcome(name, "broken", f"did not answer within {TIMEOUT_S:.0f}s")
    except Exception as exc:
        return Outcome(name, "broken", f"{type(exc).__name__}: {exc}"[:160])

    missing = sorted(wanted - names)
    if missing:
        near = ", ".join(sorted(names)[:5])
        return Outcome(name, "broken", f"tools not listed: {missing}; server offers: {near}…", len(names))
    return Outcome(name, "verified", f"{len(wanted)} tool(s) present", len(names))


async def run(only: str | None) -> list[Outcome]:
    paths = sorted(ROOT.glob("skills/*/bundle.yaml"))
    if only:
        paths = [p for p in paths if p.parent.name == only]
    return [await _check(p) for p in paths]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outcomes = asyncio.run(run(args[0] if args else None))
    today = datetime.now(UTC).strftime("%Y-%m-%d")

    mark = {"verified": "✅", "unverifiable": "🔑", "broken": "❌"}
    print(f"liveness — {today}\n")
    for o in outcomes:
        print(f"  {mark[o.state]} {o.bundle:22} {o.detail}")
    counts = {s: sum(1 for o in outcomes if o.state == s) for s in mark}
    print(f"\n{counts['verified']} verified · {counts['broken']} broken · {counts['unverifiable']} unverifiable")

    if "--write" in sys.argv:
        for o in outcomes:
            p = ROOT / "skills" / o.bundle / "bundle.yaml"
            b = yaml.safe_load(p.read_text())
            b["verification"] = {"state": o.state, "checked_at": today, "detail": o.detail}
            p.write_text(yaml.safe_dump(b, sort_keys=False, width=100))
        print("recorded into each bundle.yaml — regenerate the README")

    # Only `broken` fails. Failing on `unverifiable` would make every credentialed entry
    # permanently red and teach everyone to ignore the check.
    return 1 if counts["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())
