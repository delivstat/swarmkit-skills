#!/usr/bin/env python3
"""Paste every bundle into a real SwarmKit runtime and make it prove itself.

The liveness check answers one question — *does the tool still exist?* — and it is not the question
a reader is actually asking. They want to know that the block they are about to copy is valid
config, that the tool works when called, and that the `effects` map is doing something rather than
decorating the file. None of that is testable by listing tools.

So this check imports the real `swarmkit-runtime` and asks it, in three escalating steps:

1. **Schema.** Every skill file and the assembled workspace validate against the published
   `swarmkit-schema`. Catches a paste that SwarmKit cannot parse at all.
2. **Governance.** For every bundle, force `permission: readonly` and assert through the runtime's
   own gate that read-effect tools are allowed and write-effect tools are denied. This is the
   catalogue's central claim — that `readonly` means something because the effects are declared —
   and until now nothing tested it.
3. **Invocation, and the server's own opinion.** For bundles that declare `check.invoke`, actually
   call the tool through `governed_mcp_call` and assert something about what came back — *exists*
   and *works* are different claims, and a tool whose arguments were renamed still exists. While
   the server is up, compare every declared effect against its `readOnlyHint`. That comparison is
   the only one here that can catch a *wrong* declaration rather than an inconsistent one: step 2
   compares the bundle against itself, so `write_file: read` would sail through it.

Step 3 runs only for bundles that opt in, because the catalogue includes browsers and language
servers that are slow, and credentialed servers that cannot run here at all. A bundle with no
`check.invoke` is honestly weaker-tested, and the summary says so rather than implying otherwise.

    python3 scripts/check_contract.py [bundle]
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
AGENT = "contract-check"


def _fail(problems: list[str], msg: str) -> None:
    problems.append(msg)


# ---------------------------------------------------------------- 1. schema


def _schema_dir() -> Path:
    import swarmkit_schema

    base = Path(swarmkit_schema.__file__).parent
    for candidate in ("_schemas", "schemas"):
        if (base / candidate).is_dir():
            return base / candidate
    raise RuntimeError("swarmkit-schema is installed but ships no schemas directory")


def check_schema(bundles: list[Path], problems: list[str]) -> None:
    import jsonschema

    sdir = _schema_dir()
    skill_schema = json.loads((sdir / "skill.schema.json").read_text())
    for path in bundles:
        name = path.parent.name
        for sk in sorted((path.parent / "skills").glob("*.yaml")):
            doc = yaml.safe_load(sk.read_text())
            try:
                jsonschema.validate(doc, skill_schema)
            except jsonschema.ValidationError as exc:
                _fail(problems, f"{name}/{sk.stem}: not a valid Skill — {exc.message}")


def check_workspace_loads(problems: list[str]) -> None:
    """The example workspace is a real workspace, loaded by the real runtime.

    `reachability()` is the interesting half: it compiles every topology with a wiring ledger and
    reports configuration no code path consumes. A bundle whose server block the runtime accepts
    but never wires would pass every other check in this repo and do nothing at run time.
    """
    ws = ROOT / "examples" / "repo-report"
    if not (ws / "workspace.yaml").exists():
        _fail(problems, "examples/repo-report/workspace.yaml is missing")
        return
    from swarmkit_runtime._workspace_runtime import WorkspaceRuntime

    try:
        runtime = WorkspaceRuntime.from_workspace_path(ws)
    except Exception as exc:  # noqa: BLE001
        _fail(problems, f"example workspace does not load: {type(exc).__name__}: {exc}")
        return
    try:
        report = runtime.reachability()
    except Exception as exc:  # noqa: BLE001
        _fail(problems, f"example workspace: reachability failed: {type(exc).__name__}: {exc}")
        return
    unreached = [d for d in getattr(report, "unreached", []) or []]
    if unreached:
        shown = ", ".join(str(getattr(d, "what", d)) for d in unreached[:4])
        _fail(problems, f"example workspace declares config nothing reaches: {shown}")


# ------------------------------------------------------- 2. governance gate


async def _tier_verdict(cfg: Any, server_id: str, tool: str) -> tuple[bool, str]:
    from swarmkit_runtime.governance._mock import MockGovernanceProvider
    from swarmkit_runtime.mcp._client import MCPClientManager
    from swarmkit_runtime.mcp._governed import check_mcp_permission

    manager = MCPClientManager({server_id: cfg})
    # The agent HOLDS both scopes, so a scope refusal cannot be mistaken for a tier refusal: the
    # only thing left that can deny is the readonly tier consulting the declared effect, which is
    # the single claim under test.
    return await check_mcp_permission(
        manager,
        MockGovernanceProvider(allowed_scopes=frozenset({"workspace:read", "workspace:write"})),
        agent_id=AGENT,
        server_id=server_id,
        tool_name=tool,
        scopes=frozenset({"workspace:read", "workspace:write"}),
    )


def _config_for(bundle: dict, *, permission: str | None = None) -> Any:
    """Build the runtime's own config object from the bundle's published block.

    Deliberately routed through `parse_mcp_servers` and the workspace model rather than
    constructing MCPServerConfig directly: the thing under test is the YAML a reader copies, so
    anything that skips the parser would test a different artifact.
    """
    from swarmkit_schema.models.workspace import McpServer

    from swarmkit_runtime.mcp._client import parse_mcp_servers

    raw = dict(bundle["server"])
    if permission:
        raw["permission"] = permission
    server = McpServer.model_validate(raw)
    return parse_mcp_servers([server])[raw["id"]]


async def check_governance(bundles: list[Path], problems: list[str]) -> int:
    """Under `permission: readonly`, reads are allowed and writes are denied. For every bundle."""
    checked = 0
    for path in bundles:
        name = path.parent.name
        bundle = yaml.safe_load(path.read_text())
        try:
            cfg = _config_for(bundle, permission="readonly")
        except Exception as exc:  # noqa: BLE001
            _fail(problems, f"{name}: runtime cannot parse the published server block — {exc}")
            continue
        for tool, effect in (bundle["server"].get("effects") or {}).items():
            allowed, reason = await _tier_verdict(cfg, name, tool)
            checked += 1
            if effect == "read" and not allowed:
                _fail(problems, f"{name}/{tool}: declared read but readonly denied it — {reason}")
            if effect == "write" and allowed:
                _fail(
                    problems,
                    f"{name}/{tool}: declared write but readonly ALLOWED it. The effects map is "
                    f"not reaching the gate, so `permission: readonly` on this bundle is decorative.",
                )
    return checked


# ---------------------------------------------------------- 3. invoke a tool


def _expand(args: dict, root: Path) -> dict:
    """`${ROOT}` in an argument becomes the checkout path.

    A bundle that hard-codes one machine's absolute path passes on that machine and fails in CI,
    which is the worst of both: green where nobody is watching, red where everybody is.
    """
    return {k: v.replace("${ROOT}", str(root)) if isinstance(v, str) else v for k, v in args.items()}


def _text_of(result: Any) -> str:
    """Same extraction the skill executor does: text blocks first, structuredContent as fallback.

    Reading it differently here would test a different thing from what an agent receives — a tool
    that returns only structured content reads as empty to a naive `.text`, and this check would
    then fail a bundle that works.
    """
    parts = [t for b in (getattr(result, "content", None) or []) if (t := getattr(b, "text", None))]
    if parts:
        return "\n".join(parts)
    structured = getattr(result, "structuredContent", None)
    return json.dumps(structured) if structured else ""


async def _exercise(bundle: dict, spec: dict, root: Path) -> tuple[bool, str, list[str]]:
    """Start the server once, then do both things that need it running.

    **The hint cross-check is the one that catches a lie.** Everything else in this file compares
    the bundle against itself: declare `write_file: read` and the gate dutifully allows it, because
    the gate's whole job is to believe the declaration. The server's own `readOnlyHint` is the only
    independent opinion available, and five of six servers here publish one.

    The runtime deliberately prefers the declared effect over the hint at run time — the operator
    controls the declaration, and a server upgrade must not silently change what an agent may do.
    That is right for a workspace and wrong for a catalogue, where we author both sides: here a
    disagreement means we wrote the effects map incorrectly, so it fails.
    """
    from swarmkit_runtime.mcp._client import MCPClientManager
    from swarmkit_runtime.mcp._governed import governed_mcp_call

    name = bundle["metadata"]["id"]
    declared = (bundle["server"].get("effects") or {})
    cfg = _config_for(bundle)
    manager = MCPClientManager({name: cfg}, workspace_root=root)
    disagreements: list[str] = []
    try:
        await manager.start_all()

        hints = manager._tool_read_only.get(name, {})  # noqa: SLF001
        for tool, effect in declared.items():
            hint = hints.get(tool)
            if hint is None:
                continue
            says = "read" if hint else "write"
            if says != effect:
                disagreements.append(
                    f"{name}/{tool}: bundle declares {effect!r} but the server's readOnlyHint "
                    f"says {says!r}. The catalogue authors both; one of them is wrong."
                )

        if not spec:
            return True, "", disagreements

        response = await governed_mcp_call(
            manager,
            None,
            agent_id=AGENT,
            server_id=name,
            tool_name=spec["tool"],
            arguments=_expand(spec.get("args") or {}, root),
            skill_id=f"{name}-contract",
        )
    finally:
        with __import__("contextlib").suppress(Exception):
            await manager.close_all()

    text = _text_of(response.data)
    if getattr(response.data, "isError", False):
        return False, f"server returned an error: {text[:160]}", disagreements
    want = spec.get("expect")
    if want and want not in text:
        return False, f"response did not contain {want!r}; got {text[:160]!r}", disagreements
    return True, f"{len(text)} chars", disagreements


async def check_invocations(bundles: list[Path], problems: list[str]) -> tuple[int, int]:
    import os

    invoked = skipped = 0
    for path in bundles:
        name = path.parent.name
        bundle = yaml.safe_load(path.read_text())
        spec = (bundle.get("check") or {}).get("invoke")
        if not spec:
            skipped += 1
            continue
        for key, value in ((bundle.get("check") or {}).get("env") or {}).items():
            os.environ.setdefault(key, str(ROOT if value == "." else value))
        try:
            ok, detail, disagreements = await asyncio.wait_for(
                _exercise(bundle, spec, ROOT), timeout=240
            )
        except Exception as exc:  # noqa: BLE001
            ok, detail, disagreements = False, f"{type(exc).__name__}: {exc}"[:200], []
        mark = "✅" if ok and not disagreements else "❌"
        print(f"  {mark} {name:22} {spec['tool']} — {detail}")
        invoked += 1
        for d in disagreements:
            print(f"     ↳ {d}")
            _fail(problems, d)
        if not ok:
            _fail(problems, f"{name}: calling {spec['tool']} failed — {detail}")
    return invoked, skipped


# ----------------------------------------------------------------- assembly


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bundles = sorted(ROOT.glob("skills/*/bundle.yaml"))
    if args:
        bundles = [p for p in bundles if p.parent.name == args[0]]
    if not bundles:
        print("no bundles matched")
        return 1

    problems: list[str] = []

    print("1. schema — every skill is a valid Skill; the example workspace loads")
    check_schema(bundles, problems)
    if not args:
        check_workspace_loads(problems)
    print(f"   {len(bundles)} bundle(s) checked\n")

    print("2. governance — under `readonly`, reads pass and writes are denied")
    verdicts = asyncio.run(check_governance(bundles, problems))
    print(f"   {verdicts} tool verdict(s) from the runtime's own gate\n")

    print("3. invocation — the tool is called, and the server's readOnlyHint is cross-checked")
    invoked, skipped = asyncio.run(check_invocations(bundles, problems))
    print(f"   {invoked} invoked · {skipped} bundle(s) declare no `check.invoke`\n")

    if problems:
        print("FAIL")
        for p in problems:
            print(f"  {p}")
        return 1
    print("OK — every bundle parses, governs and (where declared) answers a real call.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
