# Adding a bundle

A bundle is one MCP server plus the skills that use it. The value is not the list — it is that
somebody already worked out the config, the tier, the effects and the scopes, and that a machine
re-checks it nightly.

## Shape

```
skills/<id>/
├── bundle.yaml        the mcp_servers block, the skill ids, the runtime floor
├── README.md          what each skill does, why you would want it, when to grant it
└── skills/*.yaml      one SwarmKit skill per tool you are exposing
```

## The rules, and why each exists

**Declare `effects` for every tool.** Nothing about a binary reveals whether it writes — `curl`
POSTs, `jq` and `sed` both take `-i`. Undeclared means `write`, so an unclassified tool fails closed
and `permission: readonly` is enforceable against a fact rather than a guess about the tool's name.

**Carry a `requires_runtime` floor.** A skill is portable data that outlives the runtime that
installed it. Without a floor it resolves cleanly into an older workspace and fails much later with
an error naming nothing.

**Give every skill `iam.required_scopes`.** Scopes are what authorize; the permission tier only
decides whether governance is consulted at all.

**Write the README for someone who has not decided yet.** Three questions per skill: what it does,
why you would want it, when to grant it. "Wraps the X API" answers none of them.

**Do not expose every tool a server has.** GitHub's exposes fifty-one. A bundle with fifty-one
skills is not useful to an agent — picking the six that matter is the work.

## Before opening a PR

```bash
python3 scripts/check_bundles.py       # structure, effects, scopes, floors
python3 scripts/check_liveness.py <id> # does the server actually answer?
python3 scripts/build_readme.py        # regenerate the index; never hand-edit README.md
```

If your server needs a credential, say so — add `credentials_ref` and it will report as
`unverifiable` rather than passing silently. That is an honest state, not a lesser one. A green tick
meaning *we did not look* is worth less than no tick.

If it needs a fixture to answer at all, declare it:

```yaml
check:
  env: { SWARMKIT_GIT_REPO: "." }
  note: needs a path to a real git repository
```

## When a bundle breaks

The nightly check marks it `broken`, records why, and files an issue — it does not quietly remove
the entry. Someone who already copied a broken bundle learns nothing from its disappearance.

The issue is the interface to whoever fixes it, and "whoever" can be a swarm: a broken bundle is a
well-specified task with a machine-checkable acceptance test, which is `scripts/check_liveness.py`
passing.
